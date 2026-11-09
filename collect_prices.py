import csv
import os
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo
import requests

API = "https://api.gold-api.com/price/{symbol}/INR"
OUT = "data/spot_history.csv"
TROY_OUNCE_GRAMS = 31.1035
FIELDS = ["timestamp_utc", "date_ist", "metal", "symbol", "currency",
          "spot_per_troy_oz_inr", "spot_per_gram_inr", "api_updated_at", "source"]

def get_price(symbol):
    response = requests.get(API.format(symbol=symbol), timeout=20)
    response.raise_for_status()
    data = response.json()
    if not isinstance(data.get("price"), (int, float)):
        raise ValueError(f"Unexpected API response for {symbol}: {data}")
    if data.get("currency") != "INR":
        raise ValueError(f"API did not return INR for {symbol}: {data}")
    return data

def main():
    os.makedirs("data", exist_ok=True)
    now = datetime.now(timezone.utc)
    today_ist = now.astimezone(ZoneInfo("Asia/Kolkata")).date().isoformat()
    records = []
    for symbol, metal in [("XAU", "Gold 24K spot benchmark"), ("XAG", "Silver spot benchmark")]:
        data = get_price(symbol)
        per_gram = float(data["price"]) / TROY_OUNCE_GRAMS
        records.append({
            "timestamp_utc": now.isoformat(timespec="seconds"),
            "date_ist": today_ist,
            "metal": metal,
            "symbol": symbol,
            "currency": "INR",
            "spot_per_troy_oz_inr": round(float(data["price"]), 4),
            "spot_per_gram_inr": round(per_gram, 4),
            "api_updated_at": data.get("updatedAt", ""),
            "source": "Gold-API.com live spot API"
        })

    existing = []
    if os.path.exists(OUT):
        with open(OUT, newline="", encoding="utf-8") as f:
            existing = list(csv.DictReader(f))

    # Keep one daily observation per metal; retain the most recent 120 days.
    by_key = {(r["date_ist"], r["symbol"]): r for r in existing}
    for r in records:
        by_key[(r["date_ist"], r["symbol"])] = r
    cutoff = (now.astimezone(ZoneInfo("Asia/Kolkata")).date() - timedelta(days=120)).isoformat()
    kept = [r for r in by_key.values() if r.get("date_ist", "") >= cutoff]
    kept.sort(key=lambda r: (r["date_ist"], r["symbol"]))
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(kept)
    print(f"Saved {len(records)} spot observations to {OUT}")

if __name__ == "__main__":
    main()
