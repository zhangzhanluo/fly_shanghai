import time
import json
import requests


def get_all_flights(direction='Departure'):
    """
    get all flight information from https://www.shanghaiairport.com/cn/flights.html.

    :param direction: Departure or Arrival
    :return: None but save the data as json file. See /Data/ folder.
    """
    # Settings
    url = 'https://www.shanghaiairport.com/ajax/flights/search.aspx?action=getData'
    # Pretend to be a browser. or the status code will be 403
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/86.0.4240.111 Safari/537.36'}
    payload = {'currentPage': 1,
               'pageSize': 20,
               'flightType': 1,
               'direction': 1,
               'airCities': '',
               'airCities2': '',
               'airCompanies': '',
               'timeDays': 0,
               'timeSpan': '00:00-23:59',
               'flightNum': None}

    if direction == 'Departure':
        payload['direction'] = 1
    elif direction == 'Arrival':
        payload['direction'] = 2
    else:
        raise NameError('Error! Wrong direction setting.')

    # Get all flights.
    all_flights = []
    i = 1
    while True:
        payload['currentPage'] = i
        print('{}: Working on page {}'.format(direction, i))
        r = requests.post(url, data=payload, headers=headers)
        if r.status_code != 200:
            print('Status Code:', r.status_code)
            print(r.text)
            raise NameError('Status Code Error')
        else:
            info = r.text
            flights_info = info.split('$$$')[1]
            if len(flights_info) == 0:
                # Break until no records.
                break
            else:
                flights = json.loads(flights_info)
                all_flights += flights
                i += 1
                # 5 seconds will lead to 403 status code
                time.sleep(20)

    # Save the data
    with open('Data/{}/{}.json'.format(direction, time.asctime().replace(':', '-')), 'w', encoding='utf-8') as f:
        json.dump(all_flights, f, indent=True, ensure_ascii=False)


get_all_flights('Departure')
get_all_flights('Arrival')
