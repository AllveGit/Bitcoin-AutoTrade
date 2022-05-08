from math import floor
import datetime
import pyupbit
from SystemPkg.TradeWorker import TradeWorker_BullMarket
from SystemPkg.DefaultConfig import DefaultConfig

class TradeWorker_BullMarket_Upbit(TradeWorker_BullMarket):
    # 업비트 원화마켓 이용
    BalanceType = "KRW"
    # 업비트 최소 주문/매도 금액이 5000원 이상
    MinTradePrice = 5000

    def __init__(self, ticker):
        super().__init__(ticker)

    def run(self):
        # 업비트 계정 불러오기
        accessKey, secretKey = DefaultConfig().GetUpbitInfo()
        self.accountInfo = pyupbit.Upbit(accessKey, secretKey)

        curCashKRW = self.GetBalanceCash()
        if curCashKRW is None:
            self.tradelog_signal.emit("===== 업비트 로그인 실패! 제대로 된 OpenAPI키를 넣어주세요. =====")
            self.close()
            return
        else:
            self.tradelog_signal.emit("===== 업비트 로그인 성공! =====")
            self.tradelog_signal.emit(f"현재 보유 현금(KRW) : {curCashKRW}₩")

        super().run()

    def GetBalanceCash(self):
        return floor(self.accountInfo.get_balance(TradeWorker_BullMarket_Upbit.BalanceType))

    def GetBalanceTickerCoin(self):
        return self.accountInfo.get_balance(self.ticker)

    def GetCurrentPrice(self):
        return pyupbit.get_current_price(self.ticker)

    def GetEarnRate(self):
        if self.bidderPrice <= 0 or self.bidderVolume <= 0:
            return 0

        oldBidder = float(self.bidderPrice * self.bidderVolume)
        curBidder = float(self.GetCurrentPrice() * self.bidderVolume)

        return ((curBidder / oldBidder) * 100)

    def GetRecentMoveAverage5Day(self):
        ohlcv = pyupbit.get_ohlcv(self.ticker)
        # 종가로 5일간의 이동평균 구하기
        ma5 = ohlcv["close"].rolling(5).mean()
        # 가장 최근의 이동평균 가져오기. -1은 현재가를 포함한 이동평균이므로 -2가 가장최근의 종가 이동평균이다.
        return ma5[-2]

    def GetTargetBuyPrice(self):
        ohlcv = pyupbit.get_ohlcv(self.ticker)
        yesterday_data = ohlcv.iloc[-2]

        today_open_price = yesterday_data["close"]
        yesterday_high_price = yesterday_data["high"]
        yesterday_low_price = yesterday_data["low"]

        targetBuyPrice = today_open_price + ((yesterday_high_price - yesterday_low_price) * 0.5)
        return targetBuyPrice

    def BuyFullTickerCoin(self):
        cashKRW = self.GetBalanceCash()
        # 지갑에 원화 잔액 자체가 없음
        if cashKRW is None:
            return

        # 잔액이 최소 트레이딩 금액보다 부족!
        if cashKRW <= TradeWorker_BullMarket_Upbit.MinTradePrice:
            return

        orderbook = pyupbit.get_orderbook(self.ticker)
        sellPrice = orderbook["orderbook_units"][0]["ask_price"]
        buyVolume = cashKRW/float(sellPrice)
        self.accountInfo.buy_limit_order(self.ticker, sellPrice, buyVolume)

        self.bidderPrice = sellPrice
        self.bidderVolume = buyVolume

        # 매수 시도 로그 남김
        buyTime = datetime.datetime.now().__str__()
        self.trade_logging(f"[{buyTime}] {sellPrice} 가격에 {buyVolume}개 매수시도. 총 매수금액 : {self.bidderPrice * self.bidderVolume}")

    def SellFullTickerCoin(self):
        cls = type(self)
        if not hasattr(cls, "accountInfo"):
            return

        curCoinAmount = self.GetBalanceTickerCoin()
        # 코인 자체를 보유하고 있지도 않음
        if curCoinAmount is None or curCoinAmount <= 0:
            return

        curCoinPrice = self.GetCurrentPrice()
        # 매도 금액이 최소 트레이딩 금액보다 부족!
        if curCoinPrice * curCoinAmount <= TradeWorker_BullMarket_Upbit.MinTradePrice:
            return

        self.accountInfo.sell_market_order(self.ticker, curCoinAmount)

        self.bidderPrice = 0
        self.bidderVolume = 0

        # 매도 시도 로그 남김
        sellTime = datetime.datetime.now().__str__()
        self.trade_logging(f"[{sellTime}] {curCoinPrice} 가격에 {curCoinAmount}개 매도시도. 총 매도금액 : {curCoinPrice * curCoinAmount}")


    # 업비트에서는 원화 마켓 은 호가별 주문 가격의 단위가 다르기 때문에 단위를 알려주는 함수
    def get_price_scale_tick_upbit(self, curPrice):
        if curPrice >= 2000000:
            return -3, 1000
        elif curPrice >= 1000000:
            return -2, 500
        elif curPrice >= 500000:
            return -2, 100
        elif curPrice >= 100000:
            return -1, 50
        elif curPrice >= 10000:
            return -1, 10
        elif curPrice >= 1000:
            return 0, 5
        elif curPrice >= 100:
            return 0, 1
        elif curPrice >= 10:
            return 1, 0.1
        elif curPrice >= 0:
            return 2, 0.01