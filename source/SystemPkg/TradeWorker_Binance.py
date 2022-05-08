from SystemPkg.TradeWorker import TradeWorker_BullMarket
from SystemPkg.DefaultConfig import DefaultConfig

class TradeWorker_BullMarket_Binance(TradeWorker_BullMarket):
    # 바이낸스 USDT 이용
    BalanceType = "USDT"

    def __init__(self, ticker):
        super().__init__(ticker)

    def run(self):
        super().run(self)

    def close(self):
        super().close()