import asyncio
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import logging
import sqlite3
from config import TOKEN

bot = Bot(token=TOKEN)
dp = Dispatcher()

# логирование
logging.basicConfig(level=logging.INFO)

# работа с состояниями
class Form(StatesGroup):
    name = State()
    age = State()
    grade = State()

def init_db():
    conn = sqlite3.connect('school_data.db')
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS students
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    age INTEGER NOT NULL,
                    grade TEXT NOT NULL)''')
    conn.commit()
    conn.close()

init_db()

@dp.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await message.answer('Привет! Как тебя зовут?')
    await state.set_state(Form.name)

@dp.message(Form.name)
async def name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer('Сколько тебе лет?')
    await state.set_state(Form.age)

@dp.message(Form.age)
async def age(message: Message, state: FSMContext):
    await state.update_data(age=message.text)
    await message.answer('В каком классе ты учишься?')
    await state.set_state(Form.grade)

@dp.message(Form.grade)
async def grade(message: Message, state: FSMContext):
    await state.update_data(grade=message.text)
    student_data = await state.get_data()

    conn = sqlite3.connect('school_data.db')
    cur = conn.cursor()
    cur.execute('''INSERT INTO students (name, age, grade) VALUES (?, ?, ?)''', (student_data['name'], student_data['age'], student_data['grade']))
    conn.commit()
    conn.close()

    student_report = (f"Тебя зовут - {student_data['name']}\n"
                    f"Тебе {student_data['age']} лет\n"
                    f"Ты учишься в {student_data['grade']} классе\n")

    await message.answer(student_report)
    await state.clear()

async def main(dp):
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main(dp))
