# ===== 카카오톡 로깅 =====
import requests
import json
# ========================

from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QWidget
from UIPkg.OverViewWidget import OverViewWidget
from UIPkg.PriceChartWidget import PriceChartWidget
from UIPkg.OrderBookWidget import OrderBookWidget
from SystemPkg.KakaoLogWorker import KakaoLogWorker
from SystemPkg.TradeWorker_Upbit import TradeWorker_BullMarket_Upbit

form_coininfodialog_class = uic.loadUiType("resource/dialog_coininfo.ui")[0]

class CoinInfoDialog(QDialog, QWidget, form_coininfodialog_class):
    def __init__(self, marketType, ticker):
        super().__init__()

        self.setupUi(self)

        self.marketType = marketType
        self.ticker = ticker

        # 트레이딩 시스템 생성
        self.createTradeWorker()

        # 카카오톡 로그 시스템 생성
        self.createKakaoLogWorker()

        self.widget_CoinInfo.workStart(marketType, ticker)
        self.widget_CoinPriceChart.workStart(marketType, ticker)
        self.widget_CoinOrderBook.workStart(marketType, ticker)

        # ===== 버튼 이벤트 연결 =====
        self.btn_AutoTrading.clicked.connect(self.onAutoTradeBtnClick)
        self.btn_Back.clicked.connect(self.onBackBtnClick)
        # ===========================

    def closeEvent(self, event):
        if self.tradeWorker is not None:
            self.tradeWorker.close() 

        if self.kakaoLogWorker is not None:
            self.kakaoLogWorker.close()

        self.widget_CoinInfo.close()
        self.widget_CoinPriceChart.close()
        self.widget_CoinOrderBook.close()

    def createTradeWorker(self):
        if self.marketType == "upbit":
            self.tradeWorker = TradeWorker_BullMarket_Upbit(self.ticker)

        self.tradeWorker.tradelog_signal.connect(self.onAddTradeLog)
        self.tradeWorker.tradelog_kakao_signal.connect(self.onAddKakaotalkLog)

    def createKakaoLogWorker(self):
        self.kakaoLogWorker = KakaoLogWorker()
        self.daemon = True

    def onAutoTradeBtnClick(self):
        if self.tradeWorker.AutoTrading is not True:
            self.btn_AutoTrading.setText("자동트레이딩 종료")
            self.tradeWorker.start()
        else:
            self.btn_AutoTrading.setText("자동트레이딩 시작")
            self.tradeWorker.close()

    def onBackBtnClick(self):
        self.close()

    def onAddTradeLog(self, log):
        self.TradingLog.append(log)

    # 카카오톡으로 나한테 로그메시지를 보내는 함수
    def onAddKakaotalkLog(self, log):
        self.kakaoLogWorker.send_to_kakao(log)

            
