import redis

# 连接到Redis
r = redis.StrictRedis(host="172.18.37.212", port=6379, password="Unms@123", decode_responses=True)

pattern = ['service_ha:info:*', 'service_ha:status:*']

# 使用scan方法进行模糊匹配
for item in pattern:
    for key in r.scan_iter(item):
        print(key)
        r.sadd(item.rsplit(":", 1)[0] + "_key", key)
    print('\n')
