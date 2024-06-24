import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import  StateFilter
import google.generativeai as genai
import os 
import cv2 
import requests
from dotenv import load_dotenv
import shutil
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from gemini import prompt, Model

load_dotenv()
# Настройка логирования (logging setup)
logging.basicConfig(level=logging.INFO)

# Инициализация бота с токеном (Bot initialization with token)
bot_token = os.getenv('BOT_TOKEN')
bot = Bot(bot_token)

# Инициализация диспетчера (Dispatcher initialization)
dp = Dispatcher()

# Конфигурация API ключа для Google Generative AI (API key configuration for Google Generative AI)
gemini_api_key = os.getenv('GEMINI_API_KEY')
genai.configure(api_key = gemini_api_key)

# Модель и промпт для генеративного AI (Model and prompt for generative AI)
model = Model
chat = prompt

# Определение состояний (State definitions)
class WaitingForMessage(StatesGroup):
    CaptureMessages = State()
    NonCaptureMessages = State()

# Обработчик команды /start (Handler for the /start command)
@dp.message(Command("start"))
async def bot_start(message: types.Message, state: FSMContext):
    # Создание клавиатуры (Keyboard creation)
    kb = [
        [
            types.KeyboardButton(text="start chat💻"),
        ],
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
    )
    
    # Приветственное сообщение (Welcome message)
    await message.answer("""
💻Hello I'm Chat bot with Gemini by IgorBlink
 """, reply_markup=keyboard)

# Обработчик сообщения "start chat💻" (Handler for the "start chat💻" message)
@dp.message(F.text.lower() == "start chat💻")
async def new_chat(message: types.Message, state: FSMContext):
    # Установка состояния для захвата сообщений (Set state for capturing messages)
    await state.set_state(WaitingForMessage.CaptureMessages)
    await message.reply("chat was successfully created.")

# Обработчик сообщений в состоянии CaptureMessages (Handler for messages in CaptureMessages state)
@dp.message(WaitingForMessage.CaptureMessages)
async def bot_answer(message: types.Message, state: FSMContext, photos_dir="photos", audio_dir="audio", video_dir="content"):
    # Создание клавиатуры (Keyboard creation)
    kb = [
        [
            types.KeyboardButton(text="stop⛔"),
        ],
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
    )

    # Обработка текстовых сообщений (Processing text messages)
    if message.text:
        if message.text == "stop⛔":
            await message.answer("Chat been successfully stoped✅!")
            await state.set_state(WaitingForMessage.NonCaptureMessages)
            await bot_start(message=message, state=state)   
        else:
            waitforasnwer = await message.answer("Generating answer⌛")
            question = message.text
            response = chat.send_message(question,
                                         safety_settings={
                                             'HATE': 'BLOCK_NONE',
                                             'HARASSMENT': 'BLOCK_NONE',
                                             'SEXUAL': 'BLOCK_NONE',
                                             'DANGEROUS': 'BLOCK_NONE'
                                         })
            await bot.delete_message(chat_id=message.chat.id, message_id=waitforasnwer.message_id)
            await message.answer(response.text, reply_markup=keyboard)
    # Обработка фото (Processing photo messages)
    elif message.photo:
        waitforasnwer = await message.answer("Generating answerт⌛")
        file_name = f"{photos_dir}/{message.photo[-1].file_id}.jpg"
        os.makedirs(photos_dir, exist_ok=True)
        await bot.download(message.photo[-1], destination=file_name)
        print(f"Photo downloaded to: {file_name}")
        sample_file = genai.upload_file(path=file_name,
                                        display_name="UserPhoto")
        print(f"Uploaded file '{sample_file.display_name}' as: {sample_file.uri}")
        file = genai.get_file(name=sample_file.name)
        print(f"Retrieved file '{file.display_name}' as: {sample_file.uri}")
        response = model.generate_content(["Describe image", sample_file])
        await bot.delete_message(chat_id=message.chat.id, message_id=waitforasnwer.message_id)
        await message.answer(response.text, reply_markup=keyboard)
        os.remove(file_name)

# Главная функция для запуска поллинга (Main function to start polling)
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
