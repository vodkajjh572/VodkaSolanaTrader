import requests
import pandas as pd
import time

# --- بياناتك الشخصية ---
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
        # جلب البيانات من بينانس
        res = requests.get(f"https://api.binance.com/api/v3/klines?symbol={SYMBOL}&interval=15m&limit=100").json()
        df = pd.DataFrame(res, columns=['t','o','h','l','c','v','ct','qv','nt','tb','tq','i'])
        df['c'] = df['c'].astype(float)
        
        current_price = df['c'].iloc[-1]
        rsi_series = calculate_rsi(df['c'])
        rsi = rsi_series.iloc[-1]
        
        # حساب الربح أو الخسارة الحالية
        profit_usd = (current_price - BUY_PRICE) * AMOUNT_SOL
        
        # تحليل الحالة بناءً على مؤشر RSI
        if rsi < 35:
            pred = "تشبع بيعي واضح. الارتداد للأعلى متوقع قريباً 🚀"
            act = "السعر في القاع حالياً، لا تبيع بخسارة."
        elif rsi > 65:
            pred = "تشبع شرائي كبير. قد يبدأ السعر بالنزول قريباً ⚠️"
            act = "راقب السعر جيداً، قد تكون لحظة مناسبة للبيع."
        else:
            pred = "السوق في حالة استقرار وتذبذب طبيعي ⚖️"
            act = "استمر في المراقبة، لا توجد إشارات قوية حالياً."

        msg = f"🤖 **رادار سولانا الذكي**\n\n" \
              f"💰 السعر الآن: `{current_price}$`\n" \
              f"💵 صافي الربح/الخسارة: `{profit_usd:.3f}$`\n" \
              f"📈 مؤشر RSI: `{rsi:.1f}`\n\n" \
              f"🔮 **التوقع:** {pred}\n" \
              f"🎯 **القرار:** {act}"
        
        send_telegram_msg(msg)
        time.sleep(120) # يرسل تحديث كل دقيقتين
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(20)
