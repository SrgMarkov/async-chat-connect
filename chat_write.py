import argparse
import asyncio
import json
import logging
import os

import aiofiles
from dotenv import load_dotenv


logger = logging.getLogger("asyncio_chat_writer")


async def post_message(host, port, message, user_hash, create):
    reader, writer = await asyncio.open_connection(host=host, port=port)
    answer = await reader.readline()
    logger.debug(answer.decode())
    if create:
        writer.write("\n".encode())
        await writer.drain()
        await reader.readline()
        writer.write(f"{create}\n".encode())
        account_details = await reader.readline()
        logger.debug(account_details.decode())
        async with aiofiles.open('account_details.json', mode="w") as account_file:
            await account_file.write(account_details.decode())
        return None
    writer.write(f"{user_hash}\n".encode())
    await writer.drain()
    submit_message = await reader.readline()
    assert json.loads("null") is None
    user_data = json.loads(submit_message.decode())
    logger.debug(user_data)
    if not user_data:
        logger.debug("Неизвестный токен. Проверьте его или зарегистрируйте заново.")
        return None

    writer.write(f"{message}\n\n".encode())
    await writer.drain()
    logger.debug(f"Сообщение отправлено: {message}")
    writer.close()


if __name__ == "__main__":
    load_dotenv()
    logging.basicConfig(format="%(levelname)-3s %(message)s", level=logging.DEBUG)
    command_arguments = argparse.ArgumentParser(
        description="Скрипт подключения к подпольному чату\
            с возможностью отправки сообщений"
    )
    command_arguments.add_argument("message", help="Введите сообщение для чата")
    command_arguments.add_argument(
        "--host", help="Укажите хост чата", default=os.getenv("HOST")
    )
    command_arguments.add_argument(
        "--create",
        help="Используйте аргумент, если необходимо создать аккаунт. После аргумента введите желаемое имя пользователя",
        default=None,
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
    asyncio.run(
        post_message(args.host, args.port, args.message, args.hash, args.create)
    )
