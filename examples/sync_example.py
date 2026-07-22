#!/usr/bin/env python3
"""
The same idea as demo.py but with the blocking API -- no asyncio
needed. Handy for quick scripts and experimenting in a Python REPL:

    >>> from pymecca.sync import Meccanoid
    >>> bot = Meccanoid("C4:BE:84:D4:68:1B")
    >>> bot.connect()
    >>> bot.eye_lights(0, 7, 0)
"""

import sys
import time

from pymecca.sync import Meccanoid, discover

if len(sys.argv) > 1:
    target = sys.argv[1]
else:
    print("Scanning for a Meccanoid...")
    found = discover()
    if not found:
        sys.exit("No Meccanoid found -- is it on and in range?")
    target = found[0]
    print(f"Found {target.name} at {target.address}")

with Meccanoid(target) as bot:
    for r, g, b in ((7, 0, 0), (0, 7, 0), (0, 0, 7)):
        bot.eye_lights(r, g, b)
        time.sleep(0.7)
    for light in range(4):
        bot.chest_light(light, True)
        time.sleep(0.2)
    for light in range(4):
        bot.chest_light(light, False)
