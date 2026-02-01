import random
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy import select, update, desc
from sqlalchemy.orm import selectinload

from app.config import bot
from app.models import async_session, User, Group, Homework, DutyLog
from app.states import Registration, News, AddGroup, Feedback, HomeworkState, ScheduleState
import app.keyboards as kb

router = Router()


@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        f"Привет, {message.from_user.first_name}!\n"
        "Добро пожаловать в бота колледжа. Выберите свою роль:",
        reply_markup=kb.role_kb()
    )
    await state.set_state(Registration.role)


@router.callback_query(Registration.role, F.data.startswith("role_"))
async def process_role(callback: CallbackQuery, state: FSMContext):
    role = callback.data.split("_")[1]
    await state.update_data(role=role)

    if role == 'teacher':
        async with async_session() as session:
            result = await session.execute(select(User).where(User.tg_id == callback.from_user.id))
            user = result.scalar_one_or_none()

            if not user:
                user = User(tg_id=callback.from_user.id, role='teacher')
                session.add(user)
            else:
                user.role = 'teacher'

            await session.commit()

        await callback.message.edit_text("Вы зарегистрированы как Учитель!", reply_markup=None)
        await callback.message.answer("Ваше меню:", reply_markup=kb.teacher_kb())
        await state.clear()

    elif role == 'student':
        async with async_session() as session:
            result = await session.execute(select(Group))
            groups = result.scalars().all()

        if not groups:
            await callback.message.answer("В базе пока нет групп. Попросите учителя добавить их.")
            await state.clear()
            return

        await callback.message.edit_text(
            "Выберите свою группу:",
            reply_markup=kb.groups_kb(groups)
        )
        await state.set_state(Registration.group)


@router.callback_query(Registration.group, F.data.startswith("group_"))
async def process_group(callback: CallbackQuery, state: FSMContext):
    group_id = int(callback.data.split("_")[1])
    data = await state.get_data()
    role = data.get('role')

    async with async_session() as session:
        result = await session.execute(select(User).where(User.tg_id == callback.from_user.id))
        user = result.scalar_one_or_none()

        if not user:
            user = User(tg_id=callback.from_user.id, role=role, group_id=group_id)
            session.add(user)
        else:
            user.role = role
            user.group_id = group_id

        await session.commit()

    await callback.message.delete()
    await callback.message.answer("Вы успешно зарегистрированы!", reply_markup=kb.student_kb())
    await state.clear()


@router.message(Command("add_group"))
async def add_group_handler(message: Message, state: FSMContext, role: str):
    if role != 'teacher': return

    if message.chat.type in ['group', 'supergroup']:
        args = message.text.split()
        if len(args) < 2:
            return await message.answer("В чате используйте формат: `/add_group Название`\nНапример: `/add_group П-11`")

        group_title = args[1]
        chat_id = message.chat.id

        async with async_session() as session:
            res = await session.execute(select(Group).where(Group.title == group_title))
            group = res.scalar_one_or_none()

            if group:
                group.chat_id = chat_id
                await message.answer(f"✅ Чат успешно привязан к уже существующей группе {group_title}!")
            else:
                session.add(Group(title=group_title, chat_id=chat_id))
                await message.answer(f"✅ Группа {group_title} создана и привязана к этому чату!")

            await session.commit()
    else:
        await message.answer("Введите название группы (например: П-11):")
        await state.set_state(AddGroup.name)


@router.message(F.text == "➕ Добавить группу")
async def add_group_btn(message: Message, state: FSMContext, role: str):
    if role != 'teacher': return
    await message.answer("Введите название группы (например: П-11):")
    await state.set_state(AddGroup.name)


@router.message(AddGroup.name)
async def add_group_finish(message: Message, state: FSMContext):
    name = message.text
    async with async_session() as session:
        res = await session.execute(select(Group).where(Group.title == name))
        if res.scalar_one_or_none():
            await message.answer("Такая группа уже есть.")
        else:
            session.add(Group(title=name))
            await session.commit()
            await message.answer(f"Группа {name} создана!")

    await state.clear()


@router.message(F.text == "📝 Добавить ДЗ")
async def add_hw_start(message: Message, state: FSMContext, role: str):
    if role != 'teacher': return

    async with async_session() as session:
        res = await session.execute(select(Group))
        groups = res.scalars().all()

    await message.answer("Для какой группы задание?", reply_markup=kb.groups_kb(groups, prefix="hw_group"))
    await state.set_state(HomeworkState.group)


@router.callback_query(HomeworkState.group, F.data.startswith("hw_group_"))
async def add_hw_group(callback: CallbackQuery, state: FSMContext):
    group_id = int(callback.data.split("_")[2])
    await state.update_data(group_id=group_id)
    await callback.message.edit_text("Напишите текст задания:")
    await state.set_state(HomeworkState.text)


@router.message(HomeworkState.text)
async def add_hw_text(message: Message, state: FSMContext):
    data = await state.get_data()
    group_id = data.get('group_id')
    text = message.text

    async with async_session() as session:
        session.add(Homework(group_id=group_id, text=text))
        await session.commit()

    await message.answer("✅ Домашнее задание сохранено!")
    await state.clear()


@router.message(F.text == "🔗 Привязать этот чат")
async def bind_chat(message: Message, role: str):
    if role != 'teacher': return
    if message.chat.type == 'private':
        return await message.answer("Эту команду нужно нажимать, находясь в ГРУППЕ.")

    async with async_session() as session:
        result = await session.execute(select(Group))
        groups = result.scalars().all()

    await message.answer(
        "К какой учебной группе привязать этот чат?",
        reply_markup=kb.groups_kb(groups)
    )


@router.callback_query(F.data.startswith("group_"))
async def bind_chat_callback(callback: CallbackQuery, state: FSMContext):
    if await state.get_state() == Registration.group:
        return

    group_id = int(callback.data.split("_")[1])
    chat_id = callback.message.chat.id

    async with async_session() as session:
        stmt = update(Group).where(Group.id == group_id).values(chat_id=chat_id)
        await session.execute(stmt)
        await session.commit()

    await callback.message.edit_text(f"Этот чат успешно привязан к группе!")


@router.message(F.text == "🧑‍✈️ Назначить дежурного")
async def duty_start(message: Message, role: str):
    if role != 'teacher': return

    if message.chat.type in ['group', 'supergroup']:
        async with async_session() as session:
            res = await session.execute(
                select(Group).where(Group.chat_id == message.chat.id).options(selectinload(Group.users))
            )
            group = res.scalar_one_or_none()

            if not group:
                return await message.answer("Чат не привязан к группе.")

            students = [u for u in group.users if u.role == 'student']
            if not students:
                return await message.answer("В группе нет студентов.")

            lucky = random.choice(students)

            try:
                chat_member = await bot.get_chat_member(message.chat.id, lucky.tg_id)
                name = chat_member.user.full_name
                mention = f"<a href='tg://user?id={lucky.tg_id}'>{name}</a>"
                await message.answer(f"🧹 Сегодня дежурный: {mention}!")
            except:
                await message.answer(f"Дежурный ID: {lucky.tg_id}")

    else:
        await message.answer("Эту кнопку нужно нажимать внутри чата группы.")


@router.message(F.text == "🖼 Обновить расписание")
async def set_schedule_start(message: Message, state: FSMContext, role: str):
    if role != 'teacher': return
    async with async_session() as session:
        res = await session.execute(select(Group))
        groups = res.scalars().all()
    await message.answer("Выберите группу:", reply_markup=kb.groups_kb(groups, prefix="sch_group"))
    await state.set_state(ScheduleState.group)


@router.callback_query(ScheduleState.group, F.data.startswith("sch_group_"))
async def set_schedule_group(callback: CallbackQuery, state: FSMContext):
    group_id = int(callback.data.split("_")[2])
    await state.update_data(group_id=group_id)
    await callback.message.edit_text("Отправьте фото расписания:")
    await state.set_state(ScheduleState.photo)


@router.message(ScheduleState.photo, F.photo)
async def set_schedule_photo(message: Message, state: FSMContext):
    data = await state.get_data()
    group_id = data.get('group_id')
    photo_id = message.photo[-1].file_id

    async with async_session() as session:
        stmt = update(Group).where(Group.id == group_id).values(schedule_photo_id=photo_id)
        await session.execute(stmt)
        await session.commit()

    await message.answer("✅ Расписание обновлено!")
    await state.clear()


@router.message(F.text == "📰 Создать новость")
async def news_start(message: Message, state: FSMContext, role: str):
    if role != 'teacher': return
    await message.answer("Введите текст новости:")
    await state.set_state(News.text)


@router.message(News.text)
async def news_text(message: Message, state: FSMContext):
    await state.update_data(text=message.text)

    async with async_session() as session:
        result = await session.execute(select(Group))
        groups = result.scalars().all()

    await message.answer("Кому отправить?", reply_markup=kb.target_kb(groups))
    await state.set_state(News.target)


@router.callback_query(News.target)
async def news_send(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    text = data.get('text')
    target = callback.data

    user_ids = []
    groups_to_send = []

    async with async_session() as session:
        if target == "target_all":
            res = await session.execute(select(User).where(User.role == 'student'))
            user_ids = [u.tg_id for u in res.scalars().all()]
            res_g = await session.execute(select(Group).where(Group.chat_id != None))
            groups_to_send = [(g.chat_id, g.title) for g in res_g.scalars().all()]

        else:
            g_id = int(target.split("_")[1])
            res = await session.execute(select(User).where(User.group_id == g_id))
            user_ids = [u.tg_id for u in res.scalars().all()]

            res_g = await session.execute(select(Group).where(Group.id == g_id))
            g = res_g.scalar_one_or_none()
            if g and g.chat_id:
                groups_to_send = [(g.chat_id, g.title)]

    count = 0
    for uid in user_ids:
        try:
            await bot.send_message(uid, f"🔔 <b>Важная новость:</b>\n\n{text}")
            count += 1
        except:
            pass

    for chat_id, title in groups_to_send:
        try:
            await bot.send_message(chat_id, f"📢 <b>Объявление для {title}:</b>\n\n{text}")
        except:
            pass

    await callback.message.edit_text(f"Новость отправлена {count} студентам и в {len(groups_to_send)} чатов.")
    await state.clear()


@router.message(F.text == "✍️ Анонимный отзыв")
async def feedback_start(message: Message, state: FSMContext, role: str):
    if role != 'student': return
    await message.answer("Напишите ваш вопрос или предложение. Учителя увидят его анонимно.")
    await state.set_state(Feedback.text)


@router.message(Feedback.text)
async def feedback_send(message: Message, state: FSMContext):
    text = message.text
    async with async_session() as session:
        res = await session.execute(select(User).where(User.role == 'teacher'))
        teachers = res.scalars().all()

    for t in teachers:
        try:
            await bot.send_message(t.tg_id, f"📬 <b>Анонимное сообщение:</b>\n\n{text}")
        except:
            pass

    await message.answer("Отправлено!")
    await state.clear()


@router.message(F.text == "📚 Домашка")
async def get_hw(message: Message, role: str):
    if role != 'student': return

    async with async_session() as session:
        user_res = await session.execute(select(User).where(User.tg_id == message.from_user.id))
        user = user_res.scalar_one_or_none()

        if not user or not user.group_id:
            return await message.answer("Вы не привязаны к группе.")

        hw_res = await session.execute(
            select(Homework)
            .where(Homework.group_id == user.group_id)
            .order_by(desc(Homework.id))
            .limit(5)
        )
        hws = hw_res.scalars().all()

    if not hws:
        return await message.answer("Домашки пока нет 🎉")

    response = "📚 <b>Последние задания:</b>\n\n"
    for hw in hws:
        date = hw.created_at.strftime("%d.%m") if hw.created_at else ""
        response += f"🔹 <i>{date}</i>: {hw.text}\n"

    await message.answer(response)


@router.message(F.text == "🗓 Расписание")
async def get_schedule(message: Message, role: str):
    if role != 'student': return

    async with async_session() as session:
        user_res = await session.execute(
            select(User).where(User.tg_id == message.from_user.id).options(selectinload(User.group))
        )
        user = user_res.scalar_one_or_none()

        if not user or not user.group:
            return await message.answer("Вы не в группе.")

        photo_id = user.group.schedule_photo_id

    if photo_id:
        await message.answer_photo(photo_id, caption=f"🗓 Расписание для {user.group.title}")
    else:
        await message.answer("Расписание еще не загружено.")