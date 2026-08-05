"""
Tests for the session line protocol (no Bluetooth hardware).
"""

from __future__ import annotations

import asyncio
import socket
import tempfile
from pathlib import Path

from pymecca.commands import dispatch, format_reply
from pymecca.protocol import Servo


class FakeBot:
    def __init__(self) -> None:
        self.calls: list[tuple] = []

    async def servo(self, servo: int, value: int) -> None:
        self.calls.append(("servo", servo, value))

    async def servo_light(self, servo: int, color) -> None:
        self.calls.append(("servo_light", servo, color))

    async def chest_light(self, light: int, on: bool) -> None:
        self.calls.append(("chest_light", light, on))

    async def eye_lights(self, r: int, g: int, b: int) -> None:
        self.calls.append(("eye_lights", r, g, b))

    async def drive(self, left_speed: int = 0, right_speed: int = 0) -> None:
        self.calls.append(("drive", left_speed, right_speed))

    async def stop(self) -> None:
        self.calls.append(("stop",))

    async def behaviour(self, *args: int) -> None:
        self.calls.append(("behaviour", args))

    async def send_raw(self, frame: bytes) -> None:
        self.calls.append(("send_raw", frame))


def _send_to(sock_path: Path, line: str) -> str:
    payload = (line.strip() + "\n").encode("utf-8")
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
        sock.settimeout(5.0)
        sock.connect(str(sock_path))
        sock.sendall(payload)
        chunks: list[bytes] = []
        while True:
            data = sock.recv(4096)
            if not data:
                break
            chunks.append(data)
    return b"".join(chunks).decode().rstrip("\n")


def test_unix_socket_command_roundtrip():
    bot = FakeBot()
    with tempfile.TemporaryDirectory() as tmp:
        sock_path = Path(tmp) / "session.sock"

        async def run():
            async def handle(reader, writer):
                raw = await reader.readline()
                result = await dispatch(bot, raw.decode().rstrip("\n\r"))
                writer.write((format_reply(result) + "\n").encode())
                await writer.drain()
                writer.close()
                await writer.wait_closed()

            server = await asyncio.start_unix_server(handle, path=str(sock_path))
            async with server:
                loop = asyncio.get_running_loop()
                reply = await loop.run_in_executor(
                    None, lambda: _send_to(sock_path, "raise right arm")
                )
                assert reply == "ok raise right arm"

        asyncio.run(run())
        assert bot.calls == [("servo", Servo.RIGHT_SHOULDER, 0xFF)]
