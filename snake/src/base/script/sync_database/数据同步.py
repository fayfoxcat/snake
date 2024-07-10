import datetime as datetime
from typing import List

import pymssql as mssql
import pymysql as mysql
import yaml

f = open('DataBase.yaml')
data = f.read()
db_config = yaml.load(data, Loader=yaml.FullLoader)

# 源数据库
ms_db = mssql.connect(host=db_config['sqlserver']['host'],
                      user=db_config['sqlserver']['user'],
                      password=str(db_config['sqlserver']['password']),
                      database=db_config['sqlserver']['db'],
                      charset='utf8')
# 创建游标对象,并设置返回数据的类型为字典
ms_cursor = ms_db.cursor(as_dict=True)
# 设置立即操作
ms_db.autocommit(True)

# sql = 'SELECT top 1* FROM ( SELECT top 100* FROM PupilPersonalDetails ) student'
sql = 'SELECT * FROM PupilPersonalDetails'
ms_cursor.execute(sql)
original_data = ms_cursor.fetchall()
array: List = [line for line in original_data]

ms_db.close()
ms_cursor.close()
# 目标数据库
mysql_db = mysql.connect(host=db_config['mysql']['host'],
                         port=db_config['mysql']['port'],
                         user=db_config['mysql']['user'],
                         password=str(db_config['mysql']['password']),
                         database=db_config['mysql']['db'],
                         charset='utf8')
mysql_cursor = mysql_db.cursor()
now = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
for i in array:
    item = {'student_id': 0,
            'student_num': 0,
            'name': '',
            'en_name': '',
            'first_name': '',
            'last_name': '',
            'email': '',
            'password': '',
            'country_id': '',
            'id_type': '',
            'moniker': '',
            'avatar_url': '',
            'gender': '',
            'birthday': '',
            'status': '',
            'section_id': '',
            'next_section_id': '',
            'school_id': '',
            'campus_id': '',
            'out_date': '',
            'province_code': '',
            'city_code': '',
            'district_code': '',
            'address': '',
            'house_group_id': '',
            'boarding': '',
            'school_bus': '',
            'bus_route': '',
            'delete_flag': 0000,
            'creator': 1,
            'create_time': now,
            'modifier': 1,
            'modify_time': now,
            'enter_year': '',
            'remark': '',
            'trans_reason_id': '',
            'trans_remark': '',
            'last_class_date': '',
            'to_school': '',
            'application_id': '',
            'follower': '',
            'last_login_time': '',
            'citic_bank_acc_id_num': '',
            'medical_tag': 0,
            'medium_tag': 0,
            'order_status': '',
            'enter_date': '',
            'int_apply_semesterId': '',
            'order_type': '',
            'surname': '',
            'school_roll_status': '',
            'school_roll_note': '',
            'bus_site': '',
            'order_satus': 0}
    save_sql = 'insert into `m_student`(`student_id`, `student_num`, `name`, `en_name`,`first_name`, `last_name`,' \
               ' `email`, `password`,`country_id`, `id_type`, `id_num`, `avatar_url`,`gender`, `birthday`, `status`, ' \
               '`section_id`,`next_section_id`, `school_id`, `campus_id`, `out_date`,`province_code`, `city_code`, ' \
               '`district_code`,`address`,`house_group_id`, `boarding`, `school_bus`, `bus_route`,`bus_site`, ' \
               '`delete_flag`, `creator`,`create_time`,`modifier`, `modify_time`, `enter_year`, `remark`,' \
               '`trans_reason_id`, `trans_remark`, `last_class_date`, `to_school`,`application_id`, `follower`, ' \
               '`last_login_time`, `citic_bank_acc_id_num`,`medical_tag`, `medium_tag`, `order_status`, `enter_date`,' \
               '`int_apply_semesterId`, `order_type`, `surname`,`moniker`,`school_roll_status`, `school_roll_note`) ' \
               'values(%d,%s,%s,%s,%s,%s,%s,%s,%d,%s,%s,%s,%s,%s,%s,%d,%d,%d,%d,%s,%s,%s,%s,%s,%d,%s,%s' \
               ',%d,%d,%s,%d,%s,%d,%s,%s,%s,%d,%s,%s,%s,%d,%d,%s,%s,%d,%d,%s,%s,%d,%s,%s,%s,%s,%s)'
    mysql_cursor.execute(save_sql, item)
    mysql_cursor.commit()
