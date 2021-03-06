'''
TEAM: FiSci
PEOPLE: Hannah Ni, Hannah Walter, Lin Su

Interactive interface via COMMAND LINE to guide user find company ticker.
Would NOT be shown via Django.
'''

try:
    from urllib.request import urlopen
except ImportError:
    from urllib2 import urlopen
from json import loads

ticker = ''
while ticker == '':
    while True:
        company_input = str(input("Please enter a company name or ticker: "))
        response = urlopen('http://chstocksearch.herokuapp.com/api/{}'.format(company_input))
        string = response.read().decode('utf-8')
        json_obj = loads(string)
        if len(json_obj) == 1:
            print("\nSorry, we could not find any company name or ticker that contains your input."
                "\nPlease check your spelling and try again:\n")
            continue
        else:
            break
    if len(json_obj) == 2: 
        ticker = json_obj[0]['symbol']
        print('\nCONGRATULATIONS, we helped you find the ticker:\n', ticker)
    else:
        print('\nWe found the following company names and tickers that contain your input:')
        for index, company in enumerate(json_obj[:-1]):
            print(index + 1, company)
        while True:
            select = input('\nIf none of the above companies is what you intended to search, '
                'please enter anything but an integer. Otherwise, please enter its index:')
            try:
                index = int(select)
                if index > 0 and index < len(json_obj):
                    ticker = json_obj[index - 1]['symbol']
                    print('\nCONGRATULATIONS, we helped you find the ticker:\n', ticker)
                    break
                else:
                    print('\nSorry, index out of range, please try again:')
                    continue
            except ValueError:
                print('\nSorry, we could not recognize the index that you entered just now.\n\n'
                    'Please try again from the start:')
                break