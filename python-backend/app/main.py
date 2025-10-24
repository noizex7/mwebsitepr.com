import asyncio
import contextlib
import json
import os
import sys
from asyncio.subprocess import Process
from pathlib import Path
from typing import Dict, Optional

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = BASE_DIR / "scripts"


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
