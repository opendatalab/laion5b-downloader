<div align="center">
<article style="display: flex; flex-direction: column; align-items: center; justify-content: center;">
    <p align="center"><img width="300" src="https://user-images.githubusercontent.com/25022954/209616423-9ab056be-5d62-4eeb-b91d-3b20f64cfcf8.svg" /></p>
    <h1 style="width: 100%; text-align: center;"></h1>
    <p align="center">
        <a href="./README-CN.md" >简体中文</a>  | English
    </p>
</article>
</div>


# LAION-5B Download Media Data Script
> LAION-5B parquet download address: https://opendatalab.com/LAION-5B
> 
> For more datasets to download, please go to: https://opendatalab.com/  （OpenDataLab is a leading platform of open-source data, making open datasets accessible.）
---
### Precautions
> * Be sure to use the parquet download address mentioned above, then use this script to download.
> * This parquet is a large and wide table merged after analysis and calculation by the big data platform, which is more friendly for subsequent use and download.
> * The script does not rely on the big data platform, and can be directly downloaded and processed on a stand-alone or distributed high-speed.

---
### Equipment and working environment preparation
> * Two server 64 core 128GB
> * python3
> * redis #The default ip here is192.168.0.1 port is 6379
---
    
    
### Run script 
    # Queue add task parquet on which machine only run one on this machine 
    Python3 add_task.py
    # monitor_disk.py open a program for each download machine
    Python monitor_disk.py
    # Start 10 download processes
    For i in {0.. 10}; do echo "nohup python3 downloader.py $i >/dev/null 2 > & 1 &" | bash; done
    # save_error_task.py save the error queue data locally in text form, and open it as needed
    Python3 save_error_task.py
    #Download status view
    Python3 speed.py
---
### Configuration file description setting.py
    # redis connection configuration
    redis_ip = "192.168.0.1"
    redis_port = 6379
    redis_db = 0
    redis_pass = "****123***"
    
    
    # The redis key configuration information used
    class RedisKey:
        task_key = "laion5b_task" # Store task queue
        tongji_all = "laion5b_tongji_all" #Count how many tasks have been added
        error_key = "laion5b_task_error" # Download failed task queue
        tongji_error = "laion5b_tongji_error" # Count failed downloads
        tongji_succ = "laion5b_tongji_succ" # Count completed downloads
        tongji_disk = "tongji_worker_disk" # Monitor disk usage

    
    # Use add_task.py to configure the parquet directory, example: /mnt/vdb/laion5b/parquet/laion1B-nolang/0000~0128.parquet  /mnt/vdb/laion5b/parquet/laion2B-en/0000~0128.parquet
    parquet_dir = "/mnt/vdb/laion5b/parquet"
    # When adding a task, there are less than 5000000 in the queue to start executing the add task
    addtask_threshold = 5000000
    # Add the parquet path after writing done_part .txt
    done_path = "./done_part.txt"
    
    
    # monitor_disk.py  View storage space usage
    monitor_disk = '/mnt/vdc'
    
    
    # downloader.py  The directory where the downloaded pictures are stored, and the directories such as laion1B-nolang laion1B-nolang will be spliced later.
    store_dir = "/mnt/vdc/laion5b/data/"
    # The disk usage threshold set here is 5000 GB. If the usage exceeds this threshold, the crawler will stop downloading until the space is freed. Unit: GB
    stop_threshold = 5000
    # The number of multi-threads downloaded by a single process, default: 32
    thread_num = 32
    
    # save_error_task.py  Local redis error queue data, decide whether to persist according to needs. Generally, this program needs to be started, otherwise there are more errors and redis occupies a higher occupancy.
    store_error_dir = "./error_task/"
---
### Download time statistics
> The amount of laion5b media data is 5.8 billion. Using 64 cores 128GB bandwidth 750MB to download 5.1 billion + media data, whose volume is 340TB, the download time is 25 days
> 
> Only 32 CPUs are basically used, each occupying about 80%. The memory 128GB takes up about 90GB. The bandwidth occupies 750GB and the download speed reaches 90 + MB per second. 50 processes and 32 threads.
> 
> It is recommended to use the server resource configuration reasonably, so that the cup, memory and bandwidth can be fully occupied under the operation of the program, and the download speed can be faster.
>
> For code questions or suggestions, please contact 185812238@qq.com
----
