# -*- coding:utf-8 -*-
# @Time: 2022/12/22 15:55
# @Author: willian
# @File：save_error_task.py
# @desc: 消费下载错误队列并存储到本地持久化

import os
import time
import redis
import hashlib
import setting

from loguru import logger
from setting import RedisKey

logger_format = "{time:YYYY-MM-DD HH:mm:ss,SSS} [{thread}] {level} {file} {line} - {message}"

redis_client = redis.Redis(host="192.168.20.191", port=6379, db=0, encoding="utf-8", decode_responses=True)

if not os.path.exists(setting.store_error_dir):
    os.makedirs(setting.store_error_dir)


def save_error_task():
    logger.add("./logs/save_error_task/save_error_task_{time:YYYY-MM-DD}.log", format=logger_format, level="INFO", rotation="00:00",
               retention='60 days')
    while True:
        error_task_str = redis_client.rpop(RedisKey.error_key)
        if not error_task_str:
            logger.info(f"没有任务了，睡眠 {30*60} 秒")
            time.sleep(30*60)
            continue
        # 接受到结束信号主程序 break
        if error_task_str and "stop_this_task" in error_task_str:
            break
        date = time.strftime("%Y%m%d", time.localtime())
        file_id = int(time.localtime().tm_hour/4)
        with open(f"{setting.store_error_dir}{date}_{file_id}.txt", "a+", encoding="utf-8") as f:
            f.write(error_task_str)
            f.write("\n")


def md5(text):
    h = hashlib.md5()
    h.update(text.encode())
    return h.hexdigest()


if __name__ == '__main__':
    save_error_task()
