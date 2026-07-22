"""
A synchronous wrapper around the async client, for scripts and
interactive (REPL) use where asyncio would just be in the way.
"""

from __future__ import annotations

import asyncio
import atexit
import threading

from . import robot as _robot


class _LoopThread:
    """
    A singleton asyncio event loop running in a daemon thread.
    """

    _instance: _LoopThread | None = None
    _lock = threading.Lock()

    def __init__(self) -> None:
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(
            target=self.loop.run_forever, name="pymecca-ble", daemon=True
        )
        self.thread.start()

    @classmethod
    def get(cls) -> _LoopThread:
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls()
                atexit.register(cls._instance._shutdown)
            return cls._instance

    def run(self, coro):
        return asyncio.run_coroutine_threadsafe(coro, self.loop).result()

    def _shutdown(self) -> None:
        self.loop.call_soon_threadsafe(self.loop.stop)
        self.thread.join(timeout=2)


def discover(timeout: float = 10.0, name_filter: str = "mecc"):
    """
    Blocking version of :func:`pymecca.robot.discover`.
    """
    return _LoopThread.get().run(_robot.discover(timeout, name_filter))


class Meccanoid:
    """
    Blocking version of :class:`pymecca.robot.Meccanoid`. Same API,
    minus the ``await``::

        from pymecca.sync import Meccanoid

        with Meccanoid("C4:BE:84:D4:68:1B") as bot:
            bot.eye_lights(7, 0, 0)
            bot.drive(100, 100)
            time.sleep(1)
            bot.stop()
    """

    def __init__(
        self,
        address,
        *,
        write_char: str | int | None = None,
        wake_on_connect: bool = True,
    ) -> None:
        self._runner = _LoopThread.get()
        self._robot = _robot.Meccanoid(
            address, write_char=write_char, wake_on_connect=wake_on_connect
        )

    @property
    def is_connected(self) -> bool:
        return self._robot.is_connected

    def connect(self, timeout: float = 20.0) -> None:
        self._runner.run(self._robot.connect(timeout))

    def disconnect(self) -> None:
        self._runner.run(self._robot.disconnect())

    def __enter__(self) -> Meccanoid:
        self.connect()
        return self

    def __exit__(self, *exc) -> None:
        self.disconnect()

    def send_raw(self, frame: bytes) -> None:
        self._runner.run(self._robot.send_raw(frame))

    def drive(self, left_speed: int = 0, right_speed: int = 0) -> None:
        self._runner.run(self._robot.drive(left_speed, right_speed))

    def stop(self) -> None:
        self._runner.run(self._robot.stop())

    def servo(self, servo: int, value: int) -> None:
        self._runner.run(self._robot.servo(servo, value))

    def servo_light(self, servo: int, color) -> None:
        self._runner.run(self._robot.servo_light(servo, color))

    def chest_light(self, light: int, on: bool) -> None:
        self._runner.run(self._robot.chest_light(light, on))

    def eye_lights(self, r: int, g: int, b: int) -> None:
        self._runner.run(self._robot.eye_lights(r, g, b))

    def behaviour(self, *args: int) -> None:
        self._runner.run(self._robot.behaviour(*args))
