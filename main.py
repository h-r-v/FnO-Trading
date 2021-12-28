#---------------------------------CLI---------------------------------
sandbox = False #True if you want to use sandbox enviorment. False to use production enviorment.
get_access_only = False #True if you want to generate the OTP onlt. Flase if you want to execute the entire program.
access_code = "2762" #OTP

if sandbox==False:
    userid = "NT1945"
    password='BT121299@'
    access_token = "3bf7af61-77c2-3f2e-b1c1-f4f5cb909db3"
    consumer_key = "ay4bObamN3KHOPzZjmpA7g9YDJwa"
    host = 'https://tradeapi.kotaksecurities.com/apim'
else:
    userid = "1T068"
    password='login@1'
    access_token = "ebe9c833-26c1-3402-bf80-c457e76a4da3"
    consumer_key = "a0s3dcOM4JgVNn3pB7fdLBFkJ4Ea"
    host = 'https://sbx.kotaksecurities.com/apim'

#---------------------------------GENERATING OTP---------------------------------
from ks_api_client.ks_api import KSTradeApi

try:
    client = KSTradeApi(access_token = access_token, userid = userid, \
                    consumer_key = consumer_key, ip = "127.0.0.1", app_id = "DefaultApplication", host = host)
    client.login(password=password)
    print('OTP generated.')
except Exception as e:
    print('Could not generate OTP. Error: ', e)

#---------------------------------OTP verification---------------------------------
if get_access_only==True:
    exit()

if sandbox==True:
    client.session_2fa(access_code = '1111')
else:
    client.session_2fa(access_code = access_code)

#---------------------------------Get token list---------------------------------
from datetime import datetime
import requests
fno_url = 'https://preferred.kotaksecurities.com/security/production/TradeApiInstruments_FNO_'+datetime.now().strftime("%d_%m_%Y")+'.txt'
cash_url = 'https://preferred.kotaksecurities.com/security/production/TradeApiInstruments_CASH_'+datetime.now().strftime("%d_%m_%Y")+'.txt'

#fno_url = 'https://preferred.kotaksecurities.com/security/production/TradeApiInstruments_FNO_10_12_2021.txt'
#cash_url = 'https://preferred.kotaksecurities.com/security/production/TradeApiInstruments_CASH_10_12_2021.txt'

fno_tokens = requests.get(fno_url)
cash_tokens = requests.get(cash_url)

if fno_tokens.status_code!=200 or cash_tokens.status_code!=200:
    print('Could not get token data.')
    exit()
else:
    print('Token data accquired.')

fno_tokens = fno_tokens.text
cash_tokens = cash_tokens.text

fno_tokens = fno_tokens.split('\n')
fno_tokens = [i.strip().split('|') for i in fno_tokens]
cash_tokens = cash_tokens.split('\n')
cash_tokens = [i.strip().split('|') for i in cash_tokens]

if len(fno_tokens) <= 1 or len(cash_tokens) <= 1:
    assert True==False, "Token list not valid"
else:
    print('Token data successful.')

#initializing DataFrames
import pandas as pd

fno_df = pd.DataFrame( fno_tokens[1:], columns=fno_tokens[0])
cash_df = pd.DataFrame( cash_tokens[1:], columns=cash_tokens[0])

print("FnO DF shape: ",fno_df.shape)
print("Cash DF shape: ",cash_df.shape)

#---------------------------------BANKNIFTY TOKEN---------------------------------
banknifty_token = int(cash_df[cash_df.instrumentName=='NIFTY BANK'].instrumentToken.values[0])
print("BANK NIFTY TOKEN:",banknifty_token)

#---------------------------------Time loop---------------------------------
from datetime import datetime
from helper import *
import os

old_second = 70

#creating log dir
if not os.path.exists('logs'):
    os.mkdir('logs')

#creating log file
log = datetime.now().strftime("%m-%d-%Y")
log = open(f"logs/{log}.txt", "a")

#main loop execution time
_hour, _min, _sec = [int(i) for i in '14.54.00'.split('.')]

#first execution flags
firstafter930 = True
firstTL = True
firstat925 = True
firstat930 = True
firstat3 = True
firstat305 = True

while True:
    
    hour, minute, second = [int(i) for i in datetime.now().strftime("%H.%M.%S").split('.')]
    
    if( (old_second+3)%60==second or firstTL):

        #log and print time loop start
        if firstTL==True:
            log_info(log, 'Time loop started', 'sys_alert')
            firstTL=False

        #update time
        old_second=second
        
        #At 9:25am
        if(hour==_hour and minute==_min-1 and firstat925==True):

            #log and print start of 9:25am procedure
            log_info(log, 'Executing before 9:25am procedure', 'sys_alert')

            #get banknifty atm
            banknity_atm = get_atm(banknifty_token, client)
            
            #log and print strike price
            log_info(log,f"BNF ATM @{banknity_atm}",'strike_price')

            #get pe and ce token at that atm
            banknity_token_pe, banknity_token_ce = get_pe_ce_token(banknity_atm, fno_df)

            #initialize hit flags
            banknifty_ce_hit = False
            banknifty_pe_hit = False
            banknifty_ce_wrong = False
            banknifty_pe_wrong = False

            #log and print end of 9:25am procedure
            log_info(log, f"Before 9:25am procedure completed", 'sys_alert')
            firstat925 = False

        #At 9:30am
        if(hour==_hour and minute==_min and firstat930==True):
            
            #log and print start of 9:30am procedure
            log_info(log,'Executing at 9:30am procedure','sys_alert')
            
            #get ce and pe quote
            banknifty_ce_ltp_930 = get_quote(banknity_token_ce, client)
            banknifty_pe_ltp_930 = get_quote(banknity_token_pe, client)

            #log and print CE LTP @9:30am
            log_info(log, f'BNF {banknity_atm} CE 9:30 am LTP @{banknifty_ce_ltp_930}', 'ltp_alert')
            
            #log and print PE LTP @9:30am
            log_info(log, f'BNF {banknity_atm} PE 9:30 am LTP @{banknifty_pe_ltp_930}', 'ltp_alert')

            #get execution price
            banknifty_ce_ex = 0.9*banknifty_ce_ltp_930
            banknifty_pe_ex = 0.9*banknifty_pe_ltp_930

            #log and print CE execution price and stop loss
            log_info(log, f'BNF {banknity_atm} CE execution price set @{banknifty_ce_ex}', 'execution_price')
            log_info(log, f'BNF {banknity_atm} CE stop loss set @{1.25*banknifty_ce_ex}', 'stop_loss')
            
            #log and print PE execution price
            log_info(log, f'BNF {banknity_atm} PE execution price set @{banknifty_pe_ex}', 'execution_price')
            log_info(log, f'BNF {banknity_atm} PE stop loss set @{1.25*banknifty_pe_ex}', 'stop_loss')

            #log and print end of 9:30am procedure
            log_info(log, f'At 9:30am procedure completed', 'sys_alert')
            firstat930=False

        #After 9:30am
        if(hour>=_hour and minute>=_min):
            if firstafter930==True:
                #log and print start of after 9:30am procedure
                log_info(log, "Executing after 9:30am procedure", 'sys_alert')
                firstafter930 = False

            #Get LTP for CE and PE every second after 9:30am
            banknifty_ce_ltp = get_quote(banknity_token_ce, client)
            banknifty_pe_ltp = get_quote(banknity_token_pe, client)

            log_info(log, f'banknifty_ce_ltp @{banknifty_ce_ltp}','ltp_alert')
            log_info(log, f'banknifty_pe_ltp @{banknifty_pe_ltp}','ltp_alert')

            #sell ce when execution price is hit for the first time
            if (banknifty_ce_ltp<=banknifty_ce_ex and banknifty_ce_hit==False):
                log_info(log, f'SELL BNF {banknity_atm} CE executed @{banknifty_ce_ltp}', 'sell')
                #client.place_order(order_type = "MIS", instrument_token = banknity_token_ce, transaction_type = "SELL", quantity = 25, price = 0)
                banknifty_ce_hit = True

            #buy ce if reversal
            if (banknifty_ce_hit==True and banknifty_ce_ltp>=1.25*banknifty_ce_ex and banknifty_ce_wrong==False):
                log_info(log, f'BUY BNF {banknity_atm} CE executed @{banknifty_ce_ltp}', 'buy')
                #client.place_order(order_type = "MIS", instrument_token = banknity_token_ce, transaction_type = "BUY", quantity = 25, price = 0)
                banknifty_ce_wrong = True

            #sell pe when execution price is hit for the first time
            if (banknifty_pe_ltp<=banknifty_pe_ex and banknifty_pe_hit==False):
                log_info(log, f'SELL BNF {banknity_atm} PE executed @{banknifty_pe_ltp}', 'sell')
                #client.place_order(order_type = "MIS", instrument_token = banknity_token_pe, transaction_type = "SELL", quantity = 25, price = 0)
                banknifty_pe_hit = True

            #buy pe if reversal
            if (banknifty_pe_hit==True and banknifty_pe_ltp>=1.25*banknifty_pe_ex and banknifty_pe_wrong==False):
                log_info(log, f'BUY BNF {banknity_atm} PE executed @{banknifty_pe_ltp}', 'buy')
                #client.place_order(order_type = "MIS", instrument_token = banknity_token_pe, transaction_type = "BUY", quantity = 25, price = 0)
                banknifty_pe_wrong = True

            #At 3pm
            if(hour==15 and minute==0 and firstat3==True):
                #buy ce to square off
                if( banknifty_ce_hit==True and banknifty_ce_wrong==False ):
                    log_info(log, f'SQUAREOFF BUY BNF {banknity_atm} CE executed @{banknifty_ce_ltp}', 'squareoff')
                    #client.place_order(order_type = "MIS", instrument_token = banknity_token_ce, transaction_type = "BUY", quantity = 25, price = 0)

                #buy pe to square off
                if( banknifty_pe_hit==True and banknifty_pe_wrong==False ):
                    log_info(log, f'SQUAREOFF BUY BNF {banknity_atm} PE executed @{banknifty_pe_ltp}', 'squareoff')
                    #client.place_order(order_type = "MIS", instrument_token = banknity_token_pe, transaction_type = "BUY", quantity = 25, price = 0)  

                firstat3 = False
            
            #At 3:05pm
            if(hour==15 and minute==5 and firstat305==True):
                #log and print end of at 3:05pm procedure
                log_info(log, 'At 3:05pm procedure completed', 'sys_alert')
                log.close()
                firstat305==False
                exit()          

        

        
