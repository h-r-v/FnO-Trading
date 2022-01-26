from helper import log_dir, log_info
from get_otp import get_otp
import os
from datetime import datetime
from mail import mail

#program launch timings
otp_gen_time = '4-00'
main_program_start_time = '9-20'
trade_loop_time = '9-30'
mail_time = '16-00'

#controller program start hr and min
main_hr, main_min = [int(i) for i in main_program_start_time.split('-')]

#otp program start hr and min
otp_hr, otp_min = [int(i) for i in otp_gen_time.split('-')]

#mail program start hr and min
mail_hr, mail_min = [int(i) for i in mail_time.split('-')]

#init
otp = None
otp_gen_flag = False
mail_flag = False
logfilename = os.path.join(log_dir(),'main.txt')

#controller program inf loop
while True:
    hour, minute, second = [int(i) for i in datetime.now().strftime("%H.%M.%S").split('.')]

    #every day reset
    if hour==0 and minute==0 and second==1:
        logfilename = os.path.join(log_dir(),'main.txt')
        otp = None
        otp_gen_flag = False
        with open(logfilename, 'a') as lf:
            log_info(lf, 'reset complete', 'daily_reset')

    #gen otp
    if hour==otp_hr and minute==otp_min and otp_gen_flag==False:
        with open(logfilename, 'a') as lf:
            try:
                log_info(lf, 'Generating otp', 'otp_generate')
                os.system(f'python trade_cli.py --get_otp')
                otp_gen_flag=True
                log_info(lf, 'OTP generated', 'otp_gen')
            except Exception as e:
                log_info(lf, e, 'ERROR: otp_gen')

    #every day at main program start time
    if hour==main_hr and minute==main_min:
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
            #trade cli launch
            try:
                log_info(lf, 'Launching trade_cli','trade_cli_launch')
                os.system(f'python trade_cli.py --otp={otp} --time={trade_loop_time}')
                log_info(lf,'trade_cli terminated', 'trade_cli_stop')
            except Exception as e:
                log_info(lf, e, 'ERROR: trade_cli')
    
    #send mail
    if hour==mail_hr and minute==mail_min and mail_flag==False:
        try:
            print('sending mail')
            mail()
            mail_flag = True
        except Exception as e:
            print(e)