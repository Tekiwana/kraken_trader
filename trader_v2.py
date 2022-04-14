import krakenex
from time import sleep
from datetime import datetime
import os
from pykrakenapi import KrakenAPI
import smtplib
import ssl
import colorama
from colorama import Fore as f


kraken = krakenex.API()
try:
    kraken.load_key("kraken.key")
except FileNotFoundError:
    print("Key file cannot be located.\nMake sure you keep the kraken.key file in the root directory.")
    input("\nPress 'ENTER' key to exit")
    os._exit(1)
kraken = KrakenAPI(kraken)


"""
Config:
Refresh rate: Time to sleep between 2 queries.
crypto_pair_list: List of crypto pairs, you want to trade.
"""
refresh_rate = 3600  # Seconds
four_month_trigger = -25  # percentage
three_day_trigger = -0.8  # percentage
price = 0.0
crypto_pair_list = [
    "AAVEGBP", "ADAGBP", "ALGOGBP", "ATOMGBP", "BCHGBP", "DOTGBP", "ENJGBP",
    "EWTGBP", "FILGBP", "FLOWGBP", "GHSTGBP", "KSMGBP", "LPTGBP", "LINKGBP",
    "LTCGBP", "MATICGBP", "MKRGBP", "OCEANGBP", "RARIGBP", "RENGBP", "SANDGBP",
    "SNXGBP", "ETHGBP", "XRPGBP", "XTZGBP", "XBTGBP", "XLMGBP"
    ]  # Tradable pair(s)
to_buy = {}
open_pos = {}
trading = False
colored_line = 0


def clear(): return os.system("cls")


def get_balance():
    """
    Returns the actual balance.
    Returns a Dictionary.
    Key : currency
    Value : amount
    """
    a = kraken.get_account_balance()
    for i in a:
        if float(a[i]) != 0:
            print(i, " : ", a[i])


def get_status():
    """
    Retuns Kraken system status in str.
    If status is not "online" than retry in 30 min.
    """
    status = kraken.get_system_status()[0]
    if status != "online":
        print("Kraken System Status : OFFLINE\n\n")
        print(get_time(), "Re-try in 30 min.")
        log = open("log.txt", "a")
        log_string = str(datetime.today().strftime("%d.%m.%y"))
        log_string += "\t" + str(get_time()) + "\tKraken server OFFLINE\n"
        log.write(log_string)
        log.close()
        sleep(3600)
        get_status()
    return status


def get_time():
    """
    Returns the current time HH:MM
    """
    return datetime.now().strftime("%H:%M")


def get_price(crypto_name):
    """
    Returns the current price of the given Crypto currencie.
    Parameters -
        crypto_name : String - Tradable asset pair.
    Return :
        Price : float
    """
    return float(kraken.get_ticker_information(crypto_name)["a"][0][0])


def get_percentage(crypto_name):
    """
    Return how much the price changed since the last known price in percentage.
    Parameters -
        crypto_name : String - Tradable asset pair.
    Return :
        pass
    """
    pass


def buy():
    """
    Get the key with the biggest value in to_buy{}, if its not already bought,
    buy it.

    *** - TEST : Simulating buy to log file.
    """
    if len(to_buy) > 0:
        for crypto in to_buy:
            #crypto_to_buy = max(to_buy, key=to_buy.get)
            if crypto not in open_pos:
                log = open("log.txt", "a")
                log_string = str(datetime.today().strftime("%d.%m.%y"))+"\t"
                log_string += str(get_time())+"\tBUY: "+crypto+"\tPrice: "
                log_string += str(to_buy[crypto])+"\n"
                log.write(log_string)
                log.close()
                open_pos[crypto] = to_buy[crypto]
                email(log_string)
        to_buy.clear()
        trading = True


def data_collection():
    pass


def data_sorter(crypto_name, data, price):
    """
    Calculate the price change in percentage.
    Parameters :
                crypto_name : String - Tradable asset pair.
                data : Json data
    Returns: percentage : float - price change
    """
    for d in data["result"]:
        if d != "last":
            crypto_name = d
    sum = 0.0
    counter = 0
    for i in data["result"][crypto_name]:
        sum += float(i[4])
        counter += 1
    average_price = float(sum/counter)
    percentage = price / average_price * 100 - 100
    return percentage


def calculate_average(crypto_name, price):
    """
    Get the 4 and 1 month OHLC data and pass it to data_sorter() func.
    if 4 month percentage smaller than -25% and 3 days perc. bigger than -0.8%,
    store the crypto name in to_buy{} dict.
    Return:
        four_month_percentage, one_month_percentage : float
    """
    sleep(1)
    four_month_data = kraken.get_ohlc_data(crypto_name, interval=240)
    sleep(1)
    four_month_percentage = data_sorter(crypto_name, four_month_data, price)
    three_day_data = kraken.get_ohlc_data(crypto_name, interval=5)
    sleep(1)
    three_day_percentage = data_sorter(crypto_name, three_day_data, price)
    if float(four_month_percentage) < four_month_trigger and float(three_day_percentage) > three_day_trigger:
        to_buy[crypto_name] = price
    return four_month_percentage, three_day_percentage


def email(message):
    print("Email is temporaly DISABLED")
#    port = 465
#    smtp_server = "smtp.gmail.com"
#    sender_email = "notification.crypto.trader@gmail.com"
#    receiver_email = ""
#    password = ""
#    message = """
#    Automatic message. DO NOT REPLY!
#    """+str(message)

#    context = ssl.create_default_context()
#    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
#        server.login(sender_email, password)
#        server.sendmail(sender_email, receiver_email, message)


def sell_mode():
    pass


if __name__ == "__main__":
    try:
        four_month_trigger = float(
            input("4 month deviation trigger % (default:-25): "))
        three_day_trigger = float(
            input("3 day deviation trigger % (default:-0.8): "))
        refresh_rate = int(input("Refresh rate (seconds) (default:3600): "))
    except ValueError:
        print("Expected a number... I will set the DEFAULT numbers.")
        four_month_trigger = -25.0
        three_day_trigger = -0.8
        refresh_rate = 3600
    print("\n\nYOUR BALANCE IS: ")
    print(get_balance(), "\n")

    while True:
        try:
            id_counter = 1
            print(f.RED + "Kraken Crypto Trader v0.2 TEST\n" + f.WHITE)
            setting_string = "Settings:\n\t4 month deviation trigger: "
            setting_string += str(four_month_trigger)+" %\n\t"
            setting_string += "3 day deviation trigger: " + \
                str(three_day_trigger)
            setting_string += " %\n\tRefresh rate: " + \
                str(refresh_rate)+" sec.\n\t"
            setting_string += "Open posistions can be found in :root\log.txt"
            setting_string += "\n\n"
            print(setting_string)
            print("Kraken System Status : ", get_status(), "\n")
            sleep(1)
            for crypto_name in crypto_pair_list:
                price = get_price(crypto_name)
                f_month_avg, t_day_avg = calculate_average(crypto_name, price)
                data_string = "[" + get_time() + "]" + "[Id:" + str(id_counter) + "]"
                if f_month_avg <= -25 and t_day_avg >= -0.8:
                    data_string += "[" + f.GREEN + crypto_name + f.WHITE + "]   "
                elif f_month_avg <= -25 or t_day_avg >= -0.8:
                    data_string += "[" + crypto_name + "]   "
                else:
                    data_string += "[" + f.RED + crypto_name + f.WHITE + "]   "
                data_string += "\t[Price: " + str(price)[:9] + "]  "
                if f_month_avg <= -25:
                    data_string += "\t[4 month change: " + f.GREEN + str(f_month_avg)[:5] + f.WHITE + "]"
                else:
                    data_string += "\t[4 month change: " + f.RED + str(f_month_avg)[:5] + f.WHITE + "]"
                if t_day_avg >= -0.8:
                    data_string += "\t[3 days change: " + f.GREEN + str(t_day_avg)[:5] + f.WHITE + "]"
                else:
                    data_string += "\t[3 days change: " + f.RED + str(t_day_avg)[:5] + f.WHITE + "]"
                print(data_string)
                id_counter += 1
            print(50*"_")
            buy()
            if trading == False:
                sleep(refresh_rate)
                clear()
            else:
                sell_mode()

        except BaseException as error:
            print("Error : {}".format(error))
            email("ERROR  "+str(error))
            sleep(60)

#01:35   10   FLOWGBP    Price:  6.9  Increase/Decrease:  -37.685552618642895
