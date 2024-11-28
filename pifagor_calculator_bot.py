import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from flask import Flask, render_template, request
from flask_ngrok import run_with_ngrok
import threading

# Настройки для Telegram
TELEGRAM_TOKEN = '8099243411:AAHoh5HgGkbj0-dWzSZ9b8rZbrP7isqRJRo'

# Настройки для Flask
app = Flask(__name__)
run_with_ngrok(app)  # Для запуска через ngrok (если локально)

# Включение логирования для Telegram бота
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Функция обработки команд от пользователя в Telegram
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Привет! Введи свою дату рождения (дд.мм.гггг), чтобы рассчитать числа по Пифагору.')

# Функция для обработки ввода даты в Telegram
def handle_date(update: Update, context: CallbackContext) -> None:
    date = update.message.text
    try:
        # Преобразуем дату и вычисляем числа
        day, month, year = map(int, date.split('.'))
        numbers = calculate_numbers(day, month, year)
        
        # Отправляем результаты пользователю
        response = f'Числа по Пифагору:\nДень: {numbers["day"]}\nМесяц: {numbers["month"]}\nГод: {numbers["year"]}\nСумма 1: {numbers["sum1"]}\nСумма 2: {numbers["sum2"]}'
        update.message.reply_text(response)
    except Exception as e:
        update.message.reply_text('Ошибка! Пожалуйста, введите дату в формате дд.мм.гггг.')

# Функция для расчета чисел по Пифагору
def calculate_numbers(day, month, year):
    # Простая логика для вычисления чисел
    sum1 = (day + month) % 9
    sum2 = (year + sum1) % 9
    return {
        'day': day % 9,
        'month': month % 9,
        'year': year % 9,
        'sum1': sum1,
        'sum2': sum2
    }

# Обработка команды /start
def start_telegram_bot():
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("date", handle_date))
    updater.start_polling()
    updater.idle()

# Веб-приложение на Flask
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    date = request.form['birthdate']
    try:
        day, month, year = map(int, date.split('.'))
        numbers = calculate_numbers(day, month, year)
        return render_template('result.html', numbers=numbers)
    except Exception as e:
        return render_template('index.html', error="Ошибка! Пожалуйста, введите дату в формате дд.мм.гггг.")

# Запуск Flask приложения и Telegram бота в отдельных потоках
if __name__ == '__main__':
    # Запускаем Telegram-бота в отдельном потоке
    threading.Thread(target=start_telegram_bot).start()

    # Запускаем Flask приложение
    app.run(debug=True)
