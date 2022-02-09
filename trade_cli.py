usage='''
Usage:
    main.py [--instrument_name=<instrument_name>] [--sandbox] [--get_otp] [--otp=<otp>] [--start_time=<start_time>] [--end_time=<end_time>] [--n=<n>]

Options:
    --instrument_name=<instrument_name>   target instrument. Ex: banknifty, nifty, etc
    --otp=<otp>                 OTP [default: 1111], ignored if get_otp is chosen
    --sandbox                   use sandbox enviorment
    --get_otp                   us to generate otp.
    --start_time=<start_time>   main loop start time in h-m format. [default: 9-30]
    --end_time=<end_time>       main loop start time in h-m format. [default: 15-00]
    --n=<n>                     number of lots. Ex:25, 20 [default: 25]  
'''
#---------------------------------CLI & INIT---------------------------------
from ast import arg
from docopt import docopt
from helper import *
from config import *

args = docopt(usage)

run_env = 'test' if args['--sandbox'] else 'prod' #True if you want to use sandbox enviorment. False to use production enviorment.
get_access_only = args['--get_otp'] #True if you want to generate the OTP onlt. Flase if you want to execute the entire program.
access_code = args['--otp'] #OTP
start_time = args['--start_time']
end_time = args['--end_time']
instrument_name = args['--instrument_name']

#number of shares
quantity = args['--n']

#get log dir
logdir = log_dir(instrument_name)

#creating log file
log = open(os.path.join(logdir,'trade.txt'), "a")

#getting the instrument according to the instrument_name
if instrument_name in controller_config:
    instrument = controller_config[instrument_name]['instrument']
    log_info(log, 'instrument loaded', 'instrument_load_succ')
else:
    log_info(log, 'instrument index miss match', 'ERROR: instrument_error')
    exit(1)

#init credentials
userid ,password, access_token ,consumer_key ,host = [None]*5

#loading credentials
for i in trade_config[run_env].items():
    exec(f"{i[0]}='{i[1]}'")

#---------------------------------GENERATING OTP---------------------------------
from ks_api_client.ks_api import KSTradeApi

try:
    client = KSTradeApi(access_token = access_token, userid = userid, \
                    consumer_key = consumer_key, ip = "127.0.0.1", app_id = "DefaultApplication", host = host)
    client.login(password=password)
    log_info(log, 'OTP Generated', 'otp_gen_succ')
except Exception as e:
    log_info(log, f'Could not generate OTP. Error: {e}', 'ERROR: otp_gen_error')
    log.close()
    exit(1)

#---------------------------------OTP VERIFICATION---------------------------------
if get_access_only==True:
    exit(0)

try:
    if run_env=='test':
        client.session_2fa(access_code = '1111')
    else:
        client.session_2fa(access_code = access_code)
    log_info(log, 'OTP Verified', 'otp_ver_succ')
except Exception as e:
    log_info(log, f'Could not verify OTP. Error: {e}', 'ERROR: otp_ver_error')
    log.close()
    exit(1)

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
    log_info(log, 'Could not get token data.', 'ERROR: token_error')
    exit(1)
else:
    log_info(log, 'Token data accquired.', 'token_succ')

fno_tokens = fno_tokens.text
cash_tokens = cash_tokens.text

fno_tokens = fno_tokens.split('\n')
fno_tokens = [i.strip().split('|') for i in fno_tokens]
cash_tokens = cash_tokens.split('\n')
cash_tokens = [i.strip().split('|') for i in cash_tokens]

if len(fno_tokens) <= 1 or len(cash_tokens) <= 1:
    log_info(log, "Token list not valid", 'ERROR: token_error')
    exit(1)
else:
    log_info(log, 'Token data successful.', 'token_succ')

#initializing DataFrames
import pandas as pd

fno_df = pd.DataFrame( fno_tokens[1:], columns=fno_tokens[0])
cash_df = pd.DataFrame( cash_tokens[1:], columns=cash_tokens[0])

log_info(log, f"FnO DF shape: {fno_df.shape}", 'df_shape')
log_info(log, f"Cash DF shape: {cash_df.shape}", 'df_shape')

#---------------------------------INSTRUMENT TOKEN---------------------------------
instrument_token = int(cash_df[cash_df.instrumentName==instrument].instrumentToken.values[0])
log_info(log, f"{instrument} TOKEN: {instrument_token}", 'instrument_token')

#---------------------------------Time loop---------------------------------
from datetime import datetime
import os

#init time vars
old_second = 70
time_diff = 10

#main loop time vars
start_hour, start_min = [int(i) for i in start_time.split('-')] # controls stage 1,2,3
end_hour, end_min = [int(i) for i in end_time.split('-')] # controls stage 4,5

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
sell_ce = 0
buy_ce = 0
sell_pe = 0
buy_pe = 0

#fail counts catch
ltp_fail_c = 0

'''
STAGE 1: At 9:25am: get atm, get ce/pe token, init flags
STAGE 2: At 9:30am: get pe/ce quote to calculate SL and EX
STAGE 3: After 9:30am: get pe/ce quote, see if criteras to buy/sell are met
STAGE 4: At 3pm: squareoff
STAGE 5: After 3pm: calc pnl
'''

while True:
    
    hour, minute, second = [int(i) for i in datetime.now().strftime("%H.%M.%S").split('.')]
    
    if( (old_second+time_diff)%60==second or firstTL):
        print(f'{hour}:{minute}:{second} : Time loop working : {instrument_name}')

        #log and print time loop start
        if firstTL==True:
            log_info(log, 'Time loop started', 'sys_alert')
            firstTL=False

        #update time
        old_second=second
        
        #STAGE 1
        if(hour==start_hour and minute==start_min-1 and firstat925==True):
            #log and print start of STAGE 1
            log_info(log, 'Executing STAGE 1 procedure', 'sys_alert')

            #get instrument atm
            instrument_atm = get_atm(instrument_token, client)
            
            
            #log and print instrument atm
            log_info(log,f"{instrument} ATM @{instrument_atm}",'strike_price')

            #get and log pe and ce token at that atm
            instrument_token_pe, instrument_token_ce = get_pe_ce_token(instrument ,instrument_atm, fno_df)
            log_info(log,f"{instrument} CE TOKEN @{instrument_token_ce}",'instrument_ce_token')
            log_info(log,f"{instrument} PE TOKEN @{instrument_token_pe}",'instrument_pe_token')

            #initialize hit flags
            instrument_ce_hit = False
            instrument_pe_hit = False
            instrument_ce_wrong = False
            instrument_pe_wrong = False

            #log and print end of STAGE 1
            log_info(log, f"STAGE 1 procedure completed", 'sys_alert')
            firstat925 = False

        #STAGE 2
        if(hour==start_hour and minute==start_min and firstat930==True):
            #log and print start of 9:30am procedure
            log_info(log,'Executing STAGE 2 procedure','sys_alert')

            #get ce and pe quote @ 9:30
            instrument_ce_ltp_930 = get_quote(instrument_token_ce, client)
            instrument_pe_ltp_930 = get_quote(instrument_token_pe, client)

            #log and print CE LTP @9:30am
            log_info(log, f'{instrument} {instrument_atm} CE 9:30 am LTP @{instrument_ce_ltp_930}', 'ltp_alert')
            
            #log and print PE LTP @9:30am
            log_info(log, f'{instrument} {instrument_atm} PE 9:30 am LTP @{instrument_pe_ltp_930}', 'ltp_alert')

            #get execution price
            instrument_ce_ex = ext*instrument_ce_ltp_930
            instrument_pe_ex = ext*instrument_pe_ltp_930

            #log and print CE execution price and stop loss
            log_info(log, f'{instrument} {instrument_atm} CE execution price set @{instrument_ce_ex}', 'execution_price')
            log_info(log, f'{instrument} {instrument_atm} CE stop loss set @{slt*instrument_ce_ex}', 'stop_loss')
            
            #log and print PE execution price
            log_info(log, f'{instrument} {instrument_atm} PE execution price set @{instrument_pe_ex}', 'execution_price')
            log_info(log, f'{instrument} {instrument_atm} PE stop loss set @{slt*instrument_pe_ex}', 'stop_loss')

            #log and print end of 9:30am procedure
            log_info(log, f'STAGE 2 procedure completed', 'sys_alert')
            firstat930=False

        #STAGE 3
        if(hour>=start_hour and firstat930==False):

            if firstafter930==True:
                #log and print start of STAGE 3 procedure
                log_info(log, "Executing STAGE 3 procedure", 'sys_alert')
                firstafter930 = False

            #Get LTP for CE and PE every time_diff second
            try:
                instrument_ce_ltp = get_quote(instrument_token_ce, client)
                instrument_pe_ltp = get_quote(instrument_token_pe, client)
                ltp_fail_c = max(0,ltp_fail_c-1)
            except Exception as e:
                log_info( log, f'{e} : LTP fail count @{ltp_fail_c}', 'ERROR: ltp_error')
                ltp_fail_c += 1
                if ltp_fail_c >= int((60*10)/time_diff):
                    log_info( log, f'LTP fail threshold reached({ltp_fail_c})','ERROR: ltp_error')
                    exit(1)
                else:
                    continue

            log_info(log, f'instrument_ce_ltp @{instrument_ce_ltp}','ltp_alert')
            log_info(log, f'instrument_pe_ltp @{instrument_pe_ltp}','ltp_alert')

            #sell ce when execution price is hit for the first time
            if (instrument_ce_ltp<=instrument_ce_ex and instrument_ce_hit==False):
                log_info(log, f'SELL {instrument} {instrument_atm} CE executed @{instrument_ce_ltp}', 'sell')
                sell_ce = instrument_ce_ltp
                #client.place_order(order_type = "MIS", instrument_token = instrument_token_ce, transaction_type = "SELL", quantity = quantity, price = 0)
                instrument_ce_hit = True

            #buy ce if reversal
            if (instrument_ce_hit==True and instrument_ce_ltp>=slt*instrument_ce_ex and instrument_ce_wrong==False):
                log_info(log, f'BUY {instrument} {instrument_atm} CE executed @{instrument_ce_ltp}', 'buy')
                buy_ce = instrument_ce_ltp
                #client.place_order(order_type = "MIS", instrument_token = instrument_token_ce, transaction_type = "BUY", quantity = quantity, price = 0)
                instrument_ce_wrong = True

            #sell pe when execution price is hit for the first time
            if (instrument_pe_ltp<=instrument_pe_ex and instrument_pe_hit==False):
                log_info(log, f'SELL {instrument} {instrument_atm} PE executed @{instrument_pe_ltp}', 'sell')
                sell_pe = instrument_pe_ltp
                #client.place_order(order_type = "MIS", instrument_token = instrument_token_pe, transaction_type = "SELL", quantity = quantity, price = 0)
                instrument_pe_hit = True

            #buy pe if reversal
            if (instrument_pe_hit==True and instrument_pe_ltp>=slt*instrument_pe_ex and instrument_pe_wrong==False):
                log_info(log, f'BUY {instrument} {instrument_atm} PE executed @{instrument_pe_ltp}', 'buy')
                buy_pe = instrument_pe_ltp
                #client.place_order(order_type = "MIS", instrument_token = instrument_token_pe, transaction_type = "BUY", quantity = quantity, price = 0)
                instrument_pe_wrong = True

            #STAGE 4
            if(hour==end_hour and minute==end_min and firstat3==True):
                log_info(log, 'STAGE 4 procedure started', 'sys_alert')

                #buy ce to square off
                if( instrument_ce_hit==True and instrument_ce_wrong==False ):
                    log_info(log, f'SQUAREOFF BUY {instrument} {instrument_atm} CE executed @{instrument_ce_ltp}', 'squareoff')
                    buy_ce = instrument_ce_ltp
                    #client.place_order(order_type = "MIS", instrument_token = instrument_token_ce, transaction_type = "BUY", quantity = quantity, price = 0)

                #buy pe to square off
                if( instrument_pe_hit==True and instrument_pe_wrong==False ):
                    log_info(log, f'SQUAREOFF BUY {instrument} {instrument_atm} PE executed @{instrument_pe_ltp}', 'squareoff')
                    buy_pe = instrument_pe_ltp
                    #client.place_order(order_type = "MIS", instrument_token = instrument_token_pe, transaction_type = "BUY", quantity = quantity, price = 0)  

                log_info(log, 'STAGE 4 procedure completed', 'sys_alert')

                firstat3 = False
            
            #STAGE 5
            if( firstat3==False and firstat305==True):
                #log and print end of at 3:05pm procedure
                log_info(log, 'STAGE 5 procedure started', 'sys_alert')
                log_info(log, f'p&l per unit today @{(sell_ce-buy_ce)+(sell_pe-buy_pe)}', typ='pnl')    
                log_info(log, f'p&l total({quantity}) today @{((sell_ce-buy_ce)+(sell_pe-buy_pe))*int(quantity)}', typ='pnl')
                log_info(log, 'STAGE 5 procedure completed', 'sys_alert')
                log.close()
                firstat305==False
                exit(0)