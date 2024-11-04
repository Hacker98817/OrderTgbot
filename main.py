API_TOKEN = '8121447155:AAHbO67DuqTrjeGQtTYIOhEgxxldUmMHzP0'
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Состояния для машины состояний
class OrderState(StatesGroup):
    waiting_for_name = State()
    waiting_for_order = State()
    waiting_for_address = State()

# Словарь для хранения заказов
orders = {}

# Приветственное сообщение и начало процесса заказа
@dp.message(Command("start"))
async def start_order(message: Message, state: FSMContext):
    await message.answer("Добро пожаловать! Пожалуйста, укажите ваше имя.")
    await state.set_state(OrderState.waiting_for_name)

# Получаем имя
@dp.message(OrderState.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Спасибо! Теперь укажите ваш заказ.")
    await state.set_state(OrderState.waiting_for_order)

# Получаем заказ
@dp.message(OrderState.waiting_for_order)
async def process_order(message: Message, state: FSMContext):
    await state.update_data(order=message.text)
    await message.answer("Принято! Пожалуйста, укажите ваш адрес.")
    await state.set_state(OrderState.waiting_for_address)

# Получаем адрес
@dp.message(OrderState.waiting_for_address)
async def process_address(message: Message, state: FSMContext):
    user_data = await state.get_data()
    user_id = message.from_user.id
    orders[user_id] = {
        "name": user_data["name"],
        "order": user_data["order"],
        "address": message.text,
    }
    await message.answer(
        "Спасибо за заказ! Пожалуйста, подождите подтверждения. Мы сообщим вам, когда заказ будет готов."
    )
    await state.clear()

    # Отправляем администратору или обработчику заказа
    admin_id = "6698994131"  # Укажите ID администратора
    await bot.send_message(
        admin_id,
        f"Новый заказ от {user_id}, {user_data['name']}:\n"
        f"Заказ: {user_data['order']}\n"
        f"Адрес: {message.text}\n\n"
        "Для подтверждения используйте команду: /confirm_order {user_id}",
    )

# Подтверждение заказа администратором
@dp.message(Command("confirm_order"))
async def confirm_order(message: Message):
    args = message.text.split()
    if len(args) < 2:
        await message.answer("Укажите ID пользователя для подтверждения заказа.")
        return

    user_id = int(args[1])
    if user_id in orders:
        await bot.send_message(
            user_id,
            "Ваш заказ подтверждён! Он будет доставлен в течение 30 минут. Приятного аппетита!"
        )
        del orders[user_id]
        await message.answer("Заказ успешно подтвержден.")
    else:
        await message.answer("Заказ с указанным ID не найден.")

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
