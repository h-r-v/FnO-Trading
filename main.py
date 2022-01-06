from helper import log_dir, log_info
from get_otp import get_otp
import os
import time

logfilename = os.path.join(log_dir(),'main.txt')
with open(logfilename, 'a') as lf:
    log_info(lf, 'Generating otp', 'otp_generate')
    os.system(f'python trade_cli.py --get_otp')
    time.sleep(20)
    log_info(lf, 'OTP generated', 'otp_retrive')
    otp = get_otp()
    if otp is None:
        log_info(lf, 'OTP not found', 'otp_error')
        assert True==False, 'OTP not found'
    log_info(lf, f'otp={otp}', 'otp')
    log_info(lf, 'Launching trade_cli','trade_cli_launch')
    os.system(f'python trade_cli.py --otp={otp}')
    log_info(lf,'trade_cli terminated', 'trade_cli_stop')
