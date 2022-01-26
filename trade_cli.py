usage='''
Usage:
    main.py [--sandbox] [--get_otp] [--otp=<otp>] [--time=<time>]

Options:
    --otp=<otp>     OTP [default: 1111], ignored if get_otp is chosen
    --prod          use sandbox enviorment
    --get_otp       us to generate otp.
    --time=<time>   main loop start time in h-m format. [default: 9-30]  
'''
#---------------------------------CLI & INIT---------------------------------
from docopt import docopt
from helper import *

args = docopt(usage)

sandbox = args['--sandbox'] #True if you want to use sandbox enviorment. False to use production enviorment.
get_access_only = args['--get_otp'] #True if you want to generate the OTP onlt. Flase if you want to execute the entire program.
access_code = args['--otp'] #OTP
main_loop_start_time = args['--time']

#get log dir
logdir = log_dir()

#creating log file
log = open(os.path.join(logdir,'trade.txt'), "a")

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
    log_info(log, 'OTP Generated', 'otp_gen_succ')
except Exception as e:
    log_info(log, f'Could not generate OTP. Error: {e}', 'otp_gen_error')
    log.close()
    exit()

#---------------------------------OTP VERIFICATION---------------------------------
if get_access_only==True:
    exit()

try:
    if sandbox==True:
        client.session_2fa(access_code = '1111')
    else:
        client.session_2fa(access_code = access_code)
    log_info(log, 'OTP Verified', 'otp_ver_succ')
except Exception as e:
    log_info(log, f'Could not verify OTP. Error: {e}', 'otp_ver_error')
    log.close()
    exit()

#---------------------------------Get TOKEN LIST---------------------------------
from datetime import datetime
import requests
fno_url = 'https://preferred.kotaksecurities.com/security/production/TradeApiInstruments_FNO_'+datetime.now().strftime("%d_%m_%Y")+'.txt'
cash_url = 'https://preferred.kotaksecurities.com/security/production/TradeApiInstruments_CASH_'+datetime.now().strftime("%d_%m_%Y")+'.txt'

#fno_url = 'https://preferred.kotaksecurities.com/security/production/TradeApiInstruments_FNO_10_12_2021.txt'
#cash_url = 'https://preferred.kotaksecurities.com/security/production/TradeApiInstruments_CASH_10_12_2021.txt'

fno_tokens = requests.get(fno_url)
cash_tokens = requests.get(cash_url)

if fno_tokens.status_code!=200 or cash_tokens.status_code!=200:
    log_info(log, 'Could not get token data.', 'token_error')
    exit()
else:
    log_info(log, 'Token data accquired.', 'token_succ')

fno_tokens = fno_tokens.text
cash_tokens = cash_tokens.text

fno_tokens = fno_tokens.split('\n')
fno_tokens = [i.strip().split('|') for i in fno_tokens]
cash_tokens = cash_tokens.split('\n')
cash_tokens = [i.strip().split('|') for i in cash_tokens]

if len(fno_tokens) <= 1 or len(cash_tokens) <= 1:
    log_info(log, "Token list not valid", 'token_error')
    exit()
else:
    log_info(log, 'Token data successful.', 'token_succ')

#initializing DataFrames
import pandas as pd

fno_df = pd.DataFrame( fno_tokens[1:], columns=fno_tokens[0])
cash_df = pd.DataFrame( cash_tokens[1:], columns=cash_tokens[0])

log_info(log, f"FnO DF shape: {fno_df.shape}", 'df_shape')
log_info(log, f"Cash DF shape: {cash_df.shape}", 'df_shape')

#---------------------------------BANKNIFTY TOKEN---------------------------------
banknifty_token = int(cash_df[cash_df.instrumentName=='NIFTY BANK'].instrumentToken.values[0])
log_info(log, f"BANK NIFTY TOKEN: {banknifty_token}", 'bnf_token')

#---------------------------------Time loop---------------------------------
from datetime import datetime
import os

old_second = 70

#main loop execution time
_hour, _min = [int(i) for i in main_loop_start_time.split('-')]

#first execution flags
firstafter930 = True
firstTL = True
firstat925 = True
firstat930 = True
firstat3 = True
firstat305 = True

#thresholds
slt = 1.3 #stop loss = slt * execution price
ext = 0.9 #execution price = ext * price at 9:30

#p&l vars
sell = 0
buy = 0

#number of shares
quantity = 25

while True:
    
    hour, minute, second = [int(i) for i in datetime.now().strftime("%H.%M.%S").split('.')]
    
    if( (old_second+3)%60==second or firstTL):
        print(f'{hour}:{minute}:{second} : Time loop working')

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
            
            
            #log and print banknifty atm
            log_info(log,f"BNF ATM @{banknity_atm}",'strike_price')

            #get and log pe and ce token at that atm
            banknity_token_pe, banknity_token_ce = get_pe_ce_token(banknity_atm, fno_df)
            log_info(log,f"BNF CE TOKEN @{banknity_token_ce}",'bnf_ce_token')
            log_info(log,f"BNF PE TOKEN @{banknity_token_pe}",'bnf_pe_token')

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
            banknifty_ce_ex = ext*banknifty_ce_ltp_930
            banknifty_pe_ex = ext*banknifty_pe_ltp_930

            #log and print CE execution price and stop loss
            log_info(log, f'BNF {banknity_atm} CE execution price set @{banknifty_ce_ex}', 'execution_price')
            log_info(log, f'BNF {banknity_atm} CE stop loss set @{slt*banknifty_ce_ex}', 'stop_loss')
            
            #log and print PE execution price
            log_info(log, f'BNF {banknity_atm} PE execution price set @{banknifty_pe_ex}', 'execution_price')
            log_info(log, f'BNF {banknity_atm} PE stop loss set @{slt*banknifty_pe_ex}', 'stop_loss')

            #log and print end of 9:30am procedure
            log_info(log, f'At 9:30am procedure completed', 'sys_alert')
            firstat930=False

        #After 9:30am
        if(hour>=_hour and firstat930==False):
            log_info(log, f'After 9:30 executed', 'sys_alert')

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
                sell = banknifty_ce_ltp
                #client.place_order(order_type = "MIS", instrument_token = banknity_token_ce, transaction_type = "SELL", quantity = quantity, price = 0)
                banknifty_ce_hit = True

            #buy ce if reversal
            if (banknifty_ce_hit==True and banknifty_ce_ltp>=slt*banknifty_ce_ex and banknifty_ce_wrong==False):
                log_info(log, f'BUY BNF {banknity_atm} CE executed @{banknifty_ce_ltp}', 'buy')
                buy = banknifty_ce_ltp
                #client.place_order(order_type = "MIS", instrument_token = banknity_token_ce, transaction_type = "BUY", quantity = quantity, price = 0)
                banknifty_ce_wrong = True

            #sell pe when execution price is hit for the first time
            if (banknifty_pe_ltp<=banknifty_pe_ex and banknifty_pe_hit==False):
                log_info(log, f'SELL BNF {banknity_atm} PE executed @{banknifty_pe_ltp}', 'sell')
                sell = banknifty_pe_ltp
                #client.place_order(order_type = "MIS", instrument_token = banknity_token_pe, transaction_type = "SELL", quantity = quantity, price = 0)
                banknifty_pe_hit = True

            #buy pe if reversal
            if (banknifty_pe_hit==True and banknifty_pe_ltp>=slt*banknifty_pe_ex and banknifty_pe_wrong==False):
                log_info(log, f'BUY BNF {banknity_atm} PE executed @{banknifty_pe_ltp}', 'buy')
                buy = banknifty_pe_ltp
                #client.place_order(order_type = "MIS", instrument_token = banknity_token_pe, transaction_type = "BUY", quantity = quantity, price = 0)
                banknifty_pe_wrong = True

            #At 3pm
            if(hour==15 and minute==3 and firstat3==True):
                log_info(log, 'At 3pm procedure started', 'sys_alert')

                #buy ce to square off
                if( banknifty_ce_hit==True and banknifty_ce_wrong==False ):
                    log_info(log, f'SQUAREOFF BUY BNF {banknity_atm} CE executed @{banknifty_ce_ltp}', 'squareoff')
                    buy = banknifty_ce_ltp
                    #client.place_order(order_type = "MIS", instrument_token = banknity_token_ce, transaction_type = "BUY", quantity = quantity, price = 0)

                #buy pe to square off
                if( banknifty_pe_hit==True and banknifty_pe_wrong==False ):
                    log_info(log, f'SQUAREOFF BUY BNF {banknity_atm} PE executed @{banknifty_pe_ltp}', 'squareoff')
                    buy = banknifty_pe_ltp
                    #client.place_order(order_type = "MIS", instrument_token = banknity_token_pe, transaction_type = "BUY", quantity = quantity, price = 0)  

                log_info(log, 'After 3pm procedure completed', 'sys_alert')

                firstat3 = False
            
            #After 3pm
            if( firstat3==False and firstat305==True):
                #log and print end of at 3:05pm procedure
                log_info(log, f'p&l per unit today @{sell-buy}')
                log_info(log, f'p&l total({quantity}) today @{(sell-buy)*quantity}')
                log_info(log, 'After 3pm procedure completed', 'sys_alert')
                log.close()
                firstat305==False
                exit()          

        

        
