"""
Persistent Meccanoid BLE session over a local Unix socket.

The session process owns one Bluetooth connection. Clients send one
command line each and receive a single reply (``ok`` / ``error: ...``).
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import signal
import socket
import sys
import time
from pathlib import Path

from .commands import CommandOutcome, dispatch, format_reply
from .robot import Meccanoid

logger = logging.getLogger(__name__)

DEFAULT_DIR = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache")) / "pymecca"
DEFAULT_SOCKET_NAME = "session.sock"
DEFAULT_PID_NAME = "session.pid"
DEFAULT_INFO_NAME = "session.json"
READY_TIMEOUT = 45.0


def session_dir(path: Path | None = None) -> Path:
    return path if path is not None else DEFAULT_DIR


def socket_path(directory: Path | None = None) -> Path:
    return session_dir(directory) / DEFAULT_SOCKET_NAME


def pid_path(directory: Path | None = None) -> Path:
    return session_dir(directory) / DEFAULT_PID_NAME


def info_path(directory: Path | None = None) -> Path:
    return session_dir(directory) / DEFAULT_INFO_NAME


def read_info(directory: Path | None = None) -> dict | None:
    path = info_path(directory)
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def pid_is_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def session_is_live(directory: Path | None = None) -> bool:
    info = read_info(directory)
    if not info:
        return False
    pid = int(info.get("pid", 0))
    if not pid_is_alive(pid):
        return False
    sock = Path(info.get("socket", socket_path(directory)))
    return sock.exists()


def cleanup_stale(directory: Path | None = None) -> None:
    """
    Remove socket/pid/info files left behind by a dead session.
    """
    directory = session_dir(directory)
    info = read_info(directory)
    if info:
        pid = int(info.get("pid", 0))
        if pid_is_alive(pid):
            return
    for path in (socket_path(directory), pid_path(directory), info_path(directory)):
        try:
            path.unlink()
        except FileNotFoundError:
            pass


def send_command(
    line: str,
    directory: Path | None = None,
    timeout: float = 10.0,
) -> str:
    """
    Send one command line to the live session; return the reply text.
    """
    sock_file = socket_path(directory)
    if not sock_file.exists():
        raise FileNotFoundError(
            f"no session socket at {sock_file}; start one with `pymecca session start`"
        )
    payload = (line.strip() + "\n").encode("utf-8")
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
        sock.settimeout(timeout)
        sock.connect(str(sock_file))
        sock.sendall(payload)
        chunks: list[bytes] = []
        while True:
            data = sock.recv(4096)
            if not data:
                break
            chunks.append(data)
    return b"".join(chunks).decode("utf-8", errors="replace").rstrip("\n")


def stop_session(directory: Path | None = None, timeout: float = 10.0) -> str:
    """
    Ask the session to shut down; fall back to SIGTERM.
    """
    directory = session_dir(directory)
    info = read_info(directory)
    if not info and not socket_path(directory).exists():
        cleanup_stale(directory)
        return "no session running"

    try:
        reply = send_command("__shutdown__", directory=directory, timeout=timeout)
    except OSError:
        reply = ""

    pid = int((info or {}).get("pid", 0))
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if not session_is_live(directory):
            cleanup_stale(directory)
            return reply or "stopped"
        time.sleep(0.1)

    if pid and pid_is_alive(pid):
        os.kill(pid, signal.SIGTERM)
        time.sleep(0.3)
        if pid_is_alive(pid):
            os.kill(pid, signal.SIGKILL)
    cleanup_stale(directory)
    return "stopped (signaled)"


def wait_until_ready(directory: Path | None = None, timeout: float = READY_TIMEOUT) -> None:
    deadline = time.monotonic() + timeout
    last_error: Exception | None = None
    while time.monotonic() < deadline:
        try:
            reply = send_command("ping", directory=directory, timeout=2.0)
            if reply.startswith("ok"):
                return
            last_error = RuntimeError(reply)
        except OSError as e:
            last_error = e
        time.sleep(0.2)
    raise TimeoutError(f"session did not become ready: {last_error}")


class SessionServer:
    """
    Own a :class:`Meccanoid` connection and serve commands on a Unix socket.
    """

    def __init__(
        self,
        address: str,
        *,
        write_char=None,
        directory: Path | None = None,
        connect_timeout: float = 20.0,
    ) -> None:
        self.address = address
        self.write_char = write_char
        self.directory = session_dir(directory)
        self.connect_timeout = connect_timeout
        self._bot: Meccanoid | None = None
        self._server: asyncio.AbstractServer | None = None
        self._stop = asyncio.Event()

    async def run(self) -> None:
        self.directory.mkdir(parents=True, exist_ok=True)
        cleanup_stale(self.directory)

        sock_file = socket_path(self.directory)
        if sock_file.exists():
            sock_file.unlink()

        self._bot = Meccanoid(
            self.address, write_char=self.write_char, wake_on_connect=True
        )
        logger.info("Connecting to %s...", self.address)
        await self._bot.connect(self.connect_timeout)
        logger.info("Connected.")

        self._write_metadata()
        self._install_signal_handlers()

        self._server = await asyncio.start_unix_server(self._handle_client, path=str(sock_file))
        os.chmod(sock_file, 0o600)
        logger.info("Session listening on %s", sock_file)
        print(f"Session ready on {sock_file} (pid {os.getpid()})", flush=True)

        await self._stop.wait()
        await self._shutdown()

    def _write_metadata(self) -> None:
        meta = {
            "pid": os.getpid(),
            "address": self.address
            if isinstance(self.address, str)
            else getattr(self.address, "address", str(self.address)),
            "socket": str(socket_path(self.directory)),
        }
        info_path(self.directory).write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
        pid_path(self.directory).write_text(f"{os.getpid()}\n", encoding="utf-8")

    def _install_signal_handlers(self) -> None:
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            try:
                loop.add_signal_handler(sig, self._stop.set)
            except NotImplementedError:
                signal.signal(sig, lambda *_: self._stop.set())

    async def _handle_client(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> None:
        try:
            raw = await reader.readline()
            if not raw:
                return
            line = raw.decode("utf-8", errors="replace").rstrip("\n\r")
            if line.strip() == "__shutdown__":
                reply = "ok shutting down"
                writer.write((reply + "\n").encode("utf-8"))
                await writer.drain()
                self._stop.set()
                return

            assert self._bot is not None
            result = await dispatch(self._bot, line)
            if result.outcome == CommandOutcome.QUIT:
                # In a session, quit from a client means shutdown.
                reply = format_reply(result)
                writer.write((reply + "\n").encode("utf-8"))
                await writer.drain()
                self._stop.set()
                return

            writer.write((format_reply(result) + "\n").encode("utf-8"))
            await writer.drain()
        except Exception:
            logger.exception("session client handler failed")
            try:
                writer.write(b"error: internal session error\n")
                await writer.drain()
            except OSError:
                pass
        finally:
            writer.close()
            try:
                await writer.wait_closed()
            except OSError:
                pass

    async def _shutdown(self) -> None:
        logger.info("Shutting down session...")
        if self._server is not None:
            self._server.close()
            await self._server.wait_closed()
        if self._bot is not None:
            try:
                await self._bot.disconnect()
            except Exception:
                logger.debug("disconnect during shutdown failed", exc_info=True)
            self._bot = None
        cleanup_stale(self.directory)
        print("Session stopped.", flush=True)


def spawn_background(
    argv_foreground: list[str],
    *,
    directory: Path | None = None,
    log_path: Path | None = None,
) -> int:
    """
    Start ``argv_foreground`` detached and wait until the session answers ping.
    """
    import subprocess

    directory = session_dir(directory)
    directory.mkdir(parents=True, exist_ok=True)
    log_path = log_path or (directory / "session.log")
    with open(log_path, "a", encoding="utf-8") as log_file:
        proc = subprocess.Popen(
            argv_foreground,
            stdin=subprocess.DEVNULL,
            stdout=log_file,
            stderr=log_file,
            start_new_session=True,
            close_fds=True,
        )

    try:
        wait_until_ready(directory)
    except Exception:
        if proc.poll() is None:
            proc.terminate()
        raise
    print(f"Session started (pid {proc.pid}, log {log_path})")
    return 0


def main_foreground(
    address: str,
    *,
    write_char=None,
    directory: Path | None = None,
    connect_timeout: float = 20.0,
) -> int:
    server = SessionServer(
        address,
        write_char=write_char,
        directory=directory,
        connect_timeout=connect_timeout,
    )
    try:
        asyncio.run(server.run())
    except KeyboardInterrupt:
        return 130
    return 0


if __name__ == "__main__":
    # Convenience for `python -m pymecca.session ADDRESS`
    if len(sys.argv) < 2:
        print("usage: python -m pymecca.session ADDRESS", file=sys.stderr)
        sys.exit(2)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    sys.exit(main_foreground(sys.argv[1]))
