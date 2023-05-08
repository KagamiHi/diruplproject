import asyncio
from rustplus import RustSocket

async def main():
    socket = RustSocket("IP", "PORT", STEAMID, PLAYERTOKEN)
    await socket.connect()

    print(f"It is {(await socket.get_time()).time}")

    await socket.disconnect()

asyncio.run(main())