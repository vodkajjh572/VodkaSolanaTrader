import requests
import pandas as pd
import time

# --- بياناتك ---
TOKEN = "8632452400:AAFrt9I-BlX7JyysX3I8UJb6ScjrkF7rY3U"
CHAT_ID = "8141702723"
SYMBOL = "SOLUSDT"
BUY_PRICE = 82.49
AMOUNT_SOL = 0.111889

def send_telegram_msg(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={text}&parse_mode=Markdown"
    try: requests.get(url)
    except: pass

def calculate_rsi(prices, period=14):
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1+rs))

while True:
    try:
        res = requests.get(f"https://api.binance.com/api/v3/klines?symbol={SYMBOL}&interval=15m&limit=100").json()
        df = pd.DataFrame(res, columns=['t','o','h','l','c','v','ct','qv','nt','tb','tq','i'])
        df['c'] = df['c'].astype(float)
        
        current_price = df['c'].iloc[-1]
        rsi = calculate_rsi(df['c']).iloc[-1]
        
        # حساب الدعم والمقاومة (بولينجر مبسط)
        sma = df['c'].rolling(window=20).mean().iloc[-1]
        std = df['c'].rolling(window=20).std().iloc[-1]
        lower_band = sma - (2 * std)
        upper_band = sma + (2 * std)
        
        profit_usd = (current_price - BUY_PRICE) * AMOUNT_SOL
        
        # تحليل الحالة
        if rsi < 35:
            pred = "تشبع بيعي. الارتداد يقترب 🚀"
            act = "تمسك بالعملة، السعر في القاع."
        elif rsi > 65:
            pred = "وصلنا للقمة، قد ينزل السعر ⚠️"
            act = "فكر في البيع إذا كنت رابحاً."
        else:
            pred = "السوق مستقر حالياً ⚖️"
            act = "راقب التحديث القادم."

        msg = f"🤖 **رادار سولانا (النسخة المستقرة)**\n\n💰 السعر: `{current_price}$`\n💵 الربح: `{profit_usd:.3f}$`\n📈 RSI: `{rsi:.1f}`\n\n🔮 **التوقع:** {pred}\n🎯 **القرار:** {act}"
        
        send_telegram_msg(msg)
        time.sleep(120)
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(20)
