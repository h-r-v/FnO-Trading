from datetime import datetime, timedelta
time_now = datetime.now()

controller_config = { 
    'nifty50':{ 
        'instrument': 'NIFTY 50',
        'n':'50',
        'trade_start_time':'9-35', 
        'trade_end_time':'15-15', 
        'otp_gen_time':'4-00', 
        'tradecli_start_time':'9-30', 
        'mail_time':'16-00'},
    'banknifty':{ 
        'instrument': 'NIFTY BANK',
        'n':'25',
        'trade_start_time':'9-45', 
        'trade_end_time':'15-00', 
        'otp_gen_time':'4-00', 
        'tradecli_start_time':'9-40', 
        'mail_time':'16-00'},
    'banknifty_test':{ 
        'instrument': 'NIFTY BANK',
        'n':'25',
        'trade_start_time':(time_now + timedelta(minutes=3)).strftime('%H-%M'), 
        'trade_end_time':(time_now + timedelta(minutes=5)).strftime('%H-%M'), 
        'otp_gen_time':(time_now + timedelta(minutes=1)).strftime('%H-%M'), 
        'tradecli_start_time':(time_now + timedelta(minutes=1)).strftime('%H-%M'), 
        'mail_time':(time_now + timedelta(minutes=6)).strftime('%H-%M')},
    'nifty50_test':{ 
        'instrument': 'NIFTY 50',
        'n':'50',
        'trade_start_time':(time_now + timedelta(minutes=3)).strftime('%H-%M'), 
        'trade_end_time':(time_now + timedelta(minutes=5)).strftime('%H-%M'), 
        'otp_gen_time':(time_now + timedelta(minutes=1)).strftime('%H-%M'), 
        'tradecli_start_time':(time_now + timedelta(minutes=1)).strftime('%H-%M'), 
        'mail_time':(time_now + timedelta(minutes=6)).strftime('%H-%M')},
    }

trade_config = {
    'test':{
        'userid' : "1T068",
        'password' : 'login@1',
        'access_token' : "ebe9c833-26c1-3402-bf80-c457e76a4da3",
        'consumer_key' : "a0s3dcOM4JgVNn3pB7fdLBFkJ4Ea",
        'host' : 'https://sbx.kotaksecurities.com/apim'},
    'prod':{
        'userid' : "NT1945",
        'password' : 'BT121299@',
        'access_token' : "3bf7af61-77c2-3f2e-b1c1-f4f5cb909db3",
        'consumer_key' : "ay4bObamN3KHOPzZjmpA7g9YDJwa",
        'host' : 'https://tradeapi.kotaksecurities.com/apim'}
        }

if __name__=='__main__':
    print("yo")