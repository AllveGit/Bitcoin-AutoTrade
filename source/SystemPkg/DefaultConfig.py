import configparser

# Configs/DefaultConfig.ini의 정보를 불러오는 클래스
# Singleton 클래스임
class DefaultConfig(object):
    # 업비트 거래소 OpenAPI 정보 섹션
    section_acc_upbit = "account_upbit"

    # 바이낸스 거래소 OpenAPI 정보 섹션
    section_acc_binance = "account_binance"

    # 로그를 위한 카카오 OpenAPI 정보 섹션
    section_acc_kakao = "kakaotalk_logging"

    # 클래스의 객체를 생성할 때 호출되는 object 오버라이드 메소드
    def __new__(cls, *args, **kwargs):
        # 한번 이 클래스의 객체가 생성이 되었으면 _instance 속성이 생기도록 한다.
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)

        return cls._instance

    def __init__(self):
        cls = type(self)
        # 한번 이 클래스의 객체가 초기화 되었으면 _init 속성이 생기도록 한다.
        if hasattr(cls, "_init"):
            return

        cls._init = True

        config = configparser.ConfigParser()
        config.read("configs/DefaultConfig.ini")

        self.accInfo_upbit      = (config[DefaultConfig.section_acc_upbit]["accesskey"], config[DefaultConfig.section_acc_upbit]["secretkey"])
        self.accInfo_binance    = (config[DefaultConfig.section_acc_binance]["accesskey"], config[DefaultConfig.section_acc_binance]["secretkey"])
        self.accInfo_kakao      = config[DefaultConfig.section_acc_kakao]["restapikey"]

    def GetUpbitInfo(self):
        return self.accInfo_upbit

    def GetBinanceInfo(self):
        return self.accInfo_binance

    def GetKakaoInfo(self):
        return self.accInfo_kakao