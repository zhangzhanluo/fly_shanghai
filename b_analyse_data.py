import json
import pandas as pd
from matplotlib import pyplot as plt

plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']


def load_all_data():
    folders = ['Data/Arrival/', 'Data/Departure/']
    files = ['Monday 20-10-26.json',
             'Tuesday 20-10-27.json',
             'Wednesday 20-10-28.json',
             'Thursday 20-10-29.json',
             'Friday 20-10-30.json',
             'Saturday 20-10-31.json',
             'Sunday 20-11-01.json']

    _all_data = []
    for folder in folders:
        for file in files:
            with open(folder + file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                data_df = pd.DataFrame(data)
                data_df['方向'] = folder.split('/')[1]
                data_df['dayofweek'] = file.split(' ')[0]
                _all_data.append(data_df)
    _all_data = pd.concat(_all_data, axis=0)
    return _all_data


def count_numbers(term, _data):
    grouper = _data.groupby(term)
    names = []
    numbers = []
    for name, group in grouper:
        names.append(name)
        numbers.append(group.shape[0])
    _numbers, _names = (list(t) for t in zip(*sorted(zip(numbers, names))))
    return _names, _numbers


# 分析总航班数
def plot_air_company(_data):
    names, numbers = count_numbers('航空公司', _data)
    names = names[14:]
    numbers = numbers[14:]
    plt.figure(figsize=(8, 10))
    plt.barh(names, numbers)
    plt.xlabel('Departure Flights', fontsize='12')
    for y, x in enumerate(numbers):
        plt.text(x + 30, y - 0.15, x)
    plt.xlim([0, 2000])
    plt.tight_layout()
    plt.savefig('Pics/航空公司总航班数分析.png', dpi=300)
    plt.show()


# 分析目的地，似乎有明显的错误，例如没有大兴机场记录
def plot_destinations(_data):
    names, numbers = count_numbers('目的地', _data)
    names = names[-30:]
    numbers = numbers[-30:]
    plt.figure(figsize=(8, 10))
    plt.barh(names, numbers)
    plt.xlabel('Departure Flights', fontsize='12')
    for y, x in enumerate(numbers):
        plt.text(x + 5, y - 0.2, x)
    plt.xlim([0, 430])
    plt.tight_layout()
    plt.savefig('Pics/目的地总航班数分析.png', dpi=300)
    plt.show()


def plot_dayofweek(_data):
    names, numbers = count_numbers('dayofweek', _data)
    correct_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    correct_names_n = [names.index(x) for x in correct_names]
    correct_numbers = [numbers[i] for i in correct_names_n]
    plt.bar(correct_names, correct_numbers)
    for x, y in enumerate(correct_numbers):
        plt.text(x - 0.25, y + 5, y)
    plt.ylim([700, 800])
    plt.ylabel('Departure Flights')
    plt.xlabel('Day of Week')
    plt.tight_layout()
    plt.savefig('Pics/一周航班数量变化.png', dpi=300)
    plt.show()


def plot_airport(_data):
    names, numbers = count_numbers('出发地代号', _data)
    plt.bar(names, numbers)
    for x, y in enumerate(numbers):
        plt.text(x, y + 30, y, horizontalalignment='center')
    plt.xlabel('Airport')
    plt.ylabel('Departure Flights')
    plt.savefig('Pics/机场总航班数分析.png', dpi=300)
    plt.show()


if __name__ == '__main__':
    all_data = load_all_data()
    departure_data = all_data[all_data['航向'] == '出发']
    all_data_m = departure_data.copy()
    all_data_m.replace('上海航空公司', '中国东方航空公司', inplace=True)
    all_data_m.replace('中国东方航空公司', 'China Eastern Airlines', inplace=True)
    all_data_m.replace('中国春秋航空公司', 'Spring Airlines', inplace=True)
    eastern_data = all_data_m[all_data_m['航空公司'] == 'China Eastern Airlines']
    eastern_data = eastern_data.set_index('dayofweek')
    eastern_data = eastern_data.loc[['Saturday', 'Monday'], :]
    spring_data = all_data_m[all_data_m['航空公司'] == 'Spring Airlines']
    results = [(len(eastern_data), len(spring_data)), (3666, 2999)]
    airport_info = []
    destination_num = []
    for data in [eastern_data, spring_data]:
        airports = {}
        grouper = data.groupby('出发地')
        for k, d in grouper:
            airports[k] = d.shape[0]
        airport_info.append(airports)
        destination_num.append(len(set(data['目的地'].tolist())))
    results += [airport_info, destination_num]

