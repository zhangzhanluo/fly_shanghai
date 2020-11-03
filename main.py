import time
import json
import requests
from datetime import date, timedelta
from copyheaders import headers_raw_to_dict

import re  # 实现正则表达式
import execjs  # 执行js代码

user_agent_global = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
'Chrome/86.0.4240.111 Safari/537.36'
url_global = 'https://www.shanghaiairport.com/ajax/flights/search.aspx?action=getData'


def get_all_flights(direction='Departure'):
    """
    get all flight information from https://www.shanghaiairport.com/cn/flights.html.

    :param direction: Departure or Arrival
    :return: None but save the data as json file. See /Data/ folder.
    """
    # Pretend to be a browser. or the status code will be 403
    headers = {
        'User-Agent': user_agent_global}
    headers_for_521 = b'''Accept: */*
Accept-Encoding: gzip, deflate, br
Accept-Language: zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7,zh-TW;q=0.6
Connection: keep-alive
Content-Length: 130
Content-Type: application/x-www-form-urlencoded; charset=UTF-8
Cookie: __jsluid_s=719744134dbd726e737da2e802314e54; Hm_lvt_d7682ab43891c68a00de46e9ce5b76aa=1603701341; shjc_indexNoticeHasRead=1; __jsl_clearance_s=1604362484.991|0|0llgShnUXtFaVn%2B5MtH4astjH6s%3D; ASP.NET_SessionId=e3liyv55hzssjxmwngl2he45; SERVERID=ad6585a6b63a4adcbf5c5362de3f1317|1604362495|1604362486
Host: www.shanghaiairport.com
Origin: https://www.shanghaiairport.com
Referer: https://www.shanghaiairport.com/cn/flights.html
Sec-Fetch-Dest: empty
Sec-Fetch-Mode: cors
Sec-Fetch-Site: same-origin
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36
X-Requested-With: XMLHttpRequest'''
    payload = {'currentPage': 1,
               'pageSize': 20,
               'flightType': 1,
               'direction': 1,
               'airCities': '',
               'airCities2': '',
               'airCompanies': '',
               # -1 means yesterday
               'timeDays': -1,
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
        r = requests.post(url_global, data=payload, headers=headers)

        if r.status_code == 200:
            pass
        elif r.status_code == 521:
            r = requests.post(url_global, data=payload, headers=headers_raw_to_dict(headers_for_521))
            if r.status_code != 200:
                raise NameError('521 - Status Code Error')
        else:
            print('Status Code:', r.status_code)
            print(r.text)
            raise NameError('Status Code Error')

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
            time.sleep(15)

    # Save the data
    yesterday = date.today() + timedelta(days=-1)
    with open('Data/{}/{}.json'.format(direction, yesterday.strftime('%A %y-%m-%d')), 'w', encoding='utf-8') as f:
        json.dump(all_flights, f, indent=True, ensure_ascii=False)


get_all_flights('Departure')
get_all_flights('Arrival')
