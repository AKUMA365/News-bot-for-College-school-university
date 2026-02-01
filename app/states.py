from aiogram.fsm.state import State, StatesGroup

class Registration(StatesGroup):
    role = State()
    group = State()

class News(StatesGroup):
    text = State()
    target = State()

class AddGroup(StatesGroup):
    name = State()

class Feedback(StatesGroup):
    text = State()

class HomeworkState(StatesGroup):
    group = State()
    text = State()

class ScheduleState(StatesGroup):
    group = State()
    photo = State()