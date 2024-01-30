import asyncio


async def get_chat_data():
    reader, writer = await asyncio.open_connection(host='minechat.dvmn.org', port=5000)
    while True:
        data = await reader.readline()
        print(data.decode())


if __name__ == '__main__':
    asyncio.run(get_chat_data())
