from sqlalchemy import BigInteger, String, Integer, ForeignKey, DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

engine = create_async_engine(url='sqlite+aiosqlite:///storage.sqlite', echo=False)
async_session = async_sessionmaker(engine, expire_on_commit=False)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class Group(Base):
    __tablename__ = 'groups'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    chat_id: Mapped[int] = mapped_column(BigInteger, nullable=True)
    schedule_photo_id: Mapped[str] = mapped_column(String, nullable=True)

    users = relationship("User", back_populates="group")
    homeworks = relationship("Homework", back_populates="group")
    duty_logs = relationship("DutyLog", back_populates="group")


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    role: Mapped[str] = mapped_column(String, nullable=False)
    group_id: Mapped[int] = mapped_column(ForeignKey('groups.id'), nullable=True)

    group = relationship("Group", back_populates="users")


class Homework(Base):
    __tablename__ = 'homeworks'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    group_id: Mapped[int] = mapped_column(ForeignKey('groups.id'))
    text: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())

    group = relationship("Group", back_populates="homeworks")


class DutyLog(Base):
    __tablename__ = 'duty_logs'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    group_id: Mapped[int] = mapped_column(ForeignKey('groups.id'))
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    date: Mapped[str] = mapped_column(String)

    group = relationship("Group", back_populates="duty_logs")


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)