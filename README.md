# Telegram Price Alert Bot

This bot sends Telegram messages for:

## Binance P2P USDT/INR

- costs `Rs 99.00` or less
- supports `UPI`
- allows a transaction up to `Rs 80,000`

## Binance Futures

- `BTCUSDT` below `75,000`
- `ETHUSDT` below `2,100`
- `DOGEUSDT` below `0.09946`
- `SOLUSDT` below `85`
- `ADAUSDT` below `0.25`

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

GitHub Actions runs the bot every 5 minutes using
`.github/workflows/check-price.yml`.
