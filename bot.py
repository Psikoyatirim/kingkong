import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np
import yfinance as yf
import requests
import time
import os
from datetime import datetime

# =====================
# TELEGRAM AYARLARI
# =====================
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '8035211094:AAEqHt4ZosBJsuT1FxdCcTR9p9uJ1O073zY')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '-1002715468798')

def telegram_gonder(mesaj):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        r = requests.post(url, data={"chat_id": CHAT_ID, "text": mesaj, "parse_mode": "HTML"}, timeout=15)
        if r.status_code == 200:
            print("📤 Telegram gönderildi", flush=True)
        else:
            print(f"⚠️ Telegram hatası: {r.status_code}", flush=True)
    except Exception as e:
        print(f"⚠️ Telegram bağlantı hatası: {e}", flush=True)

def telegram_parcali(baslik, satirlar, parca_basina=30):
    if not satirlar:
        return
    toplam = (len(satirlar) + parca_basina - 1) // parca_basina
    for i in range(0, len(satirlar), parca_basina):
        parca = satirlar[i:i + parca_basina]
        no = (i // parca_basina) + 1
        ek = f" ({no}/{toplam})" if toplam > 1 else ""
        msg = f"{baslik}{ek}\n\n" + "\n".join(parca)
        telegram_gonder(msg)
        time.sleep(0.5)

# =====================
# SUNUCU AYARLARI (SABİT)
# =====================
INTERVAL = "4h"
PERIOD = "6mo"
INTERVAL_ADI = "4 Saat"
EMA_LENGTH = 35
SCAN_INTERVAL_SECONDS = 14400  # 4 saat

# =====================
# BIST HİSSELERİ
# =====================
BIST_ALL = [
    'A1CAP','ACSEL','ADEL','ADESE','ADGYO','AEFES','AFYON','AGESA','AGHOL','AGROT',
    'AGYO','AHGAZ','AKBNK','AKCNS','AKENR','AKFGY','AKFYE','AKGRT','AKMGY','AKSA',
    'AKSEN','AKSGY','AKSUE','AKYHO','ALARK','ALBRK','ALCAR','ALCTL','ALFAS','ALGYO',
    'ALKA','ALKIM','ALMAD','ANELE','ANGEN','ANHYT','ANSGR','ARCLK','ARDYZ','ARENA',
    'ARSAN','ARZUM','ASELS','ASGYO','ASTOR','ASUZU','ATAGY','ATAKP','ATATP','ATEKS',
    'AVGYO','AVHOL','AVOD','AVTUR','AYDEM','AYEN','AYES','AYGAZ','AZTEK','BAGFS',
    'BAKAB','BALAT','BANVT','BASCM','BAYRK','BEGYO','BERA','BEYAZ','BFREN','BIMAS',
    'BIOEN','BIZIM','BJKAS','BLCYT','BMSTL','BNTAS','BORLS','BOSSA','BRISA','BRKSN',
    'BRSAN','BRYAT','BSOKE','BTCIM','BUCIM','BURCE','BURVA','BVSAN','CANTE','CCOLA',
    'CELHA','CEMAS','CEMTS','CIMSA','CLEBI','CMENT','COSMO','CRDFA','CRFSA','CUSAN',
    'CWENE','DAGI','DARDL','DENGE','DERIM','DESA','DESPC','DEVA','DGGYO','DITAS',
    'DMRGD','DMSAS','DOAS','DOCO','DOFER','DOGUB','DOHOL','DOKTA','DYOBY','DZGYO',
    'EBEBK','ECILC','ECZYT','EDIP','EGEEN','EGEPO','EGGUB','EGSER','EKGYO','EKOS',
    'EKSUN','EMKEL','ENERY','ENJSA','ENKAI','EPLAS','ERBOS','EREGL','ERSU','ESCOM',
    'ESEN','ETILR','EUHOL','EUPWR','EUREN','EYGYO','FENER','FONET','FORMT','FORTE',
    'FRIGO','FROTO','GARAN','GEDIK','GEDZA','GENIL','GENTS','GEREL','GESAN','GIPTA',
    'GLBMD','GLCVY','GLRMK','GLYHO','GMTAS','GOLTS','GOODY','GOZDE','GRSEL','GSDDE',
    'GSDHO','GSRAY','GUBRF','GWIND','HALKB','HATEK','HATSN','HEDEF','HEKTS','HLGYO',
    'HOROZ','HRKET','HUBVC','HUNER','HURGZ','ICBCT','IDGYO','IHLAS','IHLGM','IMASM',
    'INDES','INFO','INTEK','INVEO','INVES','ISCTR','ISDMR','ISFIN','ISGSY','ISKUR',
    'ISMEN','IZENR','IZMDC','JANTS','KAPLM','KAREL','KARSN','KARTN','KATMR','KAYSE',
    'KBORU','KCHOL','KENT','KGYO','KIMMR','KLGYO','KLKIM','KLMSN','KLNMA','KLRHO',
    'KLSER','KLSYN','KMPUR','KNFRT','KONKA','KONTR','KONYA','KOPOL','KORDS','KOTON',
    'KRDMA','KRDMB','KRDMD','KRONT','KRSTL','KRTEK','KRVGD','KSTUR','KTSKR','KUTPO',
    'KUYAS','LIDER','LIDFA','LINK','LOGO','LUKSK','MAALT','MAGEN','MAKIM','MANAS',
    'MARBL','MARKA','MARTI','MAVI','MEDTR','MEGAP','MEGMT','MEPET','MERCN','MERIT',
    'MERKO','METRO','MGROS','MNDRS','MOBTL','MPARK','MRSHL','MSGYO','MTRKS','NATEN',
    'NETAS','NIBAS','NTGAZ','NTHOL','NUGYO','NUHCM','OBASE','ODAS','ORGE','ORMA',
    'OSTIM','OTKAR','OTTO','OYAKC','OYLUM','OZGYO','OZRDN','OZSUB','PAGYO','PARSN',
    'PATEK','PEKGY','PENTA','PETKM','PETUN','PGSUS','PKART','PKENT','PNSUT','POLHO',
    'PRDGS','PRKAB','PRKME','PSGYO','QNBFK','QNBTR','RAYSG','RGYAS','RODRG','RUBNS',
    'RYSAS','SAHOL','SANEL','SANFM','SANKO','SARKY','SASA','SAYAS','SEGMN','SEGYO',
    'SEKUR','SELEC','SELVA','SILVR','SISE','SKBNK','SKTAS','SMART','SNGYO','SNPAM',
    'SOKM','SONME','SUMAS','SUNTK','SUWEN','TATGD','TAVHL','TBORG','TCELL','TDGYO',
    'TEKTU','TGSAS','THYAO','TKFEN','TKNSA','TLMAN','TMSN','TOASO','TRGYO','TRHOL',
    'TRILC','TRMET','TRALT','TSKB','TTKOM','TTRAK','TUKAS','TUPRS','TURSG','ULKER',
    'ULUSE','ULUUN','UNLU','USAK','VAKBN','VAKKO','VANGD','VBTYZ','VERTU','VESBE',
    'VESTL','VKGYO','VKING','VSNMD','YATAS','YAYLA','YBTAS','YESIL','YGGYO','YIGIT',
    'YKBNK','YONGA','YUNSA','YYAPI','ZEDUR','ZOREN','ZRGYO'
]

# =====================
# KING KONG JUNIOR STRATEJİSİ
# =====================
def calculate_ema(data, period):
    return data.ewm(span=period, adjust=False).mean()

def calculate_heiken_ashi(df):
    ohlc4 = (df['Open'] + df['High'] + df['Low'] + df['Close']) / 4
    ha_open = np.zeros(len(df))
    ha_open[0] = ohlc4.iloc[0]
    for i in range(1, len(df)):
        ha_open[i] = (ohlc4.iloc[i] + ha_open[i-1]) / 2
    ha_close = np.zeros(len(df))
    for i in range(len(df)):
        ha_close[i] = (ohlc4.iloc[i] + ha_open[i] +
                       max(df['High'].iloc[i], ha_open[i]) +
                       min(df['Low'].iloc[i], ha_open[i])) / 4
    return pd.Series(ha_close, index=df.index)

def calculate_tma(data, length):
    ema1 = calculate_ema(data, length)
    ema2 = calculate_ema(ema1, length)
    ema3 = calculate_ema(ema2, length)
    tma1 = 3 * ema1 - 3 * ema2 + ema3
    ema4 = calculate_ema(tma1, length)
    ema5 = calculate_ema(ema4, length)
    ema6 = calculate_ema(ema5, length)
    tma2 = 3 * ema4 - 3 * ema5 + ema6
    return tma1 + (tma1 - tma2)

def calculate_signals(df, ema_length=35):
    ha_close = calculate_heiken_ashi(df)
    hlc3 = (df['High'] + df['Low'] + df['Close']) / 3
    kirmizi = calculate_tma(ha_close, ema_length)
    mavi = calculate_tma(hlc3, ema_length)

    long_cond = (mavi > kirmizi) & (mavi.shift(1) <= kirmizi.shift(1))

    last_signal = np.zeros(len(df))
    signals = np.zeros(len(df))
    for i in range(1, len(df)):
        if long_cond.iloc[i] and (last_signal[i-1] == 0 or last_signal[i-1] == -1):
            signals[i] = 1
            last_signal[i] = 1
        elif (mavi.iloc[i] < kirmizi.iloc[i]) and (mavi.iloc[i-1] >= kirmizi.iloc[i-1]) and (last_signal[i-1] == 1):
            signals[i] = -1
            last_signal[i] = -1
        else:
            last_signal[i] = last_signal[i-1]

    return pd.Series(signals, index=df.index)

# =====================
# TARAMA
# =====================
def tarama_yap(scan_number=1):
    buy_signals = []
    toplam = len(BIST_ALL)

    print(f"\n{'='*50}", flush=True)
    print(f"🔍 TARAMA #{scan_number} — {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}", flush=True)
    print(f"{'='*50}", flush=True)

    for i, symbol in enumerate(BIST_ALL, 1):
        if i % 50 == 1:
            print(f"📈 [{i}/{toplam}] İşleniyor...", flush=True)

        try:
            ticker = f"{symbol}.IS"
            df = yf.download(ticker, period=PERIOD, interval=INTERVAL,
                             progress=False, auto_adjust=True)

            if df is None or df.empty or len(df) < 50:
                continue

            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.droplevel(1)

            signals = calculate_signals(df, EMA_LENGTH)

            if signals.iloc[-1] == 1:
                fiyat = round(float(df['Close'].iloc[-1]), 2)
                buy_signals.append({
                    "hisse": symbol,
                    "fiyat": fiyat
                })
                print(f"  🚨 BUY: {symbol} — {fiyat} TL", flush=True)

        except Exception:
            continue

        time.sleep(0.2)

    print(f"✅ Tamamlandı! {len(buy_signals)} BUY sinyali bulundu.", flush=True)
    return buy_signals


# =====================
# ANA DÖNGÜ
# =====================
if __name__ == "__main__":
    print("🚀 King Kong Junior Otomatik Tarayıcı Başladı", flush=True)
    print(f"📈 Interval: {INTERVAL_ADI} | Her 4 saatte bir", flush=True)

    telegram_gonder(
        f"🤖 <b>King Kong Junior Bot Aktif</b>\n"
        f"📅 {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n"
        f"⏰ Interval: {INTERVAL_ADI}\n"
        f"🔄 Her 4 saatte bir tarama yapılacak\n"
        f"📊 {len(BIST_ALL)} hisse takip ediliyor"
    )

    scan_count = 0
    while True:
        scan_count += 1
        simdi = datetime.now().strftime('%d.%m.%Y %H:%M:%S')

        try:
            results = tarama_yap(scan_number=scan_count)

            if results:
                telegram_gonder(
                    f"🚨 <b>King Kong Junior — #{scan_count}</b>\n"
                    f"📅 {simdi}\n"
                    f"⏰ {INTERVAL_ADI}\n\n"
                    f"✅ BUY Sinyali: {len(results)} hisse"
                )
                time.sleep(0.5)

                satirlar = [
                    f"<b>{r['hisse']}</b> — {r['fiyat']} TL"
                    for r in results
                ]
                telegram_parcali("📈 <b>BUY SİNYALLERİ</b>", satirlar)

            else:
                telegram_gonder(
                    f"📊 <b>King Kong Junior — #{scan_count}</b>\n"
                    f"📅 {simdi}\n"
                    f"⏰ {INTERVAL_ADI}\n\n"
                    f"❌ BUY sinyali bulunamadı\n"
                    f"⏳ Sonraki tarama 4 saat sonra..."
                )

        except Exception as e:
            print(f"❌ Tarama hatası: {e}", flush=True)
            telegram_gonder(f"⚠️ Tarama hatası: {str(e)[:100]}\n🔄 30 saniye sonra yeniden deneniyor...")
            time.sleep(30)
            continue

        print(f"\n⏳ 4 saat bekleniyor...", flush=True)
        time.sleep(SCAN_INTERVAL_SECONDS)
