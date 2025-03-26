import _thread
import platform
import signal
import threading
from contextlib import contextmanager


@contextmanager
def timeout(seconds: int) -> None:
    if platform.system() == 'Linux':
        def _handle_timeout(signum: int, frame: signal.FrameType) -> None:
            raise TimeoutError(f"Code block timed out after {seconds} seconds")

        signal.signal(signal.SIGALRM, _handle_timeout)
        signal.alarm(seconds)

        try:
            yield
        finally:
            signal.alarm(0)

    else:
        def timeout_handler() -> None:
            nonlocal timed_out
            timed_out = True
            _thread.interrupt_main()

        timed_out: bool = False
        timer = threading.Timer(seconds, timeout_handler)
        timer.start()

        try:
            yield
            if timed_out:
                raise TimeoutError(f"Code block timed out after {seconds} seconds")
        finally:
            timer.cancel()
