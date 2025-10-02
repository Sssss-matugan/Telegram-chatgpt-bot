import os
import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Токены из переменных окружения
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я бот с ChatGPT. Отправь мне сообщение, и я постараюсь на него ответить!"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Просто отправь мне любое сообщение, и я отвечу с помощью ChatGPT!"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    
    try:
        response = get_chatgpt_response(user_message)
        # Обрезаем сообщение если слишком длинное для Telegram
        if len(response) > 4096:
            response = response[:4090] + "..."
        await update.message.reply_text(response)
        
    except Exception as e:
        logger.error(f"Ошибка при обращении к ChatGPT: {e}")
        await update.message.reply_text("Извините, произошла ошибка. Попробуйте позже.")

def get_chatgpt_response(message: str) -> str:
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": message}
        ],
        "max_tokens": 500,
        "temperature": 0.7
    }
    
    response = requests.post(OPENAI_API_URL, headers=headers, json=data, timeout=30)
    response.raise_for_status()
    
    result = response.json()
    return result["choices"][0]["message"]["content"]

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Ошибка: {context.error}")

def main():
    # Проверяем что токены загружены
    if not TELEGRAM_TOKEN or not OPENAI_API_KEY:
        logger.error("Токены не найдены! Проверьте файл .env")
        return
    
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_error_handler(error_handler)
    
    print("Бот запущен...")
    application.run_polling()

if __name__ == "__main__":
    main()
