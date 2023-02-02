# -*- coding:utf-8 -*-
# @Time: 2022/12/21 21:01
# @Author: willian
# @File：monitor_disk.py
# @desc: 监控磁盘使用情况

import time
import redis
import socket
import shutil
import setting

from loguru import logger

from setting import RedisKey

logger_format = "{time:YYYY-MM-DD HH:mm:ss,SSS} [{thread}] {level} {file} {line} - {message}"

redis_client = redis.Redis(host=setting.redis_ip, port=setting.redis_port, db=setting.redis_db, password=setting.redis_pass, encoding="utf-8", decode_responses=True)
tongji_disk = RedisKey.tongji_disk

myname = socket.getfqdn(socket.gethostname())  # 当前机器名称
myip = socket.gethostbyname(myname).replace(".", "_")  # 当前机器IP


def monitor_disk():
    logger.add("./logs/monitor_disk/monitor_disk_{time:YYYY-MM-DD}.log", format=logger_format, level="INFO",
               rotation="00:00", retention='60 days')
    while True:
        gb = 1024 ** 3  # GB == gigabyte
        total_b, used_b, free_b = shutil.disk_usage(setting.monitor_disk)  # 查看磁盘的使用情况
        logger.info(f"当前机器：{myname}    当前机器IP:{myip}")
        logger.info('总的磁盘空间: {:6.2f} GB '.format(total_b / gb))
        logger.info('已经使用的 : {:6.2f} GB '.format(used_b / gb))
        logger.info('未使用的 : {:6.2f} GB '.format(free_b / gb))
        redis_client.hset(tongji_disk, myip, int(used_b/gb))
        time.sleep(30*60)


if __name__ == '__main__':
    monitor_disk()
    '''
        pip3 install  retrying   pyarrow
        pip3 install redis httpx httpx[http2] httpx[socks] pandas loguru fastparquet
        pip3 install httpx
        pip3 install httpx[http2]
        pip3 install httpx[socks]
        pip3 install pandas
        pip3 install loguru
        pip3 install fastparquet
    '''