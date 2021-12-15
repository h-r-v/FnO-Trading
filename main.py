#---------------------------------CLI---------------------------------
sandbox = False
get_access_only = True
access_code = "1111"

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

if fno_tokens.status_code!=200 or cash_tokens!=200:
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

print("FnO DF shape: ",fno_df.shape())
print("Cash DF shape: ",cash_df.shape())

#---------------------------------BANKNIFTY TOKEN---------------------------------
banknifty_token = int(cash_df[cash_df.instrumentName=='NIFTY BANK'].instrumentToken.values[0])
print("BANK NIFTY TOKEN:",banknifty_token)

#---------------------------------Time loop---------------------------------
from datetime import datetime
from helper import *
import os

old_second = 70

#creating log dir
if not os.path.exists('log'):
    os.mkdir('logs')

log = datetime.now().strftime("%m-%d-%Y")
log = open(f"logs/{log}.txt", "a")

while True:
    
    hour, minute, second = [int(i) for i in datetime.now().strftime("%H.%M.%S").split('.')]
    
    if(old_second!=second):
        print(hour,minute,second)

        #update time
        old_second=second
        
        #Before 9:30am
        if(hour==9 and minute==29 and int(second)==58):
            print("Executing before 9:30am procedure.")
            #get banknifty atm
            banknity_atm = get_atm(banknifty_token, client)
            
            #get pe and ce token at that atm
            banknity_token_pe, banknity_token_ce = get_pe_ce_token(banknity_atm, fno_df)

            #initialize hit flags
            banknifty_ce_hit = False
            banknifty_pe_hit = False
            banknifty_ce_wrong = False
            banknifty_pe_wrong = False

        #At 9:30am
        if(hour==9 and minute==30 and int(second)==0):
            print("Executing at 9:30am procedure.")
            #get ce and pe quote
            banknifty_ce_ltp_930 = get_quote(banknity_token_ce, client)
            banknifty_pe_ltp_930 = get_quote(banknity_token_pe, client)

            banknifty_ce_ex = 0.9*banknifty_ce_ltp_930
            banknifty_pe_ex = 0.9*banknifty_pe_ltp_930
        
        print("Executing after 9:30am procedure.")
        #After 9:30am
        if(hour>=9 and minute>=30):
            banknifty_ce_ltp = get_quote(banknity_token_ce, client)
            banknifty_pe_ltp = get_quote(banknity_token_pe, client)

            if (banknifty_ce_ltp<=banknifty_ce_ex and banknifty_ce_hit==False):
                #sell ce
                log.write(f'SELL BNF {banknity_atm} CE executed @{hour}:{minute}:{second}\n')
                print(f'SELL BNF {banknity_atm} CE executed @{hour}:{minute}:{second}')
                client.place_order(order_type = "MIS", instrument_token = banknity_token_ce, transaction_type = "SELL", quantity = 25, price = 0)
                banknifty_ce_hit = True

            if (banknifty_ce_hit==True and banknifty_ce_ltp>=1.25*banknifty_ce_ex):
                #buy ce
                log.write(f'BUY BNF {banknity_atm} CE executed @{hour}:{minute}:{second}\n')
                print(f'BUY BNF {banknity_atm} CE executed @{hour}:{minute}:{second}')
                client.place_order(order_type = "MIS", instrument_token = banknity_token_ce, transaction_type = "BUY", quantity = 25, price = 0)
                banknifty_ce_wrong = True

            if (banknifty_pe_ltp<=banknifty_pe_ex and banknifty_pe_hit==False):
                #sell pe
                log.write(f'SELL BNF {banknity_atm} PE executed @{hour}:{minute}:{second}')
                print(f'SELL BNF {banknity_atm} PE executed @{hour}:{minute}:{second}')
                client.place_order(order_type = "MIS", instrument_token = banknity_token_pe, transaction_type = "SELL", quantity = 25, price = 0)
                banknifty_pe_hit = True

            if (banknifty_pe_hit==True and banknifty_pe_ltp>=1.25*banknifty_pe_ex):
                #buy pe
                log.write(f'BUY BNF {banknity_atm} PE executed @{hour}:{minute}:{second}')
                print(f'BUY BNF {banknity_atm} PE executed @{hour}:{minute}:{second}')
                client.place_order(order_type = "MIS", instrument_token = banknity_token_pe, transaction_type = "BUY", quantity = 25, price = 0)
                banknifty_pe_wrong = True

            #At 3pm
            if(hour==15 and minute==0 and int(second)==0):
                if( banknifty_ce_hit==True and banknifty_ce_wrong==False ):
                    #buy ce
                    log.write(f'BUY BNF {banknity_atm} CE executed @{hour}:{minute}:{second}')
                    print(f'BUY BNF {banknity_atm} CE executed @{hour}:{minute}:{second}')
                    client.place_order(order_type = "MIS", instrument_token = banknity_token_ce, transaction_type = "BUY", quantity = 25, price = 0)

                if( banknifty_pe_hit==True and banknifty_pe_wrong==False ):
                    #buy pe
                    log.write(f'BUY BNF {banknity_atm} CE executed @{hour}:{minute}:{second}')
                    print(f'BUY BNF {banknity_atm} PE executed @{hour}:{minute}:{second}')
                    client.place_order(order_type = "MIS", instrument_token = banknity_token_pe, transaction_type = "BUY", quantity = 25, price = 0)  
            
            #At 3:05pm
            if(hour==15 and minute==5 and int(second)==0):
                log.close()
                exit()          

        

        