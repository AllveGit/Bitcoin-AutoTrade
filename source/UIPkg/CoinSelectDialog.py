from select import select

# ========== Upbit ==========
import pyupbit
import TestPkg.BackTesting_Upbit
# ===========================

# ========= Binance =========
from binance.client import Client
# ===========================

import re

from PyQt5 import uic
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QDialog, QWidget, QListWidgetItem

form_coinselectdialog_class = uic.loadUiType("resource/dialog_coinselect.ui")[0]

class CoinSelectDialog(QDialog, QWidget, form_coinselectdialog_class):
    coinSelectedSignal = pyqtSignal(str, str)

    def __init__(self, marketType):
        super().__init__()

        self.setupUi(self)

        self.marketType = marketType

        self.createCoinList()

        # ===== 버튼 이벤트 연결 =====
        self.btn_SelectCoin.clicked.connect(self.onSelectCoinBtnClick)
        self.btn_BackTesting.clicked.connect(self.onBackTestingBtnClick)
        self.btn_Back.clicked.connect(self.onBackBtnClick)
        # ===========================

    def createCoinList(self):
        if self.marketType == "upbit":
            # KRW 시장만 취급
            tickers = pyupbit.get_tickers(fiat="KRW")

            # 리스트에 삽입
            for ticker in tickers:
                # TODO : 아이콘삽입까지? QListWidgetItem 생성자 맨앞에 QIcon넣으면 아이콘삽입됨
                listItem = QListWidgetItem(ticker.__str__())
                self.CoinList.addItem(listItem)
        elif self.marketType == "binance":
            binance = Client()
            tickers = binance.get_all_tickers()

            # USDT 시장만 취급
            tickers_usdt = []
            filter_usdt = re.compile(r'\w+USDT')
            for tickerInfo in tickers:
                ticker = tickerInfo["symbol"]
                if filter_usdt.match(ticker) and "UP" not in ticker and "DOWN" not in ticker: #레버리지토큰 필터링을 위함
                    tickers_usdt.append(ticker)

            # 리스트에 삽입
            for usdtTicker in tickers_usdt:
                listItem = QListWidgetItem(usdtTicker.__str__())
                self.CoinList.addItem(listItem)
        elif self.marketType == "bybit":
            pass
        else:
            self.close()
            return

    def onSelectCoinBtnClick(self):
        if len(self.CoinList.selectedItems()) <= 0:
            return

        selectCoin = self.CoinList.selectedItems()[0]
        if selectCoin is None:
            return

        self.close()
        self.coinSelectedSignal.emit(self.marketType, selectCoin.text())

    def onBackTestingBtnClick(self):
        if len(self.CoinList.selectedItems()) <= 0:
            return

        selectCoin = self.CoinList.selectedItems()[0]
        if selectCoin is None:
            return

        coinTicker = selectCoin.text()

        if self.marketType == "upbit":
            TestPkg.BackTesting_Upbit.MakeBackTestData(coinTicker)
        elif self.marketType == "binance":
            pass

    def onBackBtnClick(self):
        self.close()