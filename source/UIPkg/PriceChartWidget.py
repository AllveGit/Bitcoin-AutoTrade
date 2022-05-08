import sys
import time

# ========== Upbit ==========
import pyupbit
# ===========================

# ========= Binance =========
from binance.client import Client
# ===========================

from PyQt5 import uic, QtGui
from PyQt5.QtCore import Qt, QDateTime, QThread, pyqtSignal
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtChart import QLineSeries, QChart, QValueAxis, QDateTimeAxis

class PriceChartWorker(QThread):
    curPriceSignal = pyqtSignal(float)

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
            curPrice = pyupbit.get_current_price(self.ticker)
            self.curPriceSignal.emit(curPrice)
            time.sleep(self.refreshInterval)

    def run_binance(self):
        # todo : ini파일로 accesskey 및 secretkey 불러와야함

        binanceCli = Client()
        while self.alive:
            curPrice = float(binanceCli.get_symbol_ticker(symbol=self.ticker)["price"])
            self.curPriceSignal.emit(curPrice)
            time.sleep(self.refreshInterval)

class PriceChartWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        uic.loadUi("resource/widget_pricechart.ui", self)
        
        self.viewLimit = 128

        self.priceData = QLineSeries()
        self.priceChart = QChart()
        self.priceChart.addSeries(self.priceData)

        # 범례 제거
        self.priceChart.legend().hide()
        self.priceChart.layout().setContentsMargins(0,0,0,0) 

        # 선 안티엘리어싱
        self.priceView.setRenderHints(QPainter.Antialiasing)

        # 색상 설정
        self.priceChart.setBackgroundBrush(QColor("PremiumDark"))

        # 축 설정
        axisX = QDateTimeAxis()
        axisX.setFormat("hh:mm:ss")
        axisX.setTickCount(4)
        dt = QDateTime.currentDateTime()
        axisX.setRange(dt, dt.addSecs(self.viewLimit))

        axisY = QValueAxis()
        axisY.setVisible(False)

        self.priceChart.addAxis(axisX, Qt.AlignBottom)
        self.priceChart.addAxis(axisY, Qt.AlignRight)
        self.priceData.attachAxis(axisX)
        self.priceData.attachAxis(axisY)

        self.priceView.setChart(self.priceChart)

    def closeEvent(self, event):
        if self.pcw is not None:
            self.pcw.close()

    def workStart(self, marketType="upbit", ticker="KRW-BTC"):
        self.marketType = marketType
        self.ticker = ticker

        self.pcw = PriceChartWorker(marketType, ticker)
        self.pcw.curPriceSignal.connect(self.appendPriceData)
        self.pcw.start()

    def appendPriceData(self, curPrice):
        if len(self.priceData) == self.viewLimit:
            self.priceData.remove(0)

        dt = QDateTime.currentDateTime()
        self.priceData.append(dt.toMSecsSinceEpoch(), curPrice)
        self.updatePriceChartAxis()

    def updatePriceChartAxis(self):
        pvs = self.priceData.pointsVector()

        dtStart = QDateTime.fromMSecsSinceEpoch(int(pvs[0].x()))
        if len(self.priceData) == self.viewLimit :
            dtLast = QDateTime.fromMSecsSinceEpoch(int(pvs[-1].x()))
        else:
            dtLast = dtStart.addSecs(self.viewLimit)
          
        ax = self.priceChart.axisX()
        ax.setRange(dtStart, dtLast)

        ay = self.priceChart.axisY()
        dataY = [v.y() for v in pvs]
        ay.setRange(min(dataY), max(dataY))