import json
import threading
from locust import HttpUser, task, between
import requests as r


class AtomicInteger:
    def __init__(self, value=0):
        self._value = int(value)
        self._lock = threading.Lock()

    def inc(self, d=1):
        with self._lock:
            self._value += int(d)
            return self._value

    def get_and_inc(self, d=1):
        value = self._value
        with self._lock:
            self._value += int(d)
        return value

    def dec(self, d=1):
        return self.inc(-d)

    @property
    def value(self):
        with self._lock:
            return self._value

    @value.setter
    def value(self, v):
        with self._lock:
            self._value = int(v)


data = open('src/base/single/单板运行状态.json')
# 将json格式的数据映射成list的形式
users = json.load(data)
index = AtomicInteger()
print(len(users))


class MeetingsApplicationTest(HttpUser):
    wait_time = between(3, 5)

    def __init__(self, *args, **kwargs):
        HttpUser.__init__(self, *args, **kwargs)
        self.__user = users[index.get_and_inc()]
        login_res = r.post('http://192.168.60.100:4013/login/', json={
            "mobile": self.__user["mobile"],
            "password": '123qwe.'
        }, headers={
            'X-SchoolId': '2'
        }).json()
        print(login_res)
        self.__token = login_res["token"]

    def get_application_list(self):
        self.client.get(
            f'http://192.168.60.100:4013/meetings/list?pageCurrent=1&pageSize=30&studentId={self.__user["studentId"]}',
            headers={
                'X-SchoolId': '2',
                'X-Token': self.__token
            })\

    @task
    def get_application_list(self):
        self.client.get(f'http://192.168.60.100:4013/meetings?meetingId=47&studentId={self.__user["studentId"]}',
            headers={
                'X-SchoolId': '2',
                'X-Token': self.__token
            })


