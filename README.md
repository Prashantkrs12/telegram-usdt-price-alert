# Telegram USDT Price Alert Bot

This bot sends a Telegram message when a visible Binance P2P USDT/INR offer:

- costs `Rs 99.00` or less
- supports `UPI`
- allows a transaction up to `Rs 80,000`

## Run it

```bash
export TELEGRAM_BOT_TOKEN="your_bot_token"
export TELEGRAM_CHAT_ID="your_chat_id"
python3 telegram_price_bot.py
```

## Get your chat ID

1. Open your bot in Telegram and press **Start**.
2. Ask Codex to fetch the chat ID from Telegram.
3. Codex will place that value into the run command for you.

## Test the Binance filter only

```bash
python3 telegram_price_bot.py --once
```

## Run one alert check

```bash
export TELEGRAM_BOT_TOKEN="your_bot_token"
export TELEGRAM_CHAT_ID="your_chat_id"
python3 telegram_price_bot.py --once-send
```

## Free scheduled deployment

GitHub Actions runs the bot every 10 minutes using
`.github/workflows/check-price.yml`.
