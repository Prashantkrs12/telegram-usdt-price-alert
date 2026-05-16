#!/usr/bin/env python3
import json
import os
import sys
import time
from urllib import request, parse


BINANCE_URL = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
FUTURES_PRICE_URL = "https://fapi.binance.com/fapi/v1/ticker/price"
TARGET_PRICE = 99.0
TARGET_AMOUNT_INR = 80000.0
MARKET_THRESHOLDS = {
    "BTCUSDT": 75000.0,
    "ETHUSDT": 2100.0,
    "DOGEUSDT": 0.09946,
    "SOLUSDT": 85.0,
    "ADAUSDT": 0.25,
}
STATE_FILE = "alert_state.json"


def post_json(url, payload, headers=None):
    data = json.dumps(payload).encode("utf-8")
    req = request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json", **(headers or {})},
        method="POST",
    )
    with request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))


def telegram_call(token, method, params=None):
    body = parse.urlencode(params or {}).encode("utf-8")
    req = request.Request(
        f"https://api.telegram.org/bot{token}/{method}",
        data=body,
        method="POST",
    )
    with request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))


def get_json(url):
    with request.urlopen(url, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fetch_ads():
    payload = {
        "asset": "USDT",
        "fiat": "INR",
        "page": 1,
        "rows": 20,
        "tradeType": "BUY",
        "payTypes": ["UPI"],
    }
    data = post_json(BINANCE_URL, payload)
    return data.get("data", [])


def matching_ads(ads):
    matches = []
    for item in ads:
        adv = item.get("adv", {})
        advertiser = item.get("advertiser", {})
        try:
            price = float(adv["price"])
            min_limit = float(adv["minSingleTransAmount"])
            max_limit = float(adv["dynamicMaxSingleTransAmount"])
            available = float(adv["surplusAmount"])
        except (KeyError, TypeError, ValueError):
            continue

        trade_methods = {
            method.get("tradeMethodName", "")
            for method in adv.get("tradeMethods", [])
        }
        if (
            price <= TARGET_PRICE
            and "UPI" in trade_methods
            and min_limit <= TARGET_AMOUNT_INR <= max_limit
        ):
            matches.append(
                {
                    "price": price,
                    "name": advertiser.get("nickName", "Unknown"),
                    "available": available,
                    "min_limit": min_limit,
                    "max_limit": max_limit,
                }
            )
    return sorted(matches, key=lambda ad: ad["price"])


def format_alert(ad):
    return (
        "USDT alert\n"
        f"Price: Rs {ad['price']:.2f}\n"
        f"Seller: {ad['name']}\n"
        f"Available: {ad['available']:.2f} USDT\n"
        f"Limit: Rs {ad['min_limit']:,.2f} - Rs {ad['max_limit']:,.2f}\n"
        "Payment: UPI"
    )


def fetch_futures_prices():
    prices = {}
    for symbol in MARKET_THRESHOLDS:
        data = get_json(f"{FUTURES_PRICE_URL}?symbol={symbol}")
        prices[symbol] = float(data["price"])
    return prices


def load_state():
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError:
        return {}


def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as fh:
        json.dump(state, fh, indent=2, sort_keys=True)
        fh.write("\n")


def market_alerts(prices, state):
    alerts = []
    next_state = dict(state)
    for symbol, threshold in MARKET_THRESHOLDS.items():
        price = prices[symbol]
        is_below = price < threshold
        was_below = bool(state.get(symbol, False))
        if is_below and not was_below:
            alerts.append(
                f"{symbol.replace('USDT', '')} alert\n"
                f"Price: {price:.8f} USDT\n"
                f"Threshold: below {threshold:.8f} USDT"
            )
        next_state[symbol] = is_below
    return alerts, next_state


def run_once(send_alert=False):
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if send_alert and (not token or not chat_id):
        print("Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID first.", file=sys.stderr)
        return 1

    matches = matching_ads(fetch_ads())
    if matches:
        best = matches[0]
        alert = format_alert(best)
        print(alert)
        if send_alert:
            telegram_call(token, "sendMessage", {"chat_id": chat_id, "text": alert})

    prices = fetch_futures_prices()
    alerts, next_state = market_alerts(prices, load_state())
    save_state(next_state)
    if alerts:
        for alert in alerts:
            print(alert)
            if send_alert:
                telegram_call(token, "sendMessage", {"chat_id": chat_id, "text": alert})
    elif not matches:
        print("No matching alert found.")
    return 0


def main():
    if "--once" in sys.argv:
        return run_once()
    if "--once-send" in sys.argv:
        return run_once(send_alert=True)

    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        print("Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID first.", file=sys.stderr)
        return 1

    last_alert_key = None
    while True:
        try:
            matches = matching_ads(fetch_ads())
            if matches:
                best = matches[0]
                alert_key = (
                    best["price"],
                    best["name"],
                    best["min_limit"],
                    best["max_limit"],
                )
                if alert_key != last_alert_key:
                    telegram_call(
                        token,
                        "sendMessage",
                        {"chat_id": chat_id, "text": format_alert(best)},
                    )
                    last_alert_key = alert_key
            time.sleep(60)
        except Exception as exc:
            print(f"check failed: {exc}", file=sys.stderr)
            time.sleep(60)


if __name__ == "__main__":
    raise SystemExit(main())
