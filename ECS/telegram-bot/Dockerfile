FROM python:3.12-slim
RUN pip install python-telegram-bot google-generativeai

ENV T_TOKEN=telegram_token
ENV G_TOKEN=google_token

COPY . /app
WORKDIR /app

CMD ["python", "bot.py"]