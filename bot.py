import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from bs4 import BeautifulSoup
import requests
import sqlite3
from config import token

bot = Bot(token=token)
dp = Dispatcher()

conn = sqlite3.connect('currency.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS exchange_rates (
                    id INTEGER PRIMARY KEY, 
                    content TEXT)''')
conn.commit()

@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer("Исползьуй команду /rate чтобы получить курсы валют")

@dp.message(Command('rate'))
async def get_exchange_rate(message: types.Message):
    url = "https://www.nbkr.kg/index.jsp?lang=RUS"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    exchange_rates_body = soup.find("div", class_="exchange-rates-body")
    if not exchange_rates_body:
        await message.answer("ДАнных нет")
        return

    tbody = exchange_rates_body.find("tbody")
    if not tbody:
        await message.answer("Данных нет")
        return

    exchange_rates = []
    
    for row in tbody.find_all("tr"):
        cells = row.find_all("td")
        if len(cells) >= 3:
            currency = cells[0].get_text(strip=True)
            rate1 = cells[1].get_text(strip=True)
            rate2 = cells[2].get_text(strip=True)
            exchange_rates.append(f"{currency}: {rate1} / {rate2}")

    if exchange_rates:
        rates_text = "\n".join(exchange_rates)
        cursor.execute("REPLACE INTO exchange_rates (id, content) VALUES (1, ?)", (rates_text,))
        conn.commit()
        await message.answer(rates_text)
    else:
        await message.answer("Курсы валют не найдены")

@dp.message()
async def echo(message: types.Message):
    await message.answer("Введите /rate получение актуальных курсов валют")

async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped")
