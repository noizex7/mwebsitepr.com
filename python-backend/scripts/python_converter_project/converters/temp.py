_ERROR_MESSAGE = "Unit not supported"
_RANGE_ERROR_MESSAGE = "Temperature out of range physically possible"

def c_to_f(c): return c * 9/5 + 32
def f_to_c(f): return (f-32) * 5/9
def c_to_k(c): return c + 273.15
def k_to_c(k): return k - 273.15

def convert_temp(value: float, from_u: str, to_u: str) -> float:
    if from_u == "K" and value < 0:
        raise ValueError(_RANGE_ERROR_MESSAGE)
    if from_u == "C" and value < -273.15:
        raise ValueError(_RANGE_ERROR_MESSAGE)
    if from_u == "F" and value < -459.67:
        raise ValueError(_RANGE_ERROR_MESSAGE)

    if from_u == to_u: return value
    if from_u == "C": c = value
    elif from_u == "F": c = f_to_c(value)
    elif from_u == "K": c = k_to_c(value)
    else: raise ValueError(_ERROR_MESSAGE)

    if to_u == "C": return c
    if to_u == "F": return c_to_f(c)
    if to_u == "K": return c_to_k(c)
    raise ValueError(_ERROR_MESSAGE)
