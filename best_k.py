import pyupbit
import numpy as np
import time

start = time.time()


def get_ror(k=0.5):
    """K별 누적수익률(ror) 산출"""
    df = pyupbit.get_ohlcv("KRW-BTC", count=7)
    df['range'] = (df['high'] - df['low']) * k
    df['target'] = df['open'] + df['range'].shift(1)

    df['ror'] = np.where(df['high'] > df['target'],
                         df['close'] / df['target'],
                         1)

    ror = df['ror'].cumprod()[-2]
    return ror


best_k = 0
best_ror = 0
for k in np.arange(0.1, 1.0, 0.01):
    try:
        ror = get_ror(round(k, 2))
        if ror > best_ror:
            best_ror = ror
            best_k = round(k, 4)
        # print("%.2f %f %.2f" % (k, ror, best_k))
    except Exception as e:
        print("Exception!!! with K %f" % k)

print("Time : ", time.time() - start)
print("My Best K : %.2f" % best_k)
