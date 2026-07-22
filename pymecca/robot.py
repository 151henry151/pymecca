"""
Async Meccanoid client built on bleak.

Works anywhere bleak does: Linux (including Raspberry Pi), macOS and
Windows.
"""

from __future__ import annotations

import asyncio
import logging

from bleak import BleakClient, BleakScanner
from bleak.backends.characteristic import BleakGATTCharacteristic
from bleak.backends.device import BLEDevice

from . import protocol

logger = logging.getLogger(__name__)

# Candidate write characteristics, tried in order. These are the usual
# "vendor UART" characteristics of the CC254x/HM-1x style BLE modules
# this era of toys used.
WRITE_CHAR_CANDIDATES = (
    "0000ffe9-0000-1000-8000-00805f9b34fb",
    "0000ffe1-0000-1000-8000-00805f9b34fb",
)

# The ATT handle the original pymecca wrote to with gatttool; used as a
# fallback when none of the candidate UUIDs are present.
LEGACY_WRITE_HANDLE = 0x001F

# Standard (Bluetooth SIG) services we should never try to write robot
# commands to.
_STANDARD_SERVICE_PREFIXES = ("00001800-", "00001801-", "0000180a-", "0000180f-")


class NotConnectedError(RuntimeError):
    """
    Raised when a command is issued while not connected.
    """


async def discover(timeout: float = 10.0, name_filter: str = "mecc") -> list[BLEDevice]:
    """
    Scan for BLE devices whose advertised name contains ``name_filter``
    (case-insensitive). Returns matching devices; if none match, an
    empty list.
    """
    devices = await BleakScanner.discover(timeout=timeout)
    return [d for d in devices if d.name and name_filter.lower() in d.name.lower()]


class Meccanoid:
    """
    An async client for a Meccanoid G15/G15KS.

    Usage::

        async with Meccanoid("C4:BE:84:D4:68:1B") as robot:
            await robot.eye_lights(7, 0, 0)
            await robot.drive(100, 100)
            await asyncio.sleep(1)
            await robot.stop()

    ``address`` may be a MAC address string (Linux/Windows), a CoreBluetooth
    UUID string (macOS), or a ``BLEDevice`` from :func:`discover`.

    ``write_char`` optionally forces the GATT characteristic used for
    commands: a UUID string or an integer ATT handle. Leave it as None
    to auto-detect (which handles all firmwares seen in the wild so far).
    """

    def __init__(
        self,
        address: str | BLEDevice,
        *,
        write_char: str | int | None = None,
        wake_on_connect: bool = True,
    ) -> None:
        self._address = address
        self._forced_write_char = write_char
        self._wake_on_connect = wake_on_connect
        self._client: BleakClient | None = None
        self._char: BleakGATTCharacteristic | None = None
        self._state = protocol.MeccanoidState()
        self._send_lock = asyncio.Lock()

    # ------------------------------------------------------------------
    # Connection management

    @property
    def is_connected(self) -> bool:
        return self._client is not None and self._client.is_connected

    async def connect(self, timeout: float = 20.0) -> None:
        """
        Connect to the robot and send the wake-up sequence.
        """
        if self.is_connected:
            return

        client = BleakClient(
            self._address,
            timeout=timeout,
            disconnected_callback=self._on_disconnect,
        )
        await client.connect()
        try:
            self._char = self._find_write_char(client)
        except Exception:
            await client.disconnect()
            raise
        self._client = client
        logger.info(
            "Connected; writing commands to characteristic %s (handle 0x%04x)",
            self._char.uuid,
            self._char.handle,
        )

        if self._wake_on_connect:
            # Same greeting the original library used: a no-op wheel
            # command so the robot notices us, the "I'm awake"
            # behaviour, the default arm pose, and blue eyes.
            await self.stop()
            await self.send_raw(protocol.wake_frame())
            await self.send_raw(self._state.servo_frame())
            await self.eye_lights(0, 0, 7)

    async def disconnect(self) -> None:
        """
        Disconnect from the robot.
        """
        client, self._client, self._char = self._client, None, None
        if client is not None:
            await client.disconnect()

    async def __aenter__(self) -> Meccanoid:
        await self.connect()
        return self

    async def __aexit__(self, *exc) -> None:
        await self.disconnect()

    def _on_disconnect(self, _client: BleakClient) -> None:
        logger.warning("Meccanoid disconnected")
        self._client = None
        self._char = None

    def _find_write_char(self, client: BleakClient) -> BleakGATTCharacteristic:
        """
        Pick the characteristic to write commands to.
        """
        chars = [c for s in client.services for c in s.characteristics]

        forced = self._forced_write_char
        if forced is not None:
            for char in chars:
                if (isinstance(forced, int) and char.handle == forced) or (
                    isinstance(forced, str) and char.uuid.lower() == forced.lower()
                ):
                    return char
            raise NotConnectedError(f"Requested write characteristic {forced!r} not found")

        for uuid in WRITE_CHAR_CANDIDATES:
            for char in chars:
                if char.uuid.lower() == uuid and self._is_writable(char):
                    return char

        for char in chars:
            if char.handle == LEGACY_WRITE_HANDLE and self._is_writable(char):
                return char

        # Last resort: the first writable characteristic in a
        # vendor-specific service.
        for char in chars:
            if self._is_writable(char) and not char.service_uuid.lower().startswith(
                _STANDARD_SERVICE_PREFIXES
            ):
                logger.warning(
                    "No known Meccanoid characteristic found; guessing %s "
                    "(run `pymecca explore` and report your GATT table!)",
                    char.uuid,
                )
                return char

        raise NotConnectedError(
            "No writable GATT characteristic found on this device -- is this "
            "really a Meccanoid? Run `pymecca explore <address>` to inspect it."
        )

    @staticmethod
    def _is_writable(char: BleakGATTCharacteristic) -> bool:
        return "write" in char.properties or "write-without-response" in char.properties

    # ------------------------------------------------------------------
    # Commands

    async def send_raw(self, frame: bytes) -> None:
        """
        Send a pre-built 20-byte frame (see :mod:`pymecca.protocol`).
        """
        client, char = self._client, self._char
        if client is None or char is None or not client.is_connected:
            raise NotConnectedError("Not connected to the Meccanoid")
        response = "write-without-response" not in char.properties
        async with self._send_lock:
            await client.write_gatt_char(char, frame, response=response)

    async def drive(self, left_speed: int = 0, right_speed: int = 0) -> None:
        """
        Drive the wheels. Speeds are -255 .. 255; negative is
        backwards, zero stops that wheel. The robot keeps rolling until
        you send another drive command or :meth:`stop`.
        """
        await self.send_raw(protocol.drive_frame(left_speed, right_speed))

    async def stop(self) -> None:
        """
        Stop both wheels.
        """
        await self.drive(0, 0)

    async def servo(self, servo: int, value: int) -> None:
        """
        Move a servo to a position between 0x00 and 0xff (0x80 is
        centred). Servo numbers are in :class:`pymecca.Servo`.
        """
        await self.send_raw(self._state.set_servo(servo, value))

    async def servo_light(self, servo: int, color: int | str) -> None:
        """
        Set a servo's LED colour: a :class:`pymecca.Color`, a 0-7
        integer, or a name like "red" / "cyan" / "off".
        """
        await self.send_raw(self._state.set_servo_light(servo, color))

    async def chest_light(self, light: int, on: bool) -> None:
        """
        Turn one of the four chest LEDs (0-3) on or off.
        """
        await self.send_raw(self._state.set_chest_light(light, on))

    async def eye_lights(self, r: int, g: int, b: int) -> None:
        """
        Set the eye LED colour; each channel is 0 .. 7.
        """
        await self.send_raw(protocol.eye_lights_frame(r, g, b))

    async def behaviour(self, *args: int) -> None:
        """
        Send a raw opcode-0x19 behaviour/sound command. Mostly
        unexplored territory; ``behaviour(0x1d, ... x17)`` is the
        "I'm awake" greeting.
        """
        await self.send_raw(protocol.behaviour_frame(*args))
