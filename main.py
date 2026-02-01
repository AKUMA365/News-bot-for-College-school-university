import asyncio
import logging
from aiogram import Dispatcher
from app.config import bot
from app.models import async_main
from app.handlers import router
from app.middlewares import RoleMiddleware


async def main():
    await async_main()

    dp = Dispatcher()
    dp.update.outer_middleware(RoleMiddleware())
    dp.include_router(router)

    print("Bot started...")
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exiting...')