# -*- coding:utf-8 -*-
# @Time: 2022/12/21 20:58
# @Author: willian
# @File：add_task.py
# @desc: 读取laion5b的parquet文件添加到redis的任务队列


import os
import json
import time
import redis
import pandas as pd
import setting as se

from loguru import logger

from setting import RedisKey

logger_format = "{time:YYYY-MM-DD HH:mm:ss,SSS} [{thread}] {level} {file} {line} - {message}"

redis_client = redis.Redis(host=se.redis_ip, port=se.redis_port, db=se.redis_db, password=se.redis_pass, encoding="utf-8", decode_responses=True)
task_key = RedisKey.task_key
tongji_all = RedisKey.tongji_all


def add_task():
    logger.add("./logs/add_task/add_task_{time:YYYY-MM-DD}.log", format=logger_format, level="INFO", rotation="00:00",
               retention='60 days')
    part_done = set()
    done_path = se.done_path
    if os.path.exists(done_path):
        with open(done_path, "rb") as f:
            for line in f:
                if line:
                    part_done.add(line.strip().decode())
    while True:
        if redis_client.llen(task_key) > se.addtask_threshold:
            time.sleep(10*60)
            continue
        filename = ""
        dataset_name = ""
        base_path = se.parquet_dir
        for name in os.listdir(base_path):
            if "laion" not in name:
                continue
            dataset_name = name
            for file_name in os.listdir(f"{base_path}/{name}"):
                full_path = f"{base_path}/{name}/{file_name}"
                if full_path not in part_done:
                    filename = full_path
                    break
            if filename and dataset_name:
                break
        if not filename or not dataset_name:
            break
        # dataset_name = "laion1B-nolang"
        # filename = r"D:\part-00000-4852663c-9585-44b0-9a45-f95c2b89c792-c000.snappy.parquet"
        # filename = f"/mnt/vdc4/laion5b/parquets/laion2B-en/part-00000-5114fd87-297e-42b0-9d11-50f1df323dfa-c000.snappy.parquet"
        dir_path = f"/LAION-5B/{dataset_name}/{os.path.basename(filename).split('-')[1]}/"
        # dir_path = f"s3://bucket/LAION-5B/{dataset_name}/{os.path.basename(filename).split('-')[1]}/"
        df = pd.read_parquet(filename)
        rows = df.shape[0]
        # redis_client.incr(tongji_all, rows)       # 总数统计
        logger.info(f"开始添加task任务， task数：{rows}   part_file: {filename}")
        # #  Index(['id','SAMPLE_ID', 'URL', 'TEXT', 'HEIGHT', 'WIDTH', 'LICENSE', 'NSFW', 'similarity', 'image_suffix'], dtype='object')
        for index, row in df.iterrows():
            img_url = row.get("URL")
            image_id = eval(row.get("hash"))
            image_type = row.get("image_suffix", "jpg")
            img_path = f"{dir_path}{image_id}.{image_type}"
            task_json = {"img_path": img_path, "img_url": img_url, "file_name": filename}
            logger.debug(f"添加任务：{task_json}")
            task_str = json.dumps(task_json)
            redis_client.lpush(task_key, task_str)
        logger.info(f"任务添加完成， task数：{rows}   part_file: {filename}")
        with open(done_path, "ab+") as f:
            f.write(filename.encode())
            f.write(b"\n")
        part_done.add(filename)


if __name__ == '__main__':
    add_task()