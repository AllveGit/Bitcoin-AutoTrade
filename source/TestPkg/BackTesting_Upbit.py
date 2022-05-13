from datetime import tzinfo
import pyupbit
import numpy as np
import pandas as pd
from pandas import DataFrame, Series

def MakeBackTestData(ticker):
    total_earn_rate_list = []

    # k에 따라 수익률이 천차만별로 달라진다.
    for k in np.arange(0.1, 1.0, 0.1):
        k = round(k, 1)
        
        ohlcvDF = pyupbit.get_ohlcv(ticker)
        ohlcvDF.index = ohlcvDF.index.tz_localize(None)

        # 전일 고가에서 전일 저가를 빼고 pik를 곱한 값인 range를 구한다.
        # range를 금일 시가에 더하면 목표 매수가가 된다.
        ohlcvDF["range"] = (ohlcvDF["high"] - ohlcvDF["low"]) * k

        # 목표매수가를 구한다.
        # 전날의 range를 사용하기에 1씩 내린다.
        ohlcvDF["target_buy_price"] = ohlcvDF["open"] + ohlcvDF["range"].shift(1)

        # 금일이 최근5일 이동평균 값을 토대로 상승장인지 하락장인지 구분
        ohlcvDF["recent5_move_average"] = ohlcvDF["close"].rolling(window=5).mean().shift(1)
        ohlcvDF["bull_market"] = ohlcvDF["open"] > ohlcvDF["recent5_move_average"]

        # 수수료에 따른 수익률 차이
        fee = 0.0032

        # 금일 수익률 계산 (수익률 차이 포함)
        ohlcvDF["today_earn_rate"] = np.where((ohlcvDF["high"] > ohlcvDF["target_buy_price"]) & ohlcvDF["bull_market"], 
                                     ohlcvDF["close"] / ohlcvDF["target_buy_price"] - fee,
                                     1)
    
        # 금일까지 총 수익률 계산
        ohlcvDF["total_earn_rate"] = ohlcvDF["today_earn_rate"].cumprod()

        # MDD 계산
        # MDD는 투자 기간중에 최고 고점에서 현재 가격까지 얼마나 손실을 보았는지를 계산하는 것
        ohlcvDF["MDD"] = (ohlcvDF["total_earn_rate"].cummax() - ohlcvDF["total_earn_rate"]) / ohlcvDF["total_earn_rate"].cummax() * 100

        # 백테스팅 데이터 저장
        dataName = f"backtests/Upbit_{ticker}_BackTest_range{k * 100}%.xlsx"
        ohlcvDF.to_excel(dataName)

        total_earn_rate_list.append((k, ohlcvDF["total_earn_rate"][-2]))

    maxEarnK = 0
    maxEarnTotalRate = 0
    for elem in total_earn_rate_list:
        if maxEarnTotalRate < elem[1]:
            maxEarnK = elem[0]
            maxEarnTotalRate = elem[1]

    print(f"최대 수익률을 뽑은 K : {maxEarnK} 총 수익률 : {maxEarnTotalRate}")
