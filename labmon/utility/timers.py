import sys
import ctypes
from contextlib import contextmanager


@contextmanager
def enable_high_res_timer():
    """
    Enable high resolution timers on windows
    """
    winmm = None
    if sys.platform.startswith("win32"):
        # Load WinMM.dll
        winmm = ctypes.WinDLL("winmm")
        # Enable high-resolution timer (1 ms)
        winmm.timeBeginPeriod(1)

    try:
        yield True
    finally:
        if winmm is not None:
            winmm.timeEndPeriod(1)
