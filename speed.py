# -*- coding:utf-8 -*-
# @Time: 2022/12/21 23:42
# @Author: willian
# @File：speed.py
# @desc:

import time
import redis


redis_client = redis.Redis(host="192.168.20.191", port=6379, db=0, encoding="utf-8", decode_responses=True)
error = "laion5b_tongji_error"
succ = "laion5b_tongji_succ"


def speed():
    while True:
        s_c = int(redis_client.get(error)) + int(redis_client.get(succ))
        time.sleep(10)
        e_c = int(redis_client.get(error)) + int(redis_client.get(succ))
        c = e_c-s_c
        print(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}   10秒钟处理：{c}  处理速率：{c/10}")


if __name__ == '__main__':
    speed()
