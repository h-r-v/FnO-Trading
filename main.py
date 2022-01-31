import os
import time
from helper import log_dir
from multiprocessing import Pool
from config import *

def run(a):
    #required to remove log file occupied resource
    time.sleep(a[1])

    log_dir(a[0], make=True)
        
    os.system(f'python3 controller.py --instrument={a[0]}')

if __name__=='__main__':
    instrument_names = [ 'banknifty_test', 'nifty50_test']
    
    for i in instrument_names:
        if i not in controller_config:
            assert True==False, "Index miss match"
    
    instrument_names = [(name,i*5) for i,name in enumerate(instrument_names)]

    with Pool(2) as p:
        p.map( run, instrument_names)