from helper import log_dir, log_info
from get_otp import get_otp
import os

logfilename = os.path.join(log_dir(),'main.txt')
with open(logfilename, 'a') as lf:
    log_info(lf, 'Getting otp', 'otp')
    otp = get_otp()
    log_info(lf, f'otp={otp}', 'otp')
    log_info(lf, 'Launching trade_cli','trade_cli_launch')
    os.system(f'python trade_cli.py --otp={otp}')
    log_info(lf,'trade_cli terminated', 'trade_cli_stop')
