from datetime import datetime
import json
import os

# get ltp and atm
def get_atm(instrument_token, client):
    banknity_ltp = client.quote(instrument_token = instrument_token, quote_type = "LTP")
    if 'success' in banknity_ltp:
        banknity_ltp = banknity_ltp['success'][0]['lastPrice']
    else:
        assert True==False

    banknity_ltp = float(banknity_ltp)
    banknity_atm = round(banknity_ltp, -2)

    #banknity_atm = 37100
    #print('BANK NIFTY ATM:', banknity_atm)
    
    return int(banknity_atm)

# get pe ce tokens for a strike
def get_pe_ce_token(banknity_atm, fno_df):
    fno_df = fno_df[ (fno_df.instrumentName == 'BANKNIFTY') & (fno_df.strike==str(int(banknity_atm)))][0:2]
    banknity_token_pe = int(fno_df[fno_df.optionType=='PE']['instrumentToken'].values[0])
    banknity_token_ce = int(fno_df[fno_df.optionType=='CE']['instrumentToken'].values[0])

    #print(f"BANK NIFTY {banknity_atm} PE TOKEN:",banknity_token_pe)
    #print(f"BANK NIFTY {banknity_atm} CE TOKEN:",banknity_token_ce)
    
    return banknity_token_pe,banknity_token_ce

#check and get quote
def get_quote(instrument_token, client):
    ltp = client.quote(instrument_token = instrument_token, quote_type = "LTP")
    if 'success' in ltp:
        ltp = ltp['success'][0]['lastPrice']
    else:
        assert True==False

    ltp = float(ltp)

    return ltp

#log info
def log_info(opfile, message, typ='UNK', time=None, display=True):
    
    if time==None:
        time = datetime.now().strftime("%H:%M:%S")
    elif isinstance(time,list):
        ':'.join([ str(i) for i in time])

    final_message = json.dumps({'message':message, 'type':typ, 'time':time})+'\n'
    
    if display:
        print(f'{time} : {message}')
    
    opfile.write(final_message)

#return log dir of the day
def log_dir():
    #creating log dir
    if not os.path.exists('logs'):
        os.mkdir('logs')

    #date
    log = datetime.now().strftime("%m-%d-%Y")

    #creating date subdir
    if not os.path.exists(os.path.join('logs',log)):
        os.mkdir(os.path.join('logs',log))

    #log dir for the day
    logdir = os.path.join('logs',log)

    return logdir