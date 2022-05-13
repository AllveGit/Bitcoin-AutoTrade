import sys
import time
import asyncio
import websockets
import json
import multiprocessing as mp

# ========== Upbit ==========
from pyupbit import WebSocketManager
# ===========================

# ========= Binance =========
from binance import AsyncClient, BinanceSocketManager
# ===========================

from PyQt5 import uic
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import QWidget

class OverViewWorker(QThread):
    overviewDataSignal = pyqtSignal(str, float, float, float, float, float, float, str, float)

    def __init__(self, marketType, ticker):
        super().__init__()

        self.marketType = marketType
        self.ticker = ticker
        self.tickerName = f"{self.marketType}_{self.ticker}"
        self.refreshInterval = 1

        self.alive = True

    def close(self):
        self.alive = False

    def run(self):
        if self.marketType == "upbit":
            asyncio.run(self.run_upbit())
        elif self.marketType == "binance":
            asyncio.run(self.run_binance())

    # upbit용 갱신함수
    async def run_upbit(self):
        url = "wss://api.upbit.com/websocket/v1"
        async with websockets.connect(url, ping_interval=None) as websocket:
            subscribe_fmt = [ 
                {"ticket":"test"},
                {
                    "type": "ticker",
                    "codes":[self.ticker],
                    "isOnlyRealtime": True
                },
                {"format":"SIMPLE"}
            ]

            subscribe_data = json.dumps(subscribe_fmt)
            await websocket.send(subscribe_data)

            while self.alive:
                webData = await websocket.recv()
                webData = json.loads(webData)

                self.overviewDataSignal.emit(self.tickerName,
                                             float(webData["tp"]),
                                             float(webData["scr"] * 100),
                                             float(webData["atv24h"]),
                                             int  (webData["hp"]),
                                             float(webData["atp24h"]),
                                             int  (webData["lp"]),
                                             str  (webData["dd"]),
                                             int  (webData["pcp"]))

                time.sleep(self.refreshInterval)


        # wm = WebSocketManager("ticker", [self.ticker])
        # while self.alive:
        #     webData = wm.get()
        #     # self.overviewDataSignal.emit(self.tickerName,
        #     #                              float(webData["trade_price"]),
        #     #                              float(webData["signed_change_rate"] * 100),
        #     #                              float(webData["acc_trade_volume_24h"]),
        #     #                              int  (webData["high_price"]),
        #     #                              float(webData["acc_trade_price_24h"]),
        #     #                              int  (webData["low_price"]),
        #     #                              str  (webData["delisting_date"]),
        #     #                              int  (webData["prev_closing_price"]))

        #     time.sleep(self.refreshInterval)

        # wm.terminate()

    # binance용 갱신함수
    async def run_binance(self):
        binanceAsyncCli = await AsyncClient.create()
        binanceSocketMgr = BinanceSocketManager(binanceAsyncCli, user_timeout=60)
        tickerSocket = binanceSocketMgr.symbol_ticker_socket(self.ticker) 

        async with tickerSocket as tickerSocketConn:
            while self.alive:
                webData = await tickerSocket.recv() 
                self.overviewDataSignal.emit(self.tickerName,
                                             float(webData['c']),
                                             float(webData['P']),
                                             float(webData['v']),
                                             float(webData['h']),
                                             float(webData['v']) * float(webData['w']),
                                             float(webData['l']),
                                             None,
                                             float(webData['x']))

                time.sleep(self.refreshInterval)

        await binanceAsyncCli.close_connection()
        
class OverViewWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        uic.loadUi("resource/widget_overview.ui", self)

        self.setStyleSheet("background-color:rgba(44, 43, 44, 100%);border : 1")

    def closeEvent(self, event):
        if self.ovw is not None:
            self.ovw.close()

    def workStart(self, marketType="upbit", ticker="KRW-BTC"):
        self.ticker = ticker

        self.monetaryUnit = '₩' if marketType == "upbit" else '$'
        self.tradeUnit = ticker if marketType != "upbit" else ticker.split('-')[1]

        self.ovw = OverViewWorker(marketType, ticker)
        self.ovw.overviewDataSignal.connect(self.updateOverViewData)
        self.ovw.start()

    def updateOverViewData(self, ticker, curPrice, chgRate, volume, highPrice, value, lowPrice, delistingDate, prevClosePrice):
        self.label_TickerName.setText(ticker)
        self.label_CurPrice.setText(f"{curPrice:,}{self.monetaryUnit}")
        self.label_ChangeRate.setText(f"{chgRate:+.2f}%")
        self.label_VolumeValue.setText(f"{volume:.4f}개")
        self.label_HighPriceValue.setText(f"{highPrice:,}")
        self.label_TradeAmountValue.setText(f"{value/100000000:,.1f}억 {self.monetaryUnit}")
        self.label_LowPriceValue.setText(f"{lowPrice:,}")
        self.label_DelistingDateValue.setText(delistingDate)
        self.label_EndPriceValue.setText(f"{prevClosePrice:,}")