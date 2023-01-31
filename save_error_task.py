# -*- coding:utf-8 -*-
# @Time: 2022/12/22 15:55
# @Author: willian
# @File：save_error_task.py
# @desc:

import os
import json
import time
import redis
import hashlib

from loguru import logger

logger_format = "{time:YYYY-MM-DD HH:mm:ss,SSS} [{thread}] {level} {file} {line} - {message}"

redis_client = redis.Redis(host="192.168.20.191", port=6379, db=0, encoding="utf-8", decode_responses=True)
error_key = "laion5b_task_error"

error_hash_key = "error_hash"
tongji_chongfu_key = "tongji_error_chongfu"

error_task_file_path = "./error_task/"
if not os.path.exists(error_task_file_path):
    os.makedirs(error_task_file_path)


def save_error_task():
    logger.add("./logs/save_error_task/save_error_task_{time:YYYY-MM-DD}.log", format=logger_format, level="INFO", rotation="00:00",
               retention='60 days')
    while True:
        error_task_str = redis_client.rpop(error_key)
        if not error_task_str:
            logger.info(f"没有任务了，睡眠 {30*60} 秒")
            time.sleep(30*60)
            continue
        # 接受到结束信号主程序 break
        if error_task_str and "stop_this_task" in error_task_str:
            break
        img_path = json.loads(error_task_str)["img_path"]
        img_path_md5 = md5(str(img_path))
        if redis_client.hget(error_hash_key, img_path_md5):
            redis_client.incr(tongji_chongfu_key, 1)
            continue
        redis_client.hset(error_hash_key, img_path_md5, 1)
        date = time.strftime("%Y%m%d", time.localtime())
        file_id = int(time.localtime().tm_hour/4)
        with open(f"{error_task_file_path}{date}_{file_id}.txt", "a+", encoding="utf-8") as f:
            f.write(error_task_str)
            f.write("\n")


def md5(text):
    h = hashlib.md5()
    h.update(text.encode())
    return h.hexdigest()


if __name__ == '__main__':
    save_error_task()
