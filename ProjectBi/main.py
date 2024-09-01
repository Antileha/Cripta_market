from binance.client import Client
import keys
import pandas as pd
import time

client = Client(keys.api_key, keys.api_secret) # создаем клиента binance

def top_coin():
    """
    Функция поска топовой монеты
    Возвращает топовую манету:return: string
    """
    all_tickers = pd.DataFrame(client.get_ticker()) # получаем все тикеры с биржы
    usdt = all_tickers[all_tickers.symbol.str.contains('USDT')] # выбираем все тикеры с символом USDT
    work = usdt[~((usdt.symbol.str.contains('UP')) | (usdt.symbol.str.contains('DOWN')))] # выбираем все тикеры работающие
    top_coin = work[work.priceChangePercent == work.priceChangePercent.max()] # сортирум по активности процентное изменение
    top_coin = top_coin.symbol.values[0] # выбираем первый
    return top_coin

def last_data(symbol, interval, lookback):
    """
    поиск последних изменений
    :param symbol:
    :param interval:
    :param lookback:
    :return:
    """
    frame = pd.DataFrame(client.get_historical_klines(symbol, interval,lookback + 'min ago UTC')) # получаем данные по тикеру (исторические)
    frame = frame.iloc[:,:6]    # берем первые шесть
    frame.columns = ['Time', 'Open', 'Hight', 'Close', 'Volume'] # пеперименовывем колонки
    frame = frame.set_index('Time') # сортируем по времени
    frame.index = pd.to_datetime(frame.index, unit='ms') # преобразуем дату в читаемый вид
    frame = frame.astype(float) # переводим данные в числовое значение
    return frame

def strategy(buy_amt, SL=0.985, Target=1.02, open_position=False):

    """
    :param buy_amt: -> кол-во монет или доллоров
    :param SL:
    :param Target:
    :param open_position:
    :return:
    """
    try:
        asset = top_coin()
        df = last_data(asset, '1m', '120')

    except:
        time.sleep(61)
        assed = top_coin()
        df = last_data(asset, '1m', '120')

    qty = round(buy_amt/df.Close.iloc[-1], 1) # выбираем кол-во монет

    if ((df.Close.pct_change() +1).cumprod()).iloc[-1] > 1: # если актив растет рапечатай
        print(asset) # печать актива
        print(df.Close.iloc[-1]) # печать последней цены
        print(qty) # распечатай объем quantity
        order = client.create_order(symbol=asset, side='BUY', type='MARKET', quantity=qty) # открыть ордер
        print(order)
        buyprice = float(order['fills'][0]['price'])  # цена открытия позиции
        open_position = True

        while open_position:
            try:
                df = last_data(asset, '1m', '2')
            except:
                print("Restart after 1 min")
                time.sleep(61)
                df = last_data(asset, '1m', '2')

                print(f'Price' + str(df.Close[-1]))
                print(f'Target' + str(buyprice * Target))
                print(f'Stop' + str(buyprice * SL))
                if df.Close[-1] <= buyprice * SL or df.Close[-1] >= buyprice * Target:
                    order = client.create_order(symbol=asset, side='SELL', type='MARKET', quantity=qty)  # открыть ордер
                    print(order)
                    break

        else:
            print("No find")
            time.sleep(20)

    while True:
        print(top_coin())
        strategy(1)







