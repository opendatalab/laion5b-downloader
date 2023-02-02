


# LAION-5B下载媒体数据脚本
> LAION-5B parquet 下载地址：https://opendatalab.com/LAION-5B
> 
> 更多数据集下载请到：https://opendatalab.com/  （OpenDataLab 是有影响力的数据开源开放平台，公开数据集触手可及。）
---
### 注意事项
>* 请务必使用上述提到的parquet下载地址 然后使用此脚本下载
>* 此parquet是经过大数据平台分析、计算之后合并出来的大宽表，对后续使用下载都比较友好
>* 脚本不依赖大数据平台，直接可以单机或者分布式高速下载处理

---
### 设备及工作环境准备
>* 服务器64核128GB 两台
>* python3
>* redis  # 这里默认ip为192.168.0.1 端口为6379
---
### 脚本运行
    # 队列添加任务parquet在哪台机器只在此机器运行一个就行 
    python3 add_task.py
    # monitor_disk.py 每个下载机器开启一个程序
    python monitor_disk.py
    # 开启10个下载进程
    for i in {0..10}; do echo "nohup python3 download_img.py $i >/dev/null 2>&1 &" | bash; done
    # save_error_task.py 把错误队列数据以文本形式保存到本地 根据需要是否开启
    python3 save_error_task.py
    # 下载情况查看
    python3 speed.py
---
### 配置文件说明 setting.py
    # redis连接配置
    redis_ip = "192.168.0.1"
    redis_port = 6379
    redis_db = 0
    redis_pass = "****123***"
    
    
    # 使用到的 redis key 配置信息
    class RedisKey:
        task_key = "laion5b_task"                 # 存放任务队列
        tongji_all = "laion5b_tongji_all"         # 统计已经加入了多少
        error_key = "laion5b_task_error"          # 下载失败的任务队列
        tongji_error = "laion5b_tongji_error"     # 统计下载失败数
        tongji_succ = "laion5b_tongji_succ"       # 统计下载完成数
        tongji_disk = "tongji_worker_disk"        # 监控磁盘使用量
    
    
    # parquet 目录配置 add_task.py 使用  样例：/mnt/vdb/laion5b/parquet/laion1B-nolang/0000~0128.parquet  /mnt/vdb/laion5b/parquet/laion2B-en/0000~0128.parquet
    parquet_dir = "/mnt/vdb/laion5b/parquet"
    # 添加任务时候队列中少于5000000 开始执行添加任务
    addtask_threshold = 5000000
    # 添加过后的parquet路径写入 done_part.txt
    done_path = "./done_part.txt"
    
    
    # monitor_disk.py  查看存储空间占用情况
    monitor_disk = '/mnt/vdc'
    
    
    # downloader.py  下载的图片存储的目录 后续会拼接 laion1B-nolang  laion1B-nolang 等目录
    store_dir = "/mnt/vdc/laion5b/data/"
    # 这里设置磁盘使用阈值是5000 GB 使用超过此阈值爬虫便停止下载直到空间释放出来  单位：GB
    stop_threshold = 5000
    # 单进程下载多线程数 默认：32
    thread_num = 32
    
    # save_error_task.py  本地持久化redis错误队列数据 根据需要是否持久化 一般要开启此程序 否则错误较多redis占用较高
    store_error_dir = "./error_task/"
---
### 下载用时统计
> laion5b 媒体数据量在58亿多，使用64核128GB带宽750MB  中间调试运行用时30天下载完成
> 
> cpu基本上只使用32个，每个占用80%左右。内存128GB占用90GB左右。带宽占满750GB下载速度达到90+MB每秒。 50进程32线程。
> 
> 建议合理使用服务器资源配置，让cup、内存和带宽在程序的运行下充分占用，下载速度还能更快。
>
----