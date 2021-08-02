import requests as rq
from time import time as tm
from re import findall as fa
from pylsy import pylsytable as pt
from matplotlib import pyplot as pp
from bs4 import BeautifulSoup as Bs
from tkinter.messagebox import showerror as se


def fore(pinyin: str):
    header = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                            "Chrome/92.0.4515.107 Safari/537.36 Edg/92.0.902.55"}
    page_l = rq.get("https://www.tianqi.com/" + pinyin, headers=header)
    page_l.encoding = page_l.apparent_encoding
    page_l = page_l.text  # 获取页面信息

    page_s = Bs(page_l, "html.parser")
    forecast = page_s.findAll(class_="weatherbox")[0].findAll(class_="right")[0]
    twty_h = {"crs": [], "wen": [], "wind": [], "fl": [], "time": []}

    n = 0
    list_ = forecast.findAll(class_="twty_hour")[0].div.findAll("div")
    item = []
    for i in list_:  # 筛掉多余的信息
        n += 1
        if n % 2 == 1:
            item.append(i)

    n = 0
    for i in item:
        n += 1
        for t in i.findAll(class_="zxt_shuju" + str(n))[0].ul.findAll("li"):
            twty_h["wen"].append(t.span.string)
        sa = i.findAll(class_="txt")
        for t in sa[0].findAll("li"):
            twty_h["crs"].append(t.string)
        for t in sa[1].findAll("li"):
            twty_h["wind"].append(t.string)
        for t in sa[2].findAll("li"):
            twty_h["fl"].append(t.string)
        for t in sa[3].findAll("li"):
            twty_h["time"].append(t.string[:3])

    for o in range(len(twty_h["wen"])):  # 将数据转成整数型并返回
        twty_h["wen"][o] = int(twty_h["wen"][o])
        twty_h["time"][o] = twty_h["time"][o][:-1]

    print("未来 24 小时天气预报：")
    tb = pt(["时间", "温度", "天气", "风向", "风力"])
    tb.add_data("时间", twty_h["time"])
    tb.add_data("温度", twty_h["wen"])
    tb.add_data("天气", twty_h["crs"])
    tb.add_data("风向", twty_h["wind"])
    tb.add_data("风力", twty_h["fl"])
    print(tb)

    return [[twty_h["time"], twty_h["wen"]], page_l, page_s]


def fore2(page_p: Bs):
    weather = page_p.findAll(class_="day7 hide twty_hour")[0]
    svn = {"date": [], "highest": [], "lowest": [], "crs": [], "wd": []}
    for t in weather.findAll(class_="week")[0].findAll("li"):
        svn["date"].append(t.b.string)
    for t in weather.findAll(class_="txt txt2")[0].findAll("li"):
        svn["crs"].append(t.string)
    for t in weather.findAll(class_="zxt_shuju")[0].findAll("li"):
        svn["highest"].append(t.span.string + "℃")
        svn["lowest"].append(t.b.string + "℃")
    for t in weather.findAll(class_="txt")[1].findAll("li"):
        svn["wd"].append(t.string)

    print()
    print("未来 7 天天气预报：")
    tb = pt(["日期", "天气", "最高温", "最低温", "风向"])
    tb.add_data("日期", svn["date"])
    tb.add_data("天气", svn["crs"])
    tb.add_data("最高温", svn["highest"])
    tb.add_data("最低温", svn["lowest"])
    tb.add_data("风向", svn["wd"])
    print(tb)

    for t in range(7):  # 将数据转换成数值型以便绘制图表
        svn["highest"][t] = int(svn["highest"][t][:-1])
        svn["lowest"][t] = int(svn["lowest"][t][:-1])

    return [svn["date"], svn["highest"], svn["lowest"]]


def life(page_p: Bs):
    print()
    print("生活建议：")
    weather = page_p.findAll(class_="weather_life300")[0].ul
    sug = weather.findAll("b")
    item = weather.findAll("p")
    for i in range(len(sug)):
        print("    %s：\t%s" % (sug[i].string, item[i].string))


def get_weather(page_p: Bs):
    weather = page_p.findAll(class_="weather_info")[0]

    print()  # 输出一个空行以区别于时间
    print(weather.findAll(class_="week")[0].string[:-1])

    temp = weather.findAll(class_="now")[0]
    print("当前天气：")
    print("    温度：\t%s℃" % temp.b.string)

    iteration = weather.findAll(class_="shidu")[0].children
    for i in iteration:
        info = i.string
        index = info.find("：")
        print("    %s：\t%s" % (info[:index], info[index + 1:]))

    info = weather.findAll(class_="kongqi")[0]
    info = info.h5.string
    index = info.find("：")
    print("    空气：\t%s" % info[index + 1:])
    print()  # 输出一个空行以区别于时间

    print("今天天气：")
    today = str(weather.findAll(class_="weather")[0].span)
    today = fa(pattern=r"<span>.+?</span>", string=today)[0][6:-7]
    wea = fa(pattern=r"<b>.+?</b>", string=today)[0][3:-4]

    print("    " + today[len(wea) + 7:])
    print("    " + wea)


if __name__ == "__main__":
    while True:
        try:
            val = fore(input("你想查哪里的天气？请输入拼音：").lower())
            val2 = fore2(val[2])

            life(val[2])
            get_weather(val[2])

            value1 = val[0]
            value2 = val2

            fig = pp.figure("未来温度预报", figsize=(14, 7))
            ax1 = fig.add_subplot(121)
            ax1.set(title="未来 24 小时温度预报", xlabel="时间 / 时", ylabel="温度 / 摄氏度")
            ax1.plot(value1[0], value1[1], color="green", marker="o")
            ax1.text(1, 2, "wwe")
            ax1.grid()

            ax2 = fig.add_subplot(122)
            ax2.set(title="未来 7 天温度预报", xlabel="时间 / 时", ylabel="温度 / 摄氏度")
            ax2.plot(value2[0], value2[1], color="red", marker="o")
            ax2.plot(value2[0], value2[2], color="blue", marker="o")
            ax2.grid()
            ax2.legend(["最高温", "最低温"])

            name = str(tm()) + ".svg"  # 保存为矢量图
            pp.savefig(name, format="svg")

            pp.show()  # 显示图表
        except:
            print("出错了:-(")
            print("1.请检查拼写是否正确")
            print("2.请检查网络是否通畅")
