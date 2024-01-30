import asyncio
import aiofiles
import datetime


async def get_chat_data():
    while True:
        try:
            reader, writer = await asyncio.open_connection(host='minechat.dvmn.org', port=5000)
            current_time = datetime.datetime.now().strftime('%d.%m.%Y %H:%M')
            message = await reader.readline()
            async with aiofiles.open('chat_history.txt', mode='a+') as history_file:
                await history_file.write(f'[{current_time}] {message.decode()}')

            print(f'[{current_time}] {message.decode()}')
        except Exception as error:
            print(f'Error: {error}')



if __name__ == '__main__':
    asyncio.run(get_chat_data())
