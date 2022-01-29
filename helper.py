from datetime import datetime
import json
import os

# get ltp and atm
def get_atm(instrument_token, client):
    instrument_ltp = client.quote(instrument_token = instrument_token, quote_type = "LTP")
    if 'success' in instrument_ltp:
        instrument_ltp = instrument_ltp['success'][0]['lastPrice']
    else:
        assert True==False

    instrument_ltp = float(instrument_ltp)
    instrument_atm = round(instrument_ltp, -2)

    return int(instrument_atm)

# get pe ce tokens for a strike
def get_pe_ce_token(instrument, instrument_atm, fno_df):
    #mapping according to the fno_df
    if instrument == 'NIFTY BANK':
        instrument = 'BANKNIFTY'
    elif instrument == 'NIFTY 50':
        instrument = 'NIFTY'
    
    fno_df = fno_df[ (fno_df.instrumentName == instrument) & (fno_df.strike==str(int(instrument_atm)))][0:2]
    instrument_token_pe = int(fno_df[fno_df.optionType=='PE']['instrumentToken'].values[0])
    instrument_token_ce = int(fno_df[fno_df.optionType=='CE']['instrumentToken'].values[0])
    
    return instrument_token_pe,instrument_token_ce

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

    final_message = json.dumps({'message':str(message), 'type':str(typ), 'time':str(time)})+'\n'
    
    if display:
        print(f'{time} : {message} : {opfile.name.split("/")[-2]}')
    
    opfile.write(final_message)

#return log dir of the day
def log_dir(sub_dir=''):

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

    if sub_dir != '':
        #creating instrument subdir
        if not os.path.exists(os.path.join(logdir,sub_dir)):
            os.mkdir(os.path.join(logdir,sub_dir))

        #log dir for the day
        logdir = os.path.join(logdir,sub_dir)

    return logdir

if __name__ == '__main__':
    print(log_dir('NIFTY'))