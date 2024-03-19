import asyncio

async def main():
    process = await asyncio.create_subprocess_shell("python main.py")

asyncio.run(main())