print('Main Started')

import os
from multiprocessing import Pool
from config import *

def run(a):
    p = os.system(f'python3 controller.py --instrument_name={a}')
    return p

if __name__=='__main__':
    test = True
    
    if test == True:
        instrument_names = [ 'banknifty_test', 'nifty50_test']
    else:
        instrument_names = [ 'banknifty', 'nifty50']
    
    for i in instrument_names:
        if i not in controller_config:
            assert True==False, "Index miss match"

    if test == True:
        for i in instrument_names:
            print(dict(controller_config[i]))
    
    with Pool(2) as p:
        p.map( run, instrument_names)