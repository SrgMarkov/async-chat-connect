import argparse
import asyncio
import json
import logging
import os

import aiofiles
from dotenv import load_dotenv


logger = logging.getLogger("asyncio_chat_writer")


async def register(host, port, username):
    try:
        reader, writer = await asyncio.open_connection(host=host, port=port)
        answer = await reader.readline()
        logger.debug(answer.decode())
        writer.write("\n".encode())
        await writer.drain()
        await reader.readline()
        if "\n" in username:
            logger.debug("Регистрация не удалась. Имя пользователя не корректно")
            return None
        writer.write(f"{username}\n".encode())
        account_details = await reader.readline()
        logger.debug(account_details.decode())
        async with aiofiles.open("account_details.json", mode="w") as account_file:
            await account_file.write(account_details.decode())
            logger.debug("Данные авторизации сохранены в файл account_details.json")
    except OSError as error:
        logger.error(f"Возникла ошибка: {error}")
    finally:
        writer.close()
        await writer.wait_closed()


async def authorize(reader, writer, user_hash):
    answer = await reader.readline()
    logger.debug(answer.decode())
    writer.write(f"{user_hash}\n".encode())
    await writer.drain()

    check_token = await reader.readline()
    assert json.loads("null") is None
    user_data = json.loads(check_token.decode())
    logger.debug(user_data)

    if not user_data:
        logger.debug("Неизвестный токен. Проверьте его или зарегистрируйте заново.")
        return None
    return writer


async def submit_message(writer, message):
    writer.write(f"{' '.join(message)}\n\n".encode())
    await writer.drain()
    logger.debug(f"Сообщение отправлено: {' '.join(message)}")


async def send_message(host, port, user_hash, message):
    try:
        reader, writer = await asyncio.open_connection(host=host, port=port)
        await authorize(reader, writer, user_hash)
        await submit_message(writer, message)
        writer.close()
    except OSError as error:
        logger.error(f"Возникла ошибка: {error}")
    finally:
        writer.close()
        await writer.wait_closed()


if __name__ == "__main__":
    load_dotenv()
    logging.basicConfig(format="%(levelname)-3s %(message)s", level=logging.DEBUG)
    command_arguments = argparse.ArgumentParser(
        description="Скрипт подключения к подпольному чату\
            с возможностью отправки сообщений"
    )
    command_arguments.add_argument(
        "message", help="Введите сообщение для чата", nargs="+"
    )
    command_arguments.add_argument(
        "--host", help="Укажите хост чата", default=os.getenv("HOST")
    )
    command_arguments.add_argument(
        "--create",
        help="Используйте аргумент, если необходимо создать аккаунт",
        action="store_true",
        default=False,
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

    if args.create:
        asyncio.run(register(args.host, args.port, args.message))
    else:
        asyncio.run(send_message(args.host, args.port, args.hash, args.message))
