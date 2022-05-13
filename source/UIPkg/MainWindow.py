from pickle import TRUE
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow
from UIPkg.CoinInfoDialog import CoinInfoDialog
from UIPkg.CoinSelectDialog import CoinSelectDialog

form_mainwindow_class = uic.loadUiType("resource/window_main.ui")[0]

class MainWindow(QMainWindow, form_mainwindow_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # ===== 버튼 이벤트 연결 =====
        self.btn_Market_UpBit.clicked.connect(self.onUpbitMarketBtnClick)
        self.btn_Market_Binance.clicked.connect(self.onBinanceMarketBtnClick)
        self.btn_Market_ByBit.clicked.connect(self.onBybitMarketBtnClick)
        self.btn_Market_Bithumb.clicked.connect(self.onBithumbMarketBtnClick)
        # ===========================

    def CreateCoinSelectDialog(self, marketType):
        self.hide()
        self.coinSelectDialog = CoinSelectDialog(marketType)
        self.coinSelectDialog.coinSelectedSignal.connect(self.CreateCoinInfoDialog)
        self.coinSelectDialog.exec()
        self.show()

    def CreateCoinInfoDialog(self, marketType, ticker):
        self.hide()
        self.coinInfoDialog = CoinInfoDialog(marketType, ticker)
        self.coinInfoDialog.exec()
        self.show()
        
    def onUpbitMarketBtnClick(self):
        self.CreateCoinSelectDialog("upbit")

    def onBinanceMarketBtnClick(self):
        self.CreateCoinSelectDialog("binance")

    def onBybitMarketBtnClick(self):
        pass

    def onBithumbMarketBtnClick(self):
        pass