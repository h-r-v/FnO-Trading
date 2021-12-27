# get ltp and atm
def get_atm(instrument_token, client):
    banknity_ltp = client.quote(instrument_token = instrument_token, quote_type = "LTP")
    if 'success' in banknity_ltp:
        banknity_ltp = banknity_ltp['success'][0]['lastPrice']
    else:
        assert True==False

    banknity_ltp = float(banknity_ltp)
    banknity_atm = round(banknity_ltp, -2)

    #banknity_atm = 37100

    print('BANK NIFTY ATM:', banknity_atm)
    return int(banknity_atm)

# get pe ce tokens for a strike
def get_pe_ce_token(banknity_atm, fno_df):
    fno_df = fno_df[ (fno_df.instrumentName == 'BANKNIFTY') & (fno_df.strike==str(int(banknity_atm)))][0:2]
    banknity_token_pe = int(fno_df[fno_df.optionType=='PE']['instrumentToken'].values[0])
    banknity_token_ce = int(fno_df[fno_df.optionType=='CE']['instrumentToken'].values[0])

    print(f"BANK NIFTY {banknity_atm} PE TOKEN:",banknity_token_pe)
    print(f"BANK NIFTY {banknity_atm} CE TOKEN:",banknity_token_ce)
    return banknity_token_pe,banknity_token_ce

#check and get quote
def get_quote(instrument_token, client):
    ltp = client.quote(instrument_token = instrument_token, quote_type = "LTP")
    if 'success' in ltp:
        ltp = ltp['success'][0]['lastPrice']
    else:
        assert True==False

    ltp = float(ltp)

    return ltp