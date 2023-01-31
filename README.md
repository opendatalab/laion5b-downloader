

---
## 设备及工作环境准备
>* 服务器64核128GB 两台
>* python3
>* redis
---
## python脚本依赖安装
    pip3 install redis
    pip3 install httpx
    pip3 install httpx[http2]
    pip3 install httpx[socks]
    pip3 install pandas
    pip3 install loguru
    pip3 install fastparquet
    pip3 install retrying
    pip3 install pyarrow
---
## 目录文件说明

> add_task.py  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ----------------------- &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 读取任务parquet文件添加下载任务到 redis 
>
> monitor_disk.py  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ----------------------- &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 监控磁盘空间使用防止下载比处理的快造成积压磁盘占用高
> 
> downloader.py  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ----------------------- &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 读取redis任务进行下载
---
## 脚本运行注意事项
> add_task.py 可以配置parquet文件目录自动监控下载parquet文件添加任务  设置目录参数 base_path
> 
> monitor_disk.py 启动前配置所要监控磁盘  这里配置的是  shutil.disk_usage('/mnt/vdc')
> 
> downloader.py 启动前设置一个空间较充足的的目录  设置目录参数 base_dir
> 
---
## 下载用时统计
> laion5b 媒体数据量在58亿多，使用64核128GB带宽750MB  用时30天下载完成
> 
> cpu基本上只使用32个，每个占用80%左右。内存128GB占用90GB左右。带宽占满750GB下载速度达到90+MB每秒。 50进程32线程。
> 
> 建议合理使用服务器资源配置，让cup、内存和带宽在程序的运行下充分占用，下载速度还能更快。
>
----
