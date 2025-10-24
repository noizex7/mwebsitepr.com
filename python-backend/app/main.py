import asyncio
import contextlib
import json
import logging
import os
import smtplib
import ssl
import sys
from asyncio.subprocess import Process
from email.message import EmailMessage
from pathlib import Path
from typing import Dict, Optional

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field

BASE_DIR = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = BASE_DIR / "scripts"
logger = logging.getLogger("mwebsite.backend")


def _load_scripts() -> Dict[str, Dict[str, str]]:
    scripts = {}
    for path in SCRIPTS_DIR.glob("*.py"):
        scripts[path.stem] = {
            "id": path.stem,
            "title": path.stem.replace("_", " ").title(),
            "path": path,
        }
    return scripts


SCRIPTS = _load_scripts()


class ScriptSummary(BaseModel):
    id: str
    title: str


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


CONTACT_EMAIL_TO = [
    email.strip()
    for email in os.getenv("CONTACT_EMAIL_TO", "").split(",")
    if email.strip()
]
EMAIL_SUBJECT_PREFIX = os.getenv("CONTACT_EMAIL_SUBJECT_PREFIX", "[Portfolio Contact]")
SMTP_HOST = os.getenv("SMTP_HOST", "").strip()
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "").strip()
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_USE_SSL = _env_bool("SMTP_USE_SSL", False)
SMTP_USE_TLS = _env_bool("SMTP_USE_TLS", not SMTP_USE_SSL)
CONTACT_EMAIL_FROM = os.getenv("CONTACT_EMAIL_FROM", "").strip()
if not CONTACT_EMAIL_FROM:
    if SMTP_USERNAME:
        CONTACT_EMAIL_FROM = SMTP_USERNAME
    elif CONTACT_EMAIL_TO:
        CONTACT_EMAIL_FROM = CONTACT_EMAIL_TO[0]
try:
    SMTP_PORT = int(
        os.getenv(
            "SMTP_PORT",
            "465" if SMTP_USE_SSL else "587" if SMTP_USE_TLS else "25",
        )
    )
except ValueError:
    SMTP_PORT = 465 if SMTP_USE_SSL else 587 if SMTP_USE_TLS else 25


class EmailConfigurationError(RuntimeError):
    """Raised when the email service is not fully configured."""


class ContactRequest(BaseModel):
    email: EmailStr
    name: str = Field(min_length=1, max_length=100)
    message: str = Field(min_length=1, max_length=4000)


def _validate_email_configuration() -> None:
    missing = []
    if not CONTACT_EMAIL_TO:
        missing.append("CONTACT_EMAIL_TO")
    if not CONTACT_EMAIL_FROM:
        missing.append("CONTACT_EMAIL_FROM")
    if not SMTP_HOST:
        missing.append("SMTP_HOST")
    if SMTP_USERNAME and not SMTP_PASSWORD:
        missing.append("SMTP_PASSWORD")
    if missing:
        raise EmailConfigurationError(
            f"Missing email configuration values: {', '.join(missing)}"
        )


def _send_contact_email(contact: ContactRequest) -> None:
    _validate_email_configuration()

    message = EmailMessage()
    subject_name = contact.name.strip() or "Unknown sender"
    message["Subject"] = f"{EMAIL_SUBJECT_PREFIX.strip()} - {subject_name}"
    message["From"] = CONTACT_EMAIL_FROM
    message["To"] = ", ".join(CONTACT_EMAIL_TO)
    message["Reply-To"] = contact.email

    body_lines = [
        f"Name: {contact.name}",
        f"Email: {contact.email}",
        "",
        "Message:",
        contact.message,
    ]
    message.set_content("\n".join(body_lines))

    context = ssl.create_default_context()
    try:
        if SMTP_USE_SSL:
            with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=context) as smtp:
                if SMTP_USERNAME:
                    smtp.login(SMTP_USERNAME, SMTP_PASSWORD)
                smtp.send_message(message)
        else:
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=20) as smtp:
                if SMTP_USE_TLS:
                    smtp.starttls(context=context)
                if SMTP_USERNAME:
                    smtp.login(SMTP_USERNAME, SMTP_PASSWORD)
                smtp.send_message(message)
    except EmailConfigurationError:
        raise
    except Exception as exc:
        logger.exception("Unable to send contact email")
        raise RuntimeError("Failed to send email") from exc


async def _send_contact_email_async(contact: ContactRequest) -> None:
    await asyncio.to_thread(_send_contact_email, contact)


app = FastAPI(title="Python Showcase Runner")

allowed_origins = os.getenv("ALLOWED_ORIGINS")
if allowed_origins:
    origins = [origin.strip() for origin in allowed_origins.split(",") if origin.strip()]
    if origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )


@app.get("/api/scripts", response_model=list[ScriptSummary])
async def list_scripts() -> list[ScriptSummary]:
    return [
        ScriptSummary(id=data["id"], title=data["title"])
        for data in SCRIPTS.values()
    ]


@app.post("/api/contact")
async def submit_contact(contact: ContactRequest) -> dict[str, str]:
    try:
        await _send_contact_email_async(contact)
    except EmailConfigurationError as exc:
        logger.warning("Contact form email configuration error: %s", exc)
        raise HTTPException(
            status_code=503, detail="Contact form email service is not configured."
        ) from exc
    except RuntimeError as exc:
        raise HTTPException(
            status_code=500, detail="Unable to send message at this time."
        ) from exc
    return {"status": "sent"}


class ScriptRunner:
    def __init__(self, script_id: str, websocket: WebSocket):
        self.script_id = script_id
        self.websocket = websocket
        self.process: Optional[Process] = None
        self.stdout_task: Optional[asyncio.Task] = None
        self.stderr_task: Optional[asyncio.Task] = None
        self._output_lock = asyncio.Lock()

    async def start(self) -> None:
        script = SCRIPTS.get(self.script_id)
        if not script:
            raise HTTPException(status_code=404, detail="Script not found")

        self.process = await asyncio.create_subprocess_exec(
            sys.executable,
            "-u",
            str(script["path"]),
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        self.stdout_task = asyncio.create_task(self._stream_output(self.process.stdout, "stdout"))
        self.stderr_task = asyncio.create_task(self._stream_output(self.process.stderr, "stderr"))
        await self.websocket.send_json(
            {"type": "status", "status": "started", "script": self.script_id}
        )

    async def _stream_output(self, stream: asyncio.StreamReader, channel: str) -> None:
        try:
            while True:
                data = await stream.read(1024)
                if not data:
                    break
                await self._send_output(channel, data.decode(errors="replace"))
        except Exception as exc:
            await self.websocket.send_json(
                {"type": "status", "status": "error", "message": str(exc)}
            )

    async def _send_output(self, channel: str, data: str) -> None:
        async with self._output_lock:
            await self.websocket.send_json({"type": "output", "stream": channel, "data": data})

    async def write(self, data: str) -> None:
        if not self.process or not self.process.stdin:
            raise RuntimeError("Process is not running")
        self.process.stdin.write(data.encode())
        await self.process.stdin.drain()

    async def terminate(self) -> None:
        if self.process and self.process.returncode is None:
            self.process.terminate()
            try:
                await asyncio.wait_for(self.process.wait(), timeout=5)
            except asyncio.TimeoutError:
                self.process.kill()
        await self._cleanup_tasks()

    async def _cleanup_tasks(self) -> None:
        for task in (self.stdout_task, self.stderr_task):
            if task:
                task.cancel()
                with contextlib.suppress(asyncio.CancelledError):
                    await task

    async def wait(self) -> None:
        if not self.process:
            return
        returncode = await self.process.wait()
        await self._cleanup_tasks()
        await self.websocket.send_json(
            {"type": "status", "status": "finished", "returncode": returncode}
        )


@app.websocket("/ws/run")
async def websocket_run(websocket: WebSocket) -> None:
    await websocket.accept()
    runner: Optional[ScriptRunner] = None
    wait_task: Optional[asyncio.Task] = None

    try:
        await websocket.send_json(
            {
                "type": "scripts",
                "scripts": [
                    {"id": data["id"], "title": data["title"]}
                    for data in SCRIPTS.values()
                ],
            }
        )
        while True:
            message = await websocket.receive_text()
            data = json.loads(message)
            action = data.get("action")

            if action == "start":
                if runner:
                    await websocket.send_json(
                        {"type": "status", "status": "error", "message": "Script already running"}
                    )
                    continue
                script_id = data.get("script")
                if not script_id:
                    await websocket.send_json(
                        {"type": "status", "status": "error", "message": "Missing script id"}
                    )
                    continue
                runner = ScriptRunner(script_id, websocket)
                try:
                    await runner.start()
                except HTTPException as exc:
                    await websocket.send_json(
                        {"type": "status", "status": "error", "message": exc.detail}
                    )
                    runner = None
                    continue
                wait_task = asyncio.create_task(runner.wait())

            elif action == "input":
                if not runner:
                    await websocket.send_json(
                        {"type": "status", "status": "error", "message": "No script running"}
                    )
                    continue
                text = data.get("data", "")
                await runner.write(text)

            elif action == "stop":
                if runner:
                    await runner.terminate()
                    runner = None
                    if wait_task:
                        wait_task.cancel()
                        with contextlib.suppress(asyncio.CancelledError):
                            await wait_task
                    await websocket.send_json(
                        {"type": "status", "status": "stopped"}
                    )

            else:
                await websocket.send_json(
                    {"type": "status", "status": "error", "message": "Unknown action"}
                )

            if wait_task and wait_task.done():
                runner = None
                wait_task = None
    except WebSocketDisconnect:
        pass
    finally:
        if runner:
            await runner.terminate()
        if wait_task:
            wait_task.cancel()
