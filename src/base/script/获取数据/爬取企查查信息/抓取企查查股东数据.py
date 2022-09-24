import json
import os
import random
import sys
import requests
import time
import pandas as pd
from bs4 import BeautifulSoup
from requests import HTTPError

# 读取配置文件
with open("ini.json", 'r', encoding='utf8') as ini:
    configuration = json.load(ini)

# 保持会话
sess = requests.session()
default = sess.get('https://www.qcc.com', headers=configuration.get("headers"))
# 添加headers
afterLogin_headers = configuration.get("headers")


# 获取网页信息
def get_company_message(company):
    # 获取查询到的网页内容（全部）
    search = sess.get('https://www.qcc.com/search?key={}'.format(company), headers=afterLogin_headers, timeout=10)
    search.raise_for_status()
    search.encoding = 'utf-8'
    soup = BeautifulSoup(search.text, features="html.parser")
    href = soup.find_all('a', {'class': 'title'})[0].get('href')
    time.sleep(random.randint(2, 6))
    # 获取查询到的网页内容（全部）
    details = sess.get(href, headers=afterLogin_headers, timeout=10)
    details.raise_for_status()
    details.encoding = 'utf-8'
    time.sleep(random.randint(2, 6))
    return BeautifulSoup(details.text, features="html.parser")


# 解析数据
def message_to_df(message, company):
    shareholders = message.find("div", class_="app-tree-table").find_all(name="tr")[1:]
    data_list = []
    for shareholder in shareholders:
        record = {'公司名称': company}
        td_list = shareholder.find_all(name="td")
        try:
            record['股东名称'] = td_list[1].find(name="span", class_="name").text
        except:
            try:
                record['股东名称'] = td_list[1].text
            except:
                record['股东名称'] = ""
        try:
            record['持股比例'] = td_list[2].text
        except:
            record['持股比例'] = ""
        try:
            record['持股数（股）'] = td_list[3].text
        except:
            record['持股数（股）'] = ""
        try:
            record['是否私募'] = "是" if "私募基金" in td_list[1].find(name="div", class_="tags").text else "否"
        except:
            record['是否私募'] = "否"
        try:
            record['关联产品/机构'] = td_list[4].text
        except:
            record['关联产品/机构'] = ""
        data_list.append(record)

    # 查询信息不完全补偿
    if "登录查看全部信息" in str(data_list):
        enterprise.append(company)
    else:
        return pd.DataFrame(data_list)


# 打印执行信息
def result(total, fail):
    print("执行总数：" + str(len(set(total))))
    print("未完成数：" + str(len(set(fail))))
    try:
        print("失败占比：" + str('{:.2%}'.format(len(set(fail)) / len(set(total)))))
        print("未完成详情：" + (os.path.abspath('') + "/" + configuration.get("path").get("error")).replace("\\", "/"))
        out = pd.DataFrame(set(fail))
        out.to_csv(configuration.get("path").get("error"), index=False, header=False)
    except:
        pass


# 导入企业信息记录
complete = []
original = pd.read_excel(configuration.get("path").get("input"))
enterprise = original['发行人全称'].tolist()

for index, item in enumerate(enterprise):
    try:
        messages = get_company_message(item)
        df = message_to_df(messages, item)
        if item == enterprise[0]:
            df.to_csv(configuration.get("path").get("output"), index=False, header=True)
        else:
            df.to_csv(configuration.get("path").get("output"), mode='a+', index=False, header=False)
        complete.append(item)
    except HTTPError:
        print("\n\033[1;31m 登录信息已失效或访问受限，请检查账号状态！\033[0m\n")
        result(enterprise, list(set(enterprise) ^ set(complete)))
        sys.exit(0)
    except:
        pass
    sys.stdout.write('\r' + str('进度：{:.2%}'.format((index + 1) / len(enterprise))))
    sys.stdout.flush()
    time.sleep(1)

print('\n')
result(enterprise, list(set(enterprise) ^ set(complete)))
