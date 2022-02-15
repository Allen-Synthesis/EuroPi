try:
    import uasyncio as asyncio
except ImportError:
    import asyncio
from europi import oled


def increment(counter):
    return counter + 1


async def main():
    counter = 0
    while True:
        oled.centre_text(f"Hello world\n{counter}")

        counter = increment(counter)

        await asyncio.sleep(1)


if __name__ in ["__main__", "contrib.hello_world"]:
    asyncio.run(main())
