import os
import time
from helper import log_dir
from multiprocessing import Pool
from config import *

def run(a):
    p = os.system(f'python3 controller.py --instrument_name={a}')
    return p

if __name__=='__main__':
    instrument_names = [ 'banknifty_test', 'nifty50_test']
    
    for i in instrument_names:
        if i not in controller_config:
            assert True==False, "Index miss match"

    with Pool(2) as p:
        p.map( run, instrument_names)