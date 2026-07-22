"""
pymecca -- unofficial Python control of the Meccano Meccanoid G15/G15KS
over Bluetooth LE.

Quick start (async)::

    import asyncio
    from pymecca import Meccanoid

    async def main():
        async with Meccanoid("C4:BE:84:D4:68:1B") as bot:
            await bot.eye_lights(7, 0, 0)

    asyncio.run(main())

Quick start (blocking)::

    from pymecca.sync import Meccanoid

    with Meccanoid("C4:BE:84:D4:68:1B") as bot:
        bot.eye_lights(7, 0, 0)

Find your robot's address with ``pymecca scan`` on the command line, or
:func:`pymecca.discover` from code.
"""

from .protocol import Color, Servo
from .robot import Meccanoid, NotConnectedError, discover

__all__ = [
    "Color",
    "Meccanoid",
    "NotConnectedError",
    "Servo",
    "discover",
]

__version__ = "2.0.0"
