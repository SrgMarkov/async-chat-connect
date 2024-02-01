import argparse
import asyncio
from datetime import datetime
import logging
import os

import aiofiles
from dotenv import load_dotenv


logger = logging.getLogger("asyncio_chat_listrener")


async def get_chat_data(host, port, save_file):
    reader, writer = await asyncio.open_connection(host=host, port=port)
    logger.debug(f"Успешное подключение к чату {host}:{port}")
    current_time = datetime.now().strftime("%d.%m.%Y %H:%M")
    message = await reader.readline()
    async with aiofiles.open(save_file, mode="a+") as history_file:
        await history_file.write(f"[{current_time}] {message.decode()}")

    print(f"[{current_time}] {message.decode()}")


if __name__ == "__main__":
    load_dotenv()
    logging.basicConfig(format="%(levelname)-3s %(message)s", level=logging.DEBUG)

    command_arguments = argparse.ArgumentParser(
        description="Скрипт подключения к подпольному чату с\
            возможностью сохранения переписки"
    )
    command_arguments.add_argument(
        "--host", help="Укажите хост чата", default=os.getenv("HOST")
    )
    command_arguments.add_argument(
        "--port",
        help="Укажите порт чата",
        default=int(os.getenv("LISTEN_PORT")),
        type=int,
    )
    command_arguments.add_argument(
        "--file",
        help="Укажите путь к файлу для сохранения переписки",
        default=os.getenv("HISTORY_FILE"),
    )
    args = command_arguments.parse_args()
    while True:
        try:
            asyncio.run(get_chat_data(args.host, args.port, args.file))
        except OSError as error:
            logger.error(f"Возникла ошибка: {error}")
            logger.error("Сеанс завершен")
            break
