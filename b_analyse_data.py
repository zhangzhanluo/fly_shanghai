import json
import pandas as pd
import numpy as np
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
    eastern_data = all_data_m[all_data_m['航空公司'] == 'China Eastern Airlines'].copy()
    eastern_data = eastern_data.set_index('dayofweek')
    eastern_data = eastern_data.loc[['Saturday', 'Monday'], :]
    spring_data = all_data_m[all_data_m['航空公司'] == 'Spring Airlines'].copy()
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

    # 实际可用航班数
    eastern_data['departure time'] = eastern_data['计划出发时间'].apply(lambda x: pd.to_datetime(x))
    eastern_data_time = eastern_data.set_index('departure time')
    available_flights = eastern_data_time['20201031 05:00:00':'20201031 12:00:00'].shape[0]
    spring_data['departure time'] = spring_data['计划出发时间'].apply(lambda x: pd.to_datetime(x))
    spring_data_time = spring_data.set_index('departure time')
    total_available_flights = spring_data_time['20201030 17:00:00':'20201031 12:00:00'].shape[0]
    results.append((available_flights, total_available_flights))

    eastern_results = []
    spring_results = []
    # Price Friendliness
    eastern_results.append(round(results[1][1] / results[1][0], 2))
    spring_results.append(1)
    # Number of Available Flights
    eastern_results.append(1)
    spring_results.append(round(results[0][1] / results[0][0], 2))
    # Number of Nice Flights
    eastern_results.append(1)
    spring_results.append(round(results[4][1] / results[4][0], 2))
    # Number of Destinations
    eastern_results.append(1)
    spring_results.append(round(results[3][1] / results[3][0], 2))
    # Hongqiao Rate
    eastern_results.append(round(results[2][0]['上海 虹桥'] / (results[2][0]['上海 虹桥'] + results[2][0]['上海 浦东']), 2))
    spring_results.append(round(results[2][1]['上海 虹桥'] / (results[2][1]['上海 虹桥'] + results[2][1]['上海 浦东']), 2))
    # 中文和负号的正常显示
    plt.rcParams['font.sans-serif'] = 'Microsoft YaHei'
    plt.rcParams['axes.unicode_minus'] = False

    # 使用ggplot的风格绘图
    plt.style.use('ggplot')

    # 构造数据
    values = eastern_results
    values_1 = spring_results
    feature = ['Price Friendliness', 'Number of Available Flights', "Number of Nice Flights", "Number of Destinations",
               "Hongqiao Rate"]

    N = len(values)

    # 设置雷达图的角度，用于平分切开一个平面
    angles = np.linspace(0, 2 * np.pi, N, endpoint=False)

    # 使雷达图封闭起来
    values = np.concatenate((values, [values[0]]))
    values_1 = np.concatenate((values_1, [values_1[0]]))
    angles = np.concatenate((angles, [angles[0]]))

    # 绘图
    fontsize = 15
    fig = plt.figure()
    # 设置为极坐标格式
    ax = fig.add_subplot(111, polar=True)
    # 绘制折线图
    ax.plot(angles, values, 'o-', linewidth=2, label='Eastern Airlines')
    ax.fill(angles, values, 'r', alpha=0.5)

    # 填充颜色
    ax.plot(angles, values_1, 'o-', linewidth=2, label='Spring Airlines')
    ax.fill(angles, values_1, 'b', alpha=0.5)

    # 添加每个特质的标签
    ax.set_thetagrids(angles * 180 / np.pi, [])
    # 设置极轴范围
    ax.set_ylim(0, 1)
    plt.text(angles[0], 1.05, 'Price\nFriendliness', va='center', fontsize=fontsize)
    plt.text(angles[1], 1.05, 'Available Flights', va='center', fontsize=fontsize)
    plt.text(angles[2]+0.1, 1.35, 'Nice Flights', va='center', fontsize=fontsize)
    plt.text(angles[3]-0.1, 1.35, 'Destinations', va='center', fontsize=fontsize)
    plt.text(angles[4]-0.2, 1.05, 'Hongqiao Rate', va='center', fontsize=fontsize)
    # 添加标题
    # plt.title('活动前后员工状态')
    # 增加网格纸
    ax.grid(True)
    plt.tight_layout()
    # plt.legend(loc='lower right')
    plt.savefig('Pics/Radar chart.png', dpi=300)
    plt.show()
