import os
import re
import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import asyncio

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

conn = sqlite3.connect("balance.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    amount REAL,
    comment TEXT
)
""")
conn.commit()

def get_balance():
    cursor.execute("SELECT SUM(amount) FROM transactions")
    total = cursor.fetchone()[0]
    return total if total else 0

@dp.message()
async def handle_message(message: types.Message):
    text = message.text.strip()
    match = re.match(r'([+-]?\d+)\s+(.*)', text)
    if not match:
        return
    amount = int(match.group(1))
    comment = match.group(2)

    cursor.execute(
        "INSERT INTO transactions (amount, comment) VALUES (?, ?)",
        (amount, comment)
    )
    conn.commit()

    await message.reply(f"✅ Операция добавлена.\nТекущий баланс: {get_balance()} ₽")

@dp.message(Command(commands=["balance"]))
async def balance_cmd(message: types.Message):
    await message.reply(f"💰 Текущий баланс: {get_balance()} ₽")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
