import os
from multiprocessing import Pool

def run(a):
    os.system(f'python3 controller.py --instrument={a}')

if __name__=='__main__':
    with Pool(2) as p:
        p.map(run,['banknifty_test','nifty_test'])