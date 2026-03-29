import requests
import pandas as pd
import pandas_ta as ta
import time

# --- بياناتك الثابتة ---
TOKEN = "8632452400:AAFrt9I-BlX7JyysX3I8UJb6ScjrkF7rY3U"
CHAT_ID = "8141702723"
SYMBOL = "SOLUSDT"
BUY_PRICE = 82.49  # سعر دخولك
AMOUNT_SOL = 0.111889

def send_telegram_msg(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={text}&parse_mode=Markdown"
    try: requests.get(url)
    except: pass

def get_market_data():
    url = f"https://api.binance.com/api/v3/klines?symbol={SYMBOL}&interval=15m&limit=100"
    res = requests.get(url).json()
    df = pd.DataFrame(res, columns=['t','o','h','l','c','v','ct','qv','nt','tb','tq','i'])
    df['c'] = df['c'].astype(float)
    return df

while True:
    try:
        df = get_market_data()
        current_price = df['c'].iloc[-1]
        
        # --- الحسابات الرياضية والمؤشرات ---
        # 1. RSI (قوة الزخم)
        rsi = ta.rsi(df['c'], length=14).iloc[-1]
        
        # 2. Bollinger Bands (الدعم والمقاومة)
        bbands = ta.bbands(df['c'], length=20, std=2)
        lower_band = bbands['BBL_20_2.0'].iloc[-1]  # أقوى دعم
        upper_band = bbands['BBU_20_2.0'].iloc[-1]  # أقوى مقاومة
        
        # 3. EMA 20 (متوسط السعر للاتجاه)
        ema_20 = ta.ema(df['c'], length=20).iloc[-1]
        
        # 4. MACD (اتجاه السيولة)
        macd = ta.macd(df['c'], fast=12, slow=26, signal=9)
        macd_hist = macd['MACDh_12_26_9'].iloc[-1]

        # --- حساب محفظتك ---
        profit_usd = (current_price - BUY_PRICE) * AMOUNT_SOL
        trend = "صاعد 🟢" if current_price > ema_20 else "هابط 🔴"

        # --- عقل البوت (التوقعات والنصائح) ---
        if rsi < 35 and current_price <= lower_band:
            prediction = "تشبع بيعي عنيف. متوقع ارتداد (انفجار) للأعلى قريباً جداً 🚀"
            action = "لا تبيع أبداً، السعر في القاع. فرصة ممتازة للتعزيز."
        elif rsi > 65 and current_price >= upper_band:
            prediction = "تشبع شرائي. السعر وصل للقمة ومحتمل أن يصحح للأسفل ⚠️"
            action = "جهز نفسك لجني الأرباح والبيع الآن!"
        elif macd_hist > 0 and rsi >= 45:
            prediction = "السيولة تدخل بقوة والزخم إيجابي ويميل للصعود 📈"
            action = "احتفظ بالعملة (Hold)، السوق يتحسن."
        elif macd_hist < 0 and rsi < 45:
            prediction = "الزخم سلبي حالياً، قد نشهد تذبذباً أو نزولاً طفيفاً 📉"
            action = "انتظر ولا تتخذ أي إجراء الآن."
        else:
            prediction = "السوق في مسار عرضي (حيرة بين البائعين والمشترين) ⚖️"
            action = "مراقبة فقط، لا توجد حركة قوية."

        # --- شكل الرسالة التي ستصلك ---
        msg = f"""
🤖 **الرادار الذكي | Solana**
──────────────
💰 **وضع المحفظة:**
• السعر الآن: `{current_price}$`
• سعر دخولك: `{BUY_PRICE}$`
• الربح/خسارة: `{profit_usd:.3f}$`

📊 **التحليل الفني (مهم):**
• الاتجاه العام: {trend}
• نقطة الدعم (القاع): `{lower_band:.2f}$`
• نقطة المقاومة (القمة): `{upper_band:.2f}$`
• مؤشر RSI: `{rsi:.1f}`

🔮 **توقع البوت:**
_{prediction}_

🎯 **قرارك:**
**{action}**
"""
        send_telegram_msg(msg)
        
        # البوت سيرسل التقرير كل دقيقتين (120 ثانية) لكي لا يزعجك ولكي يأخذ وقتاً لقراءة الشموع
        time.sleep(120) 

    except Exception as e:
        time.sleep(10)
