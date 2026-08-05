#!/usr/bin/env python3
"""
Minimal async example: find the robot, wake it, flash the eyes, wave.

Run with no arguments to auto-discover, or pass the robot's address:

    python examples/demo.py [ADDRESS]
"""

import asyncio
import sys

from pymecca import Meccanoid, Servo, discover


async def main() -> None:
    if len(sys.argv) > 1:
        target = sys.argv[1]
    else:
        print("Scanning for a Meccanoid...")
        found = await discover()
        if not found:
            sys.exit("No Meccanoid found -- is it on and in range?")
        target = found[0]
        print(f"Found {target.name} at {target.address}")

    async with Meccanoid(target) as bot:
        # Red eyes, wave the right arm, back to blue.
        await bot.eye_lights(7, 0, 0)
        await bot.servo(Servo.RIGHT_SHOULDER, 0xFF)
        await asyncio.sleep(1)
        for _ in range(3):
            await bot.servo(Servo.RIGHT_ELBOW, 0x40)
            await asyncio.sleep(0.4)
            await bot.servo(Servo.RIGHT_ELBOW, 0xC0)
            await asyncio.sleep(0.4)
        await bot.servo(Servo.RIGHT_SHOULDER, 0x80)
        await bot.servo(Servo.RIGHT_ELBOW, 0x80)
        await bot.eye_lights(0, 0, 7)


if __name__ == "__main__":
    asyncio.run(main())
