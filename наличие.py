import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties

API_TOKEN = '7437496034:AAFZvqBaeZd0ft--o6ea4Wns-LwLe9rRxJU'
bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Вкусы и цены
flavors = {
    "PODONKI АНАРХИЯ 🧊Тархун лимонад🍋": 15,
    "PODONKI АНАРХИЯ 🍋Лимонный мармелад🍮": 15,
    "HOTSPOT🍇Грейпфрут малина виноград🍇": 15,
    "HOTSPOT🍦Йогурт черника банан🍌": 15,
    "Рик и Морти 🍇 Клюква лайм🍋‍🟩": 15,
    "Рик и Морти 🍓Клубника банан🍌": 15,
    "Рик и Морти 💖Клюква земляника💝": 15,
    "Анархия V2 🥭Манго пинакалада🍹": 17,
    "Анархия V2 🍒Вишня лайт🍒": 17,
    "CATSWILL 🫐Черника ежевика🍓": 17,
    "CATSWILL 🍓Клубника жвачка банан🍌": 17,
    "CATSWILL 🍋Лимонад черника лайм🍋‍🟩": 17,
}

# Менеджеры
manager_ids = [958394597, 6593155809]

# Корзина и статусы
user_cart = {}
user_order_status = {}

# Кнопки выбора вкусов
def get_flavor_keyboard():
    keyboard = []
    for i, flavor in enumerate(flavors.keys()):
        keyboard.append([InlineKeyboardButton(text=f"{flavor} ➕", callback_data=f"add_{i}")])
    keyboard.append([InlineKeyboardButton(text="✅ Подтвердить заказ", callback_data="confirm")])
    keyboard.append([InlineKeyboardButton(text="🛒 Просмотреть корзину", callback_data="view_cart")])
    keyboard.append([InlineKeyboardButton(text="❌ Очистить выбор", callback_data="clear")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# Старт
@dp.message(Command("start"))
async def cmd_start(message: Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📦 Посмотреть наличие", callback_data="show_stock")],
            [InlineKeyboardButton(text="📩 Сделать заказ", callback_data="start_order")]
        ]
    )
    await message.answer(
        "Привет👋! Это <b>PAR ZAVOD💨</b> — выбери вкус и оформи заказ⭐️\n\nА также подписывайся на наш ТГК — тут проходят розыгрыши и скидки✅ — https://t.me/par_zavod",
        reply_markup=keyboard
    )

# Наличие
@dp.callback_query(F.data == "show_stock")
async def show_stock(callback: CallbackQuery):
    text = "<b>Сейчас в наличии:</b>\n"
    for name, price in flavors.items():
        text += f"• {name} — <b>{price} BYN✨</b>\n"
    await callback.message.answer(text, reply_markup=InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="📩 Сделать заказ", callback_data="start_order")]]
    ))
    await callback.answer()

# Начать заказ
@dp.callback_query(F.data == "start_order")
async def start_order(callback: CallbackQuery):
    user_cart[callback.from_user.id] = {}
    await callback.message.delete()
    await bot.send_message(callback.from_user.id, "Выбери вкусы (можно несколько):", reply_markup=get_flavor_keyboard())
    await callback.answer()

# Добавить вкус
@dp.callback_query(F.data.startswith("add_"))
async def add_to_cart(callback: CallbackQuery):
    user_id = callback.from_user.id
    index = int(callback.data.split("_")[1])
    flavor = list(flavors.keys())[index]
    user_cart.setdefault(user_id, {})
    user_cart[user_id][flavor] = user_cart[user_id].get(flavor, 0) + 1
    await callback.answer(f"{flavor} — {user_cart[user_id][flavor]} шт.")

# Очистить корзину
@dp.callback_query(F.data == "clear")
async def clear_cart(callback: CallbackQuery):
    user_cart[callback.from_user.id] = {}
    await callback.message.answer("Корзина очищена!")
    await callback.answer()

# Просмотр корзины
@dp.callback_query(F.data == "view_cart")
async def view_cart(callback: CallbackQuery):
    user_id = callback.from_user.id
    cart = user_cart.get(user_id, {})
    if not cart:
        await callback.answer("Корзина пуста.")
        return

    text = "<b>Ваша корзина:</b>\n"
    total = 0
    for name, qty in cart.items():
        price = flavors[name]
        total += price * qty
        text += f"• {name} — {qty} × {price} BYN = {qty * price} BYN✨\n"

    total_count = sum(cart.values())
    discount = 0
    if total_count >= 10:
        discount = 10
    elif total_count >= 5:
        discount = 5

    if discount:
        text += f"\n🎁 Скидка: -{discount} BYN✨"
        total -= discount

    text += f"\n\n<b>Итого: {total} BYN✨</b>"

    await callback.message.answer(text, reply_markup=InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="✅ Подтвердить заказ", callback_data="confirm")]]
    ))
    await callback.answer()

# Подтвердить заказ
@dp.callback_query(F.data == "confirm")
async def confirm_order(callback: CallbackQuery):
    user_id = callback.from_user.id
    cart = user_cart.get(user_id, {})
    if not cart:
        await callback.answer("Сначала выберите вкусы.")
        return

    user_order_status[user_id] = {"cart": cart}

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🚚 Доставка:2BYN+ОТЗЫВ✨", callback_data="delivery")],
            [InlineKeyboardButton(text="🏃‍♂️ Самовывоз:Ⓜ️МЕТРО ПАРТИЗАНСКАЯⓂ️", callback_data="pickup")]
        ]
    )
    await callback.message.answer("Выберите способ получения заказа:", reply_markup=keyboard)
    await callback.answer()

# Выбор доставки
@dp.callback_query(F.data.in_(["delivery", "pickup"]))
async def choose_delivery(callback: CallbackQuery):
    user_id = callback.from_user.id
    method = callback.data
    user_order_status[user_id]["method"] = method

    if method == "delivery":
        await bot.send_message(user_id, "Введите адрес доставки:")
    else:
        cart = user_order_status[user_id]["cart"]
        await finalize_order(user_id, "Самовывоз: метро Партизанская")

    await callback.answer()

# Получение адреса
@dp.message(F.text)
async def get_address(message: Message):
    user_id = message.from_user.id
    if user_id not in user_order_status or "method" not in user_order_status[user_id]:
        return

    if user_order_status[user_id]["method"] == "delivery":
        address = message.text
        await finalize_order(user_id, address)

# Финализировать заказ
async def finalize_order(user_id, address_info):
    cart = user_cart.get(user_id, {})
    total = 0
    text = f"🛒 Новый заказ от пользователя @{(await bot.get_chat(user_id)).username or user_id}:\n\n"
    for name, qty in cart.items():
        price = flavors[name]
        subtotal = price * qty
        total += subtotal
        text += f"• {name} — {qty} × {price} BYN = {subtotal} BYN✨\n"

    total_count = sum(cart.values())
    discount = 0
    if total_count >= 10:
        discount = 10
    elif total_count >= 5:
        discount = 5

    if user_order_status[user_id]["method"] == "delivery":
        total += 2
        text += "\n🚚 Доставка: +2 BYN+ОТЗЫВ✨"

    if discount:
        total -= discount
        text += f"\n🎁 Скидка: -{discount} BYN✨"

    text += f"\n\n<b>Итого: {total} BYN✨</b>\n<b>Получение:</b> {address_info}"

    for manager_id in manager_ids:
        await bot.send_message(manager_id, text)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Начать сначала", callback_data="start_order")]
        ]
    )

    await bot.send_message(user_id,
        "✅ Спасибо за заказ‼️\n\n"
        "Ваш заказ принят‼️ С вами в скором времени свяжется менеждер‼️\n\n"
        "🎁 Бонусы для постоянных клиентов‼️\n"
        "Подписывайся на наш канал ➔ https://t.me/par_zavod",
        reply_markup=keyboard
    )

    user_cart[user_id] = {}
    user_order_status[user_id] = {}

# Запуск
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())