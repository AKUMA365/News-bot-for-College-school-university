from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

def role_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎓 Я Ученик", callback_data="role_student")],
        [InlineKeyboardButton(text="👨‍🏫 Я Учитель", callback_data="role_teacher")]
    ])

def student_kb():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="📚 Домашка"), KeyboardButton(text="🗓 Расписание")],
        [KeyboardButton(text="✍️ Анонимный отзыв"), KeyboardButton(text="ℹ️ Помощь")]
    ], resize_keyboard=True)

def teacher_kb():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="📰 Создать новость"), KeyboardButton(text="📝 Добавить ДЗ")],
        [KeyboardButton(text="🖼 Обновить расписание"), KeyboardButton(text="🧑‍✈️ Дежурный")],
        [KeyboardButton(text="🔗 Привязать этот чат"), KeyboardButton(text="➕ Добавить группу")],
        [KeyboardButton(text="ℹ️ Помощь")]
    ], resize_keyboard=True)

def groups_kb(groups_list, prefix="group"):
    builder = InlineKeyboardBuilder()
    for group in groups_list:
        builder.button(text=group.title, callback_data=f"{prefix}_{group.id}")
    builder.adjust(2)
    return builder.as_markup()

def target_kb(groups_list):
    builder = InlineKeyboardBuilder()
    builder.button(text="📢 Отправить ВСЕМ", callback_data="target_all")
    for group in groups_list:
        builder.button(text=f"Группе {group.title}", callback_data=f"target_{group.id}")
    builder.adjust(1)
    return builder.as_markup()