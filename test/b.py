import asyncio
import datetime


class A:

    def __init__(self):
        self._msg = datetime.datetime.now()

    async def curr_time(self):
        for _ in range(100):
            print(self._msg)
            await asyncio.sleep(1)

    async def run(self):
        for _ in range(100):
            self._msg = datetime.datetime.now()
            await asyncio.sleep(1)

    async def main(self):
        await asyncio.gather(a.curr_time(), a.run())


if __name__ == '__main__':
    a = A()
    asyncio.run(a.curr_time())
