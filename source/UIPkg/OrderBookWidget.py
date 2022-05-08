from email import header
import sys
import time

# ========== Upbit ==========
import pyupbit
# ===========================

# ========= Binance =========
from binance.client import Client
# ===========================

from PyQt5 import uic, QtGui
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import QWidget, QTableWidgetItem, QProgressBar

class OrderBookWorker(QThread):
    curOrderBookSignal_upbit = pyqtSignal(list)
    curOrderBookSignal_binance = pyqtSignal(list, list)

    def __init__(self, marketType, ticker):
        super().__init__()

        self.marketType = marketType
        self.ticker = ticker
        self.refreshInterval = 1
        self.alive = True

    def close(self):
        self.alive = False

    def run(self):
        if self.marketType == "upbit":
            self.run_upbit()
        elif self.marketType == "binance":
            self.run_binance()

    def run_upbit(self):
        while self.alive:
            orderBookDatas = pyupbit.get_orderbook(self.ticker)  
            orderBookDatas = orderBookDatas["orderbook_units"]
            orderBookDatas = orderBookDatas[:10]
            self.curOrderBookSignal_upbit.emit(orderBookDatas)
            time.sleep(self.refreshInterval)

    def run_binance(self):
        # todo : ini파일로 accesskey 및 secretkey 불러와야함

        binanceCli = Client()
        while self.alive:
            orderBookDatas = binanceCli.get_order_book(symbol=self.ticker)
            orderBookAskDatas = orderBookDatas["asks"][:10]
            orderBookBidDatas = orderBookDatas["bids"][:10]
            self.curOrderBookSignal_binance.emit(orderBookAskDatas, orderBookBidDatas)
            time.sleep(self.refreshInterval)




class OrderBookWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        uic.loadUi("resource/widget_orderbook.ui", self)

    def closeEvent(self, event):
        if self.obw is not None:
            self.obw.close() 

    def workStart(self, marketType="upbit", ticker="KRW-BTC"):
        self.marketType = marketType
        self.ticker = ticker

        for i in range(self.tableBids.rowCount()):
            item0 = QTableWidgetItem(str(""))
            item0.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            item0.setForeground(QtGui.QColor(255,255,255))
            self.tableAsks.setItem(i, 0, item0)

            item1 = QTableWidgetItem(str(""))
            item1.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            item1.setForeground(QtGui.QColor(255,255,255))
            self.tableAsks.setItem(i, 1, item1)

            item2 = QProgressBar(self.tableAsks)
            item2.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

            self.tableAsks.setCellWidget(i, 2, item2)

            if (i + 1) % 2 == 0:
                item0.setBackground(QtGui.QColor(44, 43, 44))
                item1.setBackground(QtGui.QColor(44, 43, 44))
                item2.setStyleSheet("""
                    QProgressBar {background-color : rgba(44, 43, 44, 100%);border : 1}
                    QProgressBar::Chunk {background-color : rgba(255, 0, 68, 75%);border : 1}
                """)
            else:
                item0.setBackground(QtGui.QColor(25, 25, 25))
                item1.setBackground(QtGui.QColor(25, 25, 25))
                item2.setStyleSheet("""
                    QProgressBar {background-color : rgba(25, 25, 25, 100%);border : 1}
                    QProgressBar::Chunk {background-color : rgba(255, 0, 68, 75%);border : 1}
                """)

            # 매수 호가
            item0 = QTableWidgetItem(str(""))
            item0.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            item0.setForeground(QtGui.QColor(255,255,255))
            self.tableBids.setItem(i, 0, item0)

            item1 = QTableWidgetItem(str(""))
            item1.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            item1.setForeground(QtGui.QColor(255,255,255))
            self.tableBids.setItem(i, 1, item1)

            item2 = QProgressBar(self.tableBids)
            item2.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

            self.tableBids.setCellWidget(i, 2, item2)

            if (i + 1) % 2 == 0:
                item0.setBackground(QtGui.QColor(44, 43, 44))
                item1.setBackground(QtGui.QColor(44, 43, 44))
                item2.setStyleSheet("""
                    QProgressBar {background-color : rgba(44, 43, 44, 100%);border : 1}
                    QProgressBar::Chunk {background-color : rgba(0, 255, 128, 75%);border : 1}
                """)
            else:
                item0.setBackground(QtGui.QColor(25, 25, 25))
                item1.setBackground(QtGui.QColor(25, 25, 25))
                item2.setStyleSheet("""
                    QProgressBar {background-color : rgba(25, 25, 25, 100%);border : 1}
                    QProgressBar::Chunk {background-color : rgba(0, 255, 128, 75%);border : 1}
                """)
            

        # OrderBookData를 갱신하는 쓰레드 시작
        self.obw = OrderBookWorker(self.marketType, self.ticker)
        self.obw.curOrderBookSignal_upbit.connect(self.updateOrderBookData_upbit)
        self.obw.curOrderBookSignal_binance.connect(self.updateOrderBookData_binance)
        self.obw.start()

    def updateOrderBookData_upbit(self, data):
        tradingAskValues = []
        for v in data[::-1]:
            tradingAskValues.append(int(v["ask_price"] * v["ask_size"]))

        tradingBidValues = []
        for v in data:
            tradingBidValues.append(int(v["bid_price"] * v["bid_size"]))

        maxTradingValue = max(tradingBidValues + tradingAskValues)

        for i, v in enumerate(data[::-1]):
            item0 = self.tableAsks.item(i, 0)
            item0.setText(f"{v['ask_price']:,}")
            item1 = self.tableAsks.item(i, 1)
            item1.setText(f"{v['ask_size']:,}")
            item2 = self.tableAsks.cellWidget(i, 2)
            item2.setRange(0, maxTradingValue)
            item2.setFormat(f"{tradingAskValues[i]:,}")
            item2.setValue(tradingAskValues[i])

        for i, v in enumerate(data):
            item0 = self.tableBids.item(i, 0)
            item0.setText(f"{v['bid_price']:,}")
            item1 = self.tableBids.item(i, 1)
            item1.setText(f"{v['bid_size']:,}")
            item2 = self.tableBids.cellWidget(i, 2)
            item2.setRange(0, maxTradingValue)
            item2.setFormat(f"{tradingBidValues[i]:,}")
            item2.setValue(tradingBidValues[i])

    def updateOrderBookData_binance(self, askDatas, bidDatas):
        tradingAskValues = []
        for v in askDatas[::-1]:
            tradingAskValues.append(int(float(v[0]) * float(v[1])))

        tradingBidValues = []
        for v in bidDatas:
            tradingBidValues.append(int(float(v[0]) * float(v[1])))

        maxTradingValue = max(tradingBidValues + tradingAskValues)

        for i, v in enumerate(askDatas[::-1]):
            item0 = self.tableAsks.item(i, 0)
            item0.setText(f"{float(v[0]):,}")
            item1 = self.tableAsks.item(i, 1)
            item1.setText(f"{float(v[1]):,}")
            item2 = self.tableAsks.cellWidget(i, 2)
            item2.setRange(0, maxTradingValue)
            item2.setFormat(f"{tradingAskValues[i]:,}")
            item2.setValue(tradingAskValues[i])

        for i, v in enumerate(bidDatas):
            item0 = self.tableBids.item(i, 0)
            item0.setText(f"{float(v[0]):,}")
            item1 = self.tableBids.item(i, 1)
            item1.setText(f"{float(v[1]):,}")
            item2 = self.tableBids.cellWidget(i, 2)
            item2.setRange(0, maxTradingValue)
            item2.setFormat(f"{tradingBidValues[i]:,}")
            item2.setValue(tradingBidValues[i])
