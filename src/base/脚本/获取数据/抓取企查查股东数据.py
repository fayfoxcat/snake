import random
import sys

from bs4 import BeautifulSoup
import requests
import time
import pandas as pd

# 保持会话
from requests import HTTPError

sess = requests.session()

# 添加headers（header为自己登录的企查查网址，输入账号密码登录之后所显示的header，此代码的上方介绍了获取方法）
afterLogin_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                    'Chrome/105.0.0.0 Safari/537.36 Edg/105.0.1343.27',
                      'cookie': 'QCCSESSID=764bf33914a82be15712f79610; qcc_did=8ea235a1-33a1-4982-93fb-ee4dc3be4702; '
                                'acw_tc=0884322b16626849078076761e6f349d37c9d92bb28f63dc5d081a209d'
                      }


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
    for item in shareholders:
        record = {'公司名称': company}
        td_list = item.find_all(name="td")
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
        companys.append(company)
    else:
        return pd.DataFrame(data_list)


# 导入企业信息记录
errors = []
df_companys = pd.read_excel('C:/Users/cat/Desktop/原始数据.xlsx')
companys = df_companys['发行人全称'].tolist()

for index, item in enumerate(companys):
    try:
        messages = get_company_message(item)
        df = message_to_df(messages, item)
        if item == companys[0]:
            df.to_csv('C:/Users/cat/Desktop/股东数据.csv', index=False, header=True)
        else:
            df.to_csv('C:/Users/cat/Desktop/股东数据.csv', mode='a+', index=False, header=False)
    except HTTPError:
        print("\033[1;31m 登录信息已失效或访问受限，请检查账号状态！\033[0m")
        print("执行总数：" + str(len(set(companys))))
        print("未完成数：" + str(len(set(errors))))
        try:
            print("失败占比：" + str('{:.2%}'.format(len(set(errors)) / len(set(companys)))))
            print("未完成详细信息：" + str(set(errors)))
        except:
            pass
        sys.exit(0)
    except:
        errors.append(item)
    sys.stdout.write('\r' + str('进度：{:.2%}'.format((index + 1) / len(companys))))
    sys.stdout.flush()
    time.sleep(1)

print("\n执行总数：" + str(len(set(companys))))
print("未完成数：" + str(len(set(errors))))
try:
    print("失败占比：" + str('{:.2%}'.format(len(set(errors)) / len(set(companys)))))
    print("未完成详细信息：" + str(set(errors)))
except:
    pass
