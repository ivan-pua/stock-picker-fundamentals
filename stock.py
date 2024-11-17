#!/usr/bin/env python

from urllib.request import urlopen # For Python 3.0 and later
from dotenv import load_dotenv
import json
import os
from pprint import pprint
import ssl
from colorama import Fore, Style

load_dotenv() 
FM_PREP_API_KEY = os.environ.get("FM_PREP_API_KEY")

def get_jsonparsed_data(url):
    ssl_context = ssl.create_default_context()
    response = urlopen(url, context=ssl_context)
    data = response.read().decode("utf-8")
    return json.loads(data)

def get_stock_details(stock_symbol):

    stock_details = {'symbol': stock_symbol}

    '''
    Company Profile
    '''
    profile_url = f"https://financialmodelingprep.com/api/v3/profile/{stock_symbol}?apikey={FM_PREP_API_KEY}"

    company_profile = get_jsonparsed_data(profile_url)[0]

    stock_details['name'] = company_profile['companyName']
    stock_details['industry'] = company_profile['industry']
    stock_details['year_inc'] = company_profile['ipoDate'].split('-')[0]
    stock_details['current_price'] = company_profile['price']

    '''
    Company Quote
    Grain: Seconds, in real time
    '''
    quote_url = f"https://financialmodelingprep.com/api/v3/quote/{stock_symbol}?apikey={FM_PREP_API_KEY}"
    company_quote = get_jsonparsed_data(quote_url)[0]

    stock_details['year_high'] = company_quote['yearHigh']
    stock_details['year_low'] = company_quote['yearLow']
    stock_details['market_cap'] = company_quote['marketCap']
    # eps = company_quote['eps']
    stock_details['realtime_pe_ratio'] = company_quote['pe']

    '''
    Company Financials Growth
    Grain: Annually, based on Financial Statement
    '''
    financial_growth_url = f"https://financialmodelingprep.com/api/v3/financial-growth/{stock_symbol}?period=annual&apikey={FM_PREP_API_KEY}"
    financial_growth = get_jsonparsed_data(financial_growth_url)[0]

    stock_details['financial_statement_date'] = financial_growth['date']
    stock_details['eps_growth'] = financial_growth['epsgrowth']
    stock_details['grossProfitGrowth'] = financial_growth['grossProfitGrowth']

    '''
    Financial Ratios
    Grain: Annually, based on Financial Statement
    Also has debt equity ratio, return on tangible assets
    '''
    ratios_url = f"https://financialmodelingprep.com/api/v3/ratios/{stock_symbol}?period=annual&apikey={FM_PREP_API_KEY}"
    ratios = get_jsonparsed_data(ratios_url)[0]

    stock_details['returnOnAssets'] = ratios['returnOnAssets']
    stock_details['returnOnEquity'] = ratios['returnOnEquity']
    stock_details['dividendYield'] = ratios['dividendYield']
    stock_details['interestCoverage'] = ratios['interestCoverage']
    stock_details['debtEquityRatio'] = ratios['debtEquityRatio']
    stock_details['priceToBookRatio'] = ratios['priceToBookRatio']
    # debtEquityRatioTTM = company_ratio_ttm['debtEquityRatioTTM']

    '''
    Stock Price Change
    '''
    price_change_url = f"https://financialmodelingprep.com/api/v3/stock-price-change/{stock_symbol}?apikey={FM_PREP_API_KEY}"
    price_change = get_jsonparsed_data(price_change_url)[0]

    stock_details['1Y_change'] = price_change['1Y'] / stock_details['current_price']
    stock_details['3Y_change'] = (price_change['3Y'] / 3) / stock_details['current_price'] #divided by 3

    return stock_details

def check_stock(stock):
    checks = {
            'year_inc': (lambda x: 2023 - int(x) > 3, '2023 - year_inc > 3'),
            'market_cap': (lambda x: x > 100000000, 'market_cap > 100000000'),
            'grossProfitGrowth': (lambda x: x > 0, 'grossProfitGrowth > 0'),
            'returnOnAssets': (lambda x: x > 0.08, 'returnOnAssets > 0.08'),
            'returnOnEquity': (lambda x: x > 0.1, 'returnOnEquity > 0.1'),
            'eps_growth': (lambda x: x > 0.05, 'eps_growth > 0.05'),
            'dividendYield': (lambda x: 0 if x is None else x > 0.03, 'dividendYield > 0.03'),
            'interestCoverage': (lambda x: x > 2, 'interestCoverage > 2'),
            'debtEquityRatio': (lambda x: 0 < x < 1.5, '0 < debtEquityRatio < 1.5'),
            'realtime_pe_ratio': (lambda x: 10 < x < 25, '10 < realtime_pe_ratio < 25'),
            'priceToBookRatio': (lambda x: 0 < x < 4, '0 < priceToBookRatio < 4'),
            '1Y_change': (lambda x: x > 0.1, 'Average 1 year change > 0.1'),
            '3Y_change': (lambda x: x > 0.1, 'Average 3 years change > 0.1')
        }

    for key in stock:
        value = stock[key]
        if isinstance(value, float):
            value = round(value, 3)

        if value is None:
            continue

        if key in checks:
            condition, condition_str = checks[key]
            if condition(value):
                print(Fore.GREEN + f"{key}: {value}")
            else:
                print(Fore.YELLOW + f"{key}: {value} ({condition_str})")
        else:
            print(Style.RESET_ALL + f"{key}: {value}")

    print(Style.RESET_ALL + "------------------")


def main():
    current_stocks = ["AAPL", "MSFT", "CRWD", # Tech 
                      "UNH", "AMGN", # Health
                      "WMT", "HD", # Retail
                      "ADM", # Food
                      "JPM", #Finance
                      "PLTR", "CGC", # Speculative 
                      ]
    
    # These stocks are identified via https://www.tradingview.com/markets/stocks-usa/sectorandindustry-sector/
    # Be diverse!
    exploratory_stocks = ['UROY', 'UUUU', 'LEU', 'SMR', 'URG', 'DNN', 'UEC','SBSW', 'NXE', 'CCJ']
    gaming_stocks = ["UBER", "DIS", "EA", "TTWO"]
    retail = ["HD", "COST", "PDD", "LOW", "MELI", "LULU" ]
    utilities = ["NEE", "SO", "DUK", "CEG"]
    process_industry = ["LIN", "SHW", "ECL"]
    consumer_services = ["TCOM", "CTAS"]

    # Modify this one:
    stock_list = consumer_services
    
    for id, stock_symbol in enumerate(stock_list):
        print(f"[{id}/{len(stock_list)-1}]")
        stock = get_stock_details(stock_symbol)
        check_stock(stock)

if __name__ == '__main__':
    main()