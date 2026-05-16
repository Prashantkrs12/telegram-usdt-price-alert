FROM python:3.12-slim

WORKDIR /app

COPY telegram_price_bot.py /app/telegram_price_bot.py

CMD ["python", "telegram_price_bot.py"]
