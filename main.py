from aiogram import Bot, Dispatcher, executor, types
import logging
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage



import requests
from bs4 import BeautifulSoup

user_parametrs = []

logging.basicConfig(level=logging.INFO)

bot = Bot("BOT_TOKEN")
dp = Dispatcher(bot, storage=MemoryStorage())

kb = ReplyKeyboardMarkup(resize_keyboard=True,
                         one_time_keyboard=False)
kb.add(KeyboardButton("/show"), KeyboardButton("size_and_brand"))

class UserState(StatesGroup):
    size1 = State()
    brand1 = State()



@dp.message_handler(commands=["start"])
async def send_welcome(message: types.Message):
    await message.answer("""<b>Привет!!\nСюда будут приходить все товары, выбранной вами, категории.</b>""",
                         parse_mode="HTML",
                         reply_markup=kb)


@dp.message_handler(Text(equals="size_and_brand"))
async def parametrs(message: types.Message):
    await message.answer("<b>Введите размер</b> <em>(us)</em>.",
                         parse_mode="HTML",)
    await UserState.size1.set()

@dp.message_handler(state=UserState.size1)
async def get_username(message: types.Message, state: FSMContext):
    await state.update_data(user_size=message.text)
    await message.answer("<b>Отлично! Теперь введите название бренда (если в названии есть пробелы, пишите с пробелами).</b>",
                         parse_mode="HTML")
    await UserState.next()



@dp.message_handler(state=UserState.brand1)
async def save_parametrs(message: types.Message, state: FSMContext):
    global user_parametrs
    await state.update_data(user_brand=message.text)
    data = await state.get_data()
    user_size = data["user_size"].upper()
    user_brand = data["user_brand"].lower()
    if " " in user_brand:
        popa = user_brand.split(" ")
        user_brand = "-".join(popa)
    user_parametrs.append(user_size)
    user_parametrs.append(user_brand)
    await message.answer(f"<b>Отлично, данные сохранены!</b> <em>Размер: {user_size}, бренд: {user_brand}.</em>\n<b>Нажми [/show], чтобы посмотреть все позиции.</b>",
                        parse_mode="HTML",
                        reply_markup=kb)
    await state.finish()





@dp.message_handler(commands=["show"])
async def send_description(message: types.Message):
    global user_parametrs
    headers = {
        "Accept": "*/*",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }
    final = user_parametrs
    user_size = final[0]
    user_brand = final[1].lower()


    url = f"https://brandshop.ru/{user_brand}/?sort=priceASC&mfp=13o-razmer%5B{user_size}%5D,83-kategoriya%5B%D0%A4%D1%83%D1%82%D0%B1%D0%BE%D0%BB%D0%BA%D0%B8,%D0%A2%D0%BE%D0%BB%D1%81%D1%82%D0%BE%D0%B2%D0%BA%D0%B8,%D0%A1%D0%B2%D0%B8%D1%82%D0%B5%D1%80%D1%8B%5D"

    req = requests.get(url, headers=headers)
    res = req.content

    res2 = []
    soup = BeautifulSoup(res, "lxml")
    shmotki = soup.find_all(class_="product-card__link")
    for i in shmotki:
        url_shmotki = i.get("href")
        res2.append(url_shmotki)

    res67 = []
    for line in range(1, len(res2)):
        link = f"https://brandshop.ru{res2[line]}"
        res67.append(link)

    for line_res in range(len(res67)):
        await message.answer(f"<b>Все позиции:</b>\n{res67[line_res]}",
                             parse_mode="HTML")

    user_parametrs = []


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)


