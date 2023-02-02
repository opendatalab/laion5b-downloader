# -*- coding:utf-8 -*-
# @Time: 2022/12/21 20:56
# @Author: willian
# @File：downloader.py
# @desc: 读取redis任务队列下载图片并保存

import os
import sys
import json
import time
import redis
import queue
import httpx
import socket
import setting

from loguru import logger
from setting import RedisKey
from concurrent.futures import ThreadPoolExecutor

logger_format = "{time:YYYY-MM-DD HH:mm:ss,SSS} [{thread}] {level} {file} {line} - {message}"

redis_client = redis.Redis(host=setting.redis_ip, port=setting.redis_port, db=setting.redis_db, password=setting.redis_pass, encoding="utf-8", decode_responses=True)

myname = socket.getfqdn(socket.gethostname())  # 当前机器名称
myip = socket.gethostbyname(myname).replace(".", "_")  # 当前机器IP


class BoundedThreadPoolExecutor(ThreadPoolExecutor):
    def __init__(self, max_workers, *args, **kwargs):
        super().__init__(max_workers=max_workers, *args, **kwargs)
        self._work_queue = queue.Queue(maxsize=max_workers)


class Downloader():
    def __init__(self, work_name="1"):
        self.headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-language': 'zh-CN,zh;q=0.9',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
        }
        print(work_name)
        logger.add("./logs/download_img/download_img_%s_{time:YYYY-MM-DD}.log" % work_name, format=logger_format, level="INFO", rotation="00:00", retention='7 days')
        self.pre_dir = None
        self.sleep_time = 30
        self.base_dir = setting.store_dir

    def http_get(self, url, retry_times=2):
        for i in range(retry_times):
            try:
                proxies = None
                with httpx.Client(http2=True, proxies=proxies, headers=self.headers, follow_redirects=True) as client:
                    response = client.get(url, timeout=3)
                if response.status_code >= 300 and retry_times-1 > i:
                    logger.warning(f"http请求状态码不对，需要重试当前请求次数：{i+1}    status_code：{response.status_code}    url:{url}")
                return response
            except Exception as e:
                logger.error(f"http请求失败，需要重试当前请求次数：{i+1}    url:{url}    错误信息：{e}")

    def download(self, task_json):
        status = 0
        error_msg = ""
        try:
            img_url = task_json.get("img_url")
            time.time()
            img_path = f'{self.base_dir}{time.strftime("%Y%m%d%H", time.localtime())}{task_json.get("img_path")}'.replace("//", "/")
            response = self.http_get(img_url)
            if response.status_code < 300:
                # if str(img_path).startswith("s3://"):
                #     self.ali_help.put_object(img_path, response.content)
                # else:
                if not os.path.exists(os.path.dirname(img_path)):
                    os.makedirs(os.path.dirname(img_path))
                with open(img_path, "wb") as f:
                    f.write(response.content)
            else:
                status = response.status_code
        except Exception as e:
            # 保存失败的序号和链接到指定文件 这里是多线程使用loguru是线程安全的
            status = 900
            error_msg = f"{e}"
        if status >= 300:
            task_json.update({"status": status, "error_msg": error_msg})
            task_str = json.dumps(task_json)
            logger.error(f"error_task {task_json}")
            redis_client.lpush(RedisKey.error_key, task_str)
            redis_client.incr(RedisKey.tongji_error, 1)
        else:
            redis_client.incr(RedisKey.tongji_succ, 1)

    def run(self):
        with BoundedThreadPoolExecutor(setting.thread_num) as executor:
            task_str = ""
            while True:
                try:
                    use_disk = int(redis_client.hget(RedisKey.tongji_disk, myip))
                    if use_disk > setting.stop_threshold:
                        time.sleep(30*60)
                        continue
                    task_str = redis_client.rpop(RedisKey.task_key)
                    # 接受到结束信号主程序 break
                    if task_str and "stop_this_task" in task_str:
                        break
                    if not task_str:
                        logger.info(f"没有任务了，睡眠 {self.sleep_time} 秒")
                        time.sleep(self.sleep_time)
                        continue
                    # logger.warning(f"start_task {task_str}")
                    task_json = json.loads(task_str)
                    dir_path = task_json.get("dir_path")
                    if self.pre_dir != dir_path and not os.path.exists(dir_path):
                        os.makedirs(dir_path)
                        self.pre_dir = dir_path
                except Exception as e:
                    logger.error(f"error_task {task_str}    error_info {e}")
                    redis_client.lpush(RedisKey.error_key, task_str)
                    redis_client.incr(RedisKey.tongji_error, 1)
                    break
                executor.submit(self.download, task_json)


if __name__ == '__main__':
    work_name = sys.argv[1]
    d = Downloader(work_name=work_name)
    d.run()