import psycopg2

try:
    conn = psycopg2.connect(
        database="ENVS",
        user="jssd",
        password="jssd123",
        host="172.18.37.202",
        port="54321"
    )
    print("数据库连接成功")
except Exception as e:
    print(e)
