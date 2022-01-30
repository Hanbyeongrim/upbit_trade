import time
import datetime
import pyupbit
import numpy as np

start = time.time()

access = "xLXg1r7B4itxi5fUip0eesGzxBDSGQ7OkfjkN5Bo"  # 본인 값으로 변경
secret = "DZmMcPxzI8mYLd8xTaK39cnilHLu8UsBFBjRpFnE"  # 본인 값으로 변경
upbit = pyupbit.Upbit(access, secret)


def get_target_price(ticker, k):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price


def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)  # api내에서 일봉시작이 9시로 되어 있음
    start_time = df.index[0]
    return start_time


def get_balance(ticker):
    """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0
    return 0


def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(ticker=ticker)["orderbook_units"][0]["ask_price"]


def get_ror(coin, k=0.5):
    """K별 누적수익률(ror) 산출"""
    df = pyupbit.get_ohlcv("KRW-"+coin, count=7)

    df['range'] = (df['high'] - df['low']) * k
    df['target'] = df['open'] + df['range'].shift(1)

    df['ror'] = np.where(df['high'] > df['target'],
                         df['close'] / df['target'],
                         1)

    ror = df['ror'].cumprod()[-2]
    return ror


def get_best_k(coin):
    max_k = 0
    max_ror = 0
    for k in np.arange(0.1, 1.0, 0.05):
        try:
            ror = get_ror(coin, round(k, 2))
            if ror > max_ror:
                max_ror = ror
                max_k = round(k, 4)
            # print("%.2f %f %.2f" % (k, ror, best_k))
        except Exception:
            print(datetime.date.today(), "Exception!!! with K %f" % k)
    # print("My Best K : %.2f" % max_k)
    return max_k


best_k_btc = get_best_k("BTC")  # 처음 사용 할 최적 btc_K 산출
best_k_eth = get_best_k("ETH")  # 처음 사용 할 최적 eth_K 산출

# 로그인
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")

# print(get_balance("KRW"))
# print(get_balance("BTC"))

# 자동매매 시작
while True:
    try:
        now = datetime.datetime.now()
        start_time = get_start_time("KRW-BTC")
        end_time = start_time + datetime.timedelta(days=1)

        # 9시~ 익일 8시59분30초
        if start_time < now < end_time - datetime.timedelta(seconds=30):
            # BUY BTC
            target_price_btc = get_target_price("KRW-BTC", best_k_btc)  # 변동성전략에 따른 목표가
            current_price_btc = get_current_price("KRW-BTC")
            if target_price_btc < current_price_btc:
                krw = get_balance("KRW")
                if krw > 10000:
                    upbit.buy_market_order("KRW-BTC", (krw / 2))  # 비트코인과 이더리움을 절반씩 운용하기 위함
                    print(datetime.date.today(), "BUY BTC!!!")
            # BUY ETH
            target_price_eth = get_target_price("KRW-ETH", best_k_eth)  # 변동성전략에 따른 목표가
            current_price_eth = get_current_price("KRW-ETH")
            if target_price_eth < current_price_eth:
                krw = get_balance("KRW")
                if krw > 10000:
                    upbit.buy_market_order("KRW-ETH", (krw / 2))  # 비트코인과 이더리움을 절반씩 운용하기 위함
                    print(datetime.date.today(), "BUY ETH!!!")
        else:
            best_k_btc = get_best_k("BTC")  # 당일 거래 시작 전 새로운 최적 btc K 산출
            best_k_eth = get_best_k("ETH")  # 당일 거래 시작 전 새로운 최적 eth K 산출
            btc = get_balance("BTC")
            eth = get_balance("ETH")
            if btc > 0.0002:  # 수수료 이상일 경우 전량매도
                upbit.sell_market_order("KRW-BTC", btc * 0.9995)
                print(datetime.date.today(), "SELL BTC!!!")
            if eth > 0.0002:  # 수수료 이상일 경우 전량매도
                upbit.sell_market_order("KRW-ETH", eth * 0.9995)
                print(datetime.date.today(), "SELL ETH!!!")
        time.sleep(1)
    except Exception as e:
        print(e)
        time.sleep(1)
