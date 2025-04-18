import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr

import pytz
import requests
import json
from datetime import datetime


def send_email(filename, current_date):
    # 设置发件人和收件人
    from_email = "unms_jenkins@wiscom.com.cn"
    from_password = "Unmsjenkins123"

    # 朱开市、袁亚洁
    # recipients = ["20230904064@wiscom.com.cn", "yjyuan@wiscom.com.cn"]
    recipients = ["20230904061@wiscom.com.cn"]

    try:
        # 创建邮件对象
        msg = MIMEMultipart()
        msg['To'] = ",".join(recipients)
        msg['Subject'] = current_date.strftime("%Y-%m-%d") + "天气数据报告"  # 邮件主题

        # 添加附件
        attachment = open(filename, "rb")
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f"attachment; filename= {filename}")
        msg.attach(part)

        # 设置邮件正文内容
        email_content = f"""
            你好，江苏省今日极端天气文件。详情请查阅附件。
            执行命令：psql -U postgres -d envs -f """ + filename + """
            此为自动发送邮件，请勿回复。

            谢谢！
            """
        msg.attach(MIMEText(email_content, "plain"))
        msg['From'] = formataddr(pair=("网管研发部", from_email))

        # 连接到SMTP服务器并发送邮件
        server = smtplib.SMTP_SSL("smtp.exmail.qq.com", 465)  # 修改为你的SMTP服务器和端口号
        server.login(from_email, from_password)  # 修改为发件人邮箱的授权码或密码
        server.sendmail(from_email, recipients, msg.as_string())
        server.quit()
        print("邮件发送成功！")
    except smtplib.SMTPException as e:
        print('邮件发送失败！', e)


# 请求接口
url = "https://weather.cma.cn/api/map/alarm"
response = requests.get(url)

# 检查请求是否成功
if response.status_code == 200:
    data = response.json().get("data", [])

    # 获取当前日期
    record_time = datetime.now().strftime('%Y-%m-%d')
    current_date = datetime.now(pytz.timezone("Asia/Shanghai")).date()

    # 格式化数据为SQL插入语句
    weather_info = json.dumps(data, ensure_ascii=False)  # 确保中文字符正确编码
    sql_insert = f'INSERT INTO weather_extreme("record_time", "weather_info") VALUES (\'{record_time}\', \'{weather_info}\');\n'

    # 保存到SQL文件
    file_name = 'weather_extreme_' + record_time + '.sql'
    with open(file_name, 'w', encoding='utf-8') as file:
        file.write(sql_insert)

    print("数据已成功保存到 {} 文件中。",file_name)
    send_email(file_name, current_date)
else:
    print(f"请求失败，状态码：{response.status_code}")
