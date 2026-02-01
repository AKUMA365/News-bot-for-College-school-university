from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy import select
from app.models import async_session, User


class RoleMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        tg_user = data.get('event_from_user')

        if not tg_user:
            data['role'] = None
            return await handler(event, data)

        async with async_session() as session:
            result = await session.execute(select(User).where(User.tg_id == tg_user.id))
            user = result.scalar_one_or_none()

            if user:
                data['role'] = user.role
                data['db_user'] = user
            else:
                data['role'] = None

        return await handler(event, data)