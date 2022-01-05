usage = '''
Usage:
    test.py start prod [--otp=<otp>|--gen_otp]
    test.py start test [--otp=<otp>|--gen_otp]

Options:
    --otp=<otp>  OTP [default: 1111]
    --gen_otp    generate otp
'''

from docopt import docopt
args = docopt(usage)
print(args)
