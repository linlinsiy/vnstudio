from time import sleep
from datetime import datetime, time

from vnpy.event import EventEngine
from vnpy.trader.engine import MainEngine

from vnpy.gateway.ctp import CtpGateway

from vnpy.gateway.sina import SinaGateway


from vnpy.trader.ui import MainWindow, create_qapp
from vnpy.app.cta_strategy import CtaStrategyApp
from vnpy.app.cta_backtester import CtaBacktesterApp
from vnpy.app.csv_loader import CsvLoaderApp
from vnpy.app.data_recorder import DataRecorderApp
from vnpy.app.data_recorder.engine import EVENT_RECORDER_LOG




ctp_setting = {
    "用户名": "666857",
    "密码": "690522",
    "经纪商代码": "66666",
    "交易服务器": "tcp://180.169.101.177:43205",
    "行情服务器": "tcp://180.169.101.177:43213",
    "产品名称": "client_itrader_1.1.1.1",
    "授权编码": "6BQKCO5WBK213AXI",
    "产品信息": ""
}

import urllib.parse
import urllib.request

import requests,json



def main():
    """运行函数"""
    print('-' * 20)

    x = 3251.6
    lst_decimal = str(x).split(".")
    ll = len(lst_decimal)
    if len(lst_decimal) > 1:
        decimal_places = len(lst_decimal[1])
        min_unit = 1/10**decimal_places
    else:
        min_unit = 1


    qapp = create_qapp()

    event_engine = EventEngine()
    main_engine = MainEngine(event_engine)
    main_engine.add_gateway(CtpGateway)

    main_engine.add_gateway(SinaGateway)

	
    main_engine.add_app(CtaStrategyApp)
    main_engine.add_app(CtaBacktesterApp)
    main_engine.add_app(CsvLoaderApp)
    main_engine.add_app(DataRecorderApp)

	
    main_window = MainWindow(main_engine, event_engine)
    main_window.showMaximized()

    qapp.exec()

if __name__ == '__main__':

#    data = bytes(urllib.parse.urlencode({'symbol':'i2009','XDEBUG_SESSION_START':15926}), encoding='utf8')
#    response = urllib.request.urlopen('http://127.0.0.1/aiexpect/public/v1/deliverthinkingdetail', data=data)

    """
    url = 'http://127.0.0.1/aiexpect/public/v1/deliverthinkingdetail'
    symbol = 'p2009'
    dt = '2020-04-09 14:22:23'
    calMom = 20
    calThre = 7.90
    xDebug = 19856
    data = {'symbol':symbol,'datetime':dt,'calMomentum':calMom,'calThreshold':calThre,'XDEBUG_SESSION_START':xDebug}
    r = requests.post(url, data)
    """

    """
    url = 'http://127.0.0.1/aiexpect/public/v1/deliverlastprice'
    symbol = 'i2009'
    dt = '2020-04-09 14:22:23'
    lastprice = 709
    xDebug = 17430
    onlyone = False

    if onlyone:
        url = 'http://127.0.0.1/aiexpect/public/v1/deliverlastprice'
        send_data = {'symbol': symbol, 'datetime': dt, 'lastprice': lastprice,'XDEBUG_SESSION_START': xDebug}
    else:
        url = 'http://127.0.0.1/aiexpect/public/v1/delivermultilastprice'
        priceForAll = [{'symbol': symbol,  'lastprice': lastprice},{'symbol': 'sc2009',  'lastprice': 305.2}]
        data_json = json.dumps(priceForAll)
        send_data = {'priceforall': data_json,'datetime': dt,'XDEBUG_SESSION_START': xDebug}
    try:
        r = requests.post(url, send_data,  timeout=0.1)

        print(r.text)
        a = json.loads(r.text)
    except Exception as e:
        a = 2
    
    """

    main()