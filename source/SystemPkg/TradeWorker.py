import time
import datetime
from PyQt5.QtCore import Qt, QThread, pyqtSignal

class TradeWorker_BullMarket(QThread):
    tradelog_signal         = pyqtSignal(str)
    tradelog_kakao_signal   = pyqtSignal(str)

    def __init__(self, ticker):
        super().__init__()

        self.ticker = ticker
        self.AutoTrading = False

        # 체결가, 수량
        self.bidderPrice = 0
        self.bidderVolume = 0

        # 30초마다 리프레시
        self.refreshInterval = 30

    # 실제 로직이 돌아갈 함수
    def run(self):
        now = datetime.datetime.now()
        # 현재일에서 1시간을 더한만큼의 시간
        nextHourTime = now + datetime.timedelta(seconds=3600)
        # 현재일에서 1일을 더한만큼의 시간
        nextDayTime = datetime.datetime(now.year, now.month, now.day) + datetime.timedelta(days=1)
        # 최근 5일간의 이동평균
        recentMA5 = self.GetRecentMoveAverage5Day()
        # 매수 목표가 설정
        targetBuyPrice = self.GetTargetBuyPrice()

        self.trade_logging("""===== 자동 트레이딩 시작! =====
        [5일 종가 이동평균가] : %f
        [매수 목표가] : %f
        """ % (recentMA5, targetBuyPrice))

        self.AutoTrading = True
        while self.AutoTrading:
            try:
                now = datetime.datetime.now()
                # 하루가 지나면 목표가 갱신 및 풀매도
                if nextDayTime < now < nextDayTime + datetime.timedelta(seconds=60):
                    nextDayTime = datetime.datetime(now.year, now.month, now.day) + datetime.timedelta(days=1)
                    recentMA5 = self.GetRecentMoveAverage5Day()
                    targetBuyPrice = self.GetTargetBuyPrice()

                    self.SellFullTickerCoin()

                    self.trade_logging("""===== 하루가 지나 목표가 갱신 및 전량 매도합니다. =====
                    [5일 종가 이동평균가] : %f
                    [매수 목표가] : %f
                    """ % (recentMA5, targetBuyPrice))

                # 1시간이 지날때마다 수익률 로그
                if nextHourTime < now < nextHourTime + datetime.timedelta(seconds=60):
                    nextHourTime = now + datetime.timedelta(seconds=3600)

                    earnRate = self.GetEarnRate()
                    if earnRate != 0:
                        self.trade_logging(f"자동트레이딩 결과 : 현재 수익률은 {earnRate}%입니다.")

                curPrice = self.GetCurrentPrice()
                # 지금이 상승장인가?
                isBullMarket = curPrice > recentMA5
                # 현재 가격이 목표가보다 높은가?
                isTargetPrice = curPrice > targetBuyPrice

                if isBullMarket and isTargetPrice:
                    self.BuyFullTickerCoin()
            except:
                self.trade_logging("예외가 발생하여 자동 트레이딩을 종료합니다.")
                self.close()

            time.sleep(self.refreshInterval)

    # 자동 트레이딩을 종료하는 함수
    def close(self):
        self.AutoTrading = False
        self.SellFullTickerCoin()
        self.trade_logging("===== 자동 트레이딩 종료! =====")

    # 현재 UI 텍스트 필드 및 카카오톡으로 로그쓰기
    def trade_logging(self, log):
        self.tradelog_signal.emit(log)
        self.tradelog_kakao_signal.emit(log)

    # 달러 혹은 원화가 얼마나 보유하고 있는지 확인하는 함수
    def GetBalanceCash(self):
        raise NotImplementedError

    # 현재 보유하고 있는 티커의 코인을 보유하고 있는지 확인하는 함수
    def GetBalanceTickerCoin(self):
        raise NotImplementedError

    # 현재가를 구하는 함수
    def GetCurrentPrice(self):
        raise NotImplementedError

    # 현재 수익률을 가져오는 함수
    def GetEarnRate(self):
        raise NotImplementedError

    # 가장 최근 5일간의 이동평균을 구하는 함수
    def GetRecentMoveAverage5Day(self):
        raise NotImplementedError

    # 매수 목표가를 구하는 함수
    def GetTargetBuyPrice(self):
        raise NotImplementedError

    # 티커의 코인을 보유하고 있는 재화로 풀매수하는 함수 
    def BuyFullTickerCoin(self):
        raise NotImplementedError

    # 티커의 코인을 보유하고 있는만큼 풀매도하는 함수
    def SellFullTickerCoin(self):
        raise NotImplementedError
