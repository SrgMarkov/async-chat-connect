import argparse
import asyncio
import os

from dotenv import load_dotenv


async def post_message(host, port, message, user_hash):
    reader, writer = await asyncio.open_connection(host=host, port=port)

    writer.write(f"{user_hash}\n".encode())
    await writer.drain()
    submit_message = await reader.readline()
    print(submit_message.decode())

    writer.write(f"{message}\n\n".encode())
    await writer.drain()
    writer.close()


if __name__ == "__main__":
    load_dotenv()
    command_arguments = argparse.ArgumentParser(
        description="Скрипт подключения к подпольному чату с возможностью отправки сообщений"
    )
    command_arguments.add_argument(
        "message", help="Введите сообщение для чата"
    )
    command_arguments.add_argument(
        "--host", help="Укажите хост чата", default=os.getenv("HOST")
    )
    command_arguments.add_argument(
        "--port",
        help="Укажите порт чата",
        default=int(os.getenv("WRITE_PORT")),
        type=int,
    )
    command_arguments.add_argument(
        "--hash", help="Укажите токен чата", default=os.getenv("ACCOUNT_HASH")
    )
    args = command_arguments.parse_args()
    asyncio.run(post_message(args.host, args.port, args.message, args.hash))
