print('Contoller Started')

from time import time, sleep
from helper import log_dir, log_info
from get_otp import get_otp
import os
from datetime import datetime
from mail import mail
from config import *
from docopt import docopt

usage='''
Usage:
    main.py [--instrument_name=<instrument_name>]

Options:
    --instrument_name=<instrument_name>   target instrument. Ex: banknifty, nifty50 [default: None]
'''

args = docopt(usage)
instrument_name = args['--instrument_name']

instrument, n, trade_start_time, trade_end_time , otp_gen_time, tradecli_start_time, mail_time = [None]*7

#loading variables
for i in controller_config[instrument_name].items():
    exec(f"{i[0]}='{i[1]}'")

#controller program start hr and min
start_hr, start_min = [int(i) for i in tradecli_start_time.split('-')]

#otp program start hr and min
otp_hr, otp_min = [int(i) for i in otp_gen_time.split('-')]

#mail program start hr and min
mail_hr, mail_min = [int(i) for i in mail_time.split('-')]

#init
otp = None
otp_gen_flag = False
mail_flag = False
logfilename = os.path.join(log_dir(instrument_name),'main.txt')
error_flag = False

#controller program inf loop
while True:
    hour, minute, second = [int(i) for i in datetime.now().strftime("%H.%M.%S").split('.')]

    #every day reset
    if hour==0 and minute==0 and second==1:
        otp = None
        otp_gen_flag = False
        error_flag = False
        mail_flag = False
        logfilename = os.path.join(log_dir(instrument_name),'main.txt')
        with open(logfilename, 'a') as lf:
            log_info(lf, 'reset complete', 'daily_reset')

    #if error flag is raised all operations are halted for that day
    if error_flag:
        #print('Some error occured. Check log files.')
        continue

    #gen otp
    if hour==otp_hr and minute==otp_min and otp_gen_flag==False:
        with open(logfilename, 'a') as lf:
            try:
                log_info(lf, 'Generating otp', 'otp_generate')
                p = os.system(f'python trade_cli.py --instrument_name="{instrument_name}" --get_otp')
                if p!=0:
                    raise Exception("otp gen failed")
                otp_gen_flag=True
                log_info(lf, 'OTP generated', 'otp_gen')
            except Exception as e:
                log_info(lf, e, 'ERROR: otp_gen')
                c = 60
                s = 10
                p = 1
                log_info(lf, f'Trying to gen otp {c} times at an interval of {s} seconds', 'otp_gen_retry')
                for i in range(c):
                    p = min(os.system(f'python trade_cli.py --instrument_name="{instrument_name}" --get_otp'), p)
                    sleep(s)
                
                if p != 0:    
                    error_flag = True
                

    #every day at main program start time
    if hour==start_hr and minute==start_min:
        with open(logfilename, 'a') as lf:
            #otp retrival
            try:
                otp = get_otp()
                if otp is None:
                    log_info(lf, 'OTP not found', 'otp_error')
                    assert True==False, 'OTP not found'
                log_info(lf, f'otp retrive succ', 'otp_ret')
                log_info(lf, f'otp={otp}', 'otp')
            except Exception as e:
                log_info(lf, e, 'ERROR: otp_retrive')
                error_flag = True
            #trade cli launch
            try:
                log_info(lf, 'Launching trade_cli','trade_cli_launch')
                p = os.system(f'python3 trade_cli.py --instrument_name="{instrument_name}" --otp="{otp}" --start_time="{trade_start_time}" --end_time="{trade_end_time}" --n="{n}"')
                if p!=0:
                    raise Exception("trade_cli failed")
                log_info(lf,'trade_cli terminated', 'trade_cli_stop')
            except Exception as e:
                log_info(lf, e, 'ERROR: trade_cli')
                error_flag = True
    
    #send mail
    if (hour==mail_hr and minute==mail_min and mail_flag==False) or error_flag:
        print('sending mail')
        mail(instrument_name, error_flag)
        mail_flag = True