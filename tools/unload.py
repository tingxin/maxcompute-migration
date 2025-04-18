import time
from datetime import datetime
from collections import deque
import queue
import json
import os
import boto3
import threading
import shutil

from .maxcompute import get_conn
from .helper import get_tasks
from .log import get_logger




logger = get_logger("unload")


class EWorkerThread(threading.Thread):
    """
    增量桶的迁移
    """
    def __init__(self, job_name, deque_queue, index):
        threading.Thread.__init__(self)
        self.job_name = job_name
        self.index = index
        self.deque_queue=deque_queue


    def run(self):
        o = get_conn()
        location = os.getenv("STORAGES")
        role = os.getenv("ROLE")
        project = os.getenv("TARGET_PROJECT_NAME")
        while True:
            try:
                # 从队列中获取数据
                table_name, partition = self.deque_queue.popleft()
                logger.info(f"BEGIN TO UNLOAD DATA {table_name}==>{partition}")
                
                cmd = f"""
                UNLOAD FROM 
                (select * from {project}.{table_name} where  {partition})
                INTO 
                LOCATION '{location}/{self.job_name}/{project}/{table_name}/{partition}' 
                ROW FORMAT SERDE 'org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe' 
                WITH SERDEPROPERTIES ('odps.properties.rolearn'='{role}') 
                STORED AS PARQUET 
                PROPERTIES('mcfed.parquet.compression'='SNAPPY');
                """
                o.execute_sql(cmd)
            except IndexError:
                # 如果队列为空，退出线程
                print(f"Thread {self.index}: No more data to process. Exiting.")
                break
            except Exception as ex:
                print(f"Thread {self.index}: {ex}")
                


def run(job_name:str, table_names:list):

    num_threads = int(os.getenv("CONCURRENCY"))
    
    data_queue = deque()
    for table_name in table_names:
        logger.info(f"[unload][{job_name}]===>BEGION ANALYZE RUN {table_name}!")
        partitions = get_tasks(table_name)
        print(partitions)
        for partition in partitions:
            data_queue.append((table_name, partition))
    
    threads = list()
    for index in range(num_threads):
        thread = EWorkerThread(job_name, data_queue, index)
        threads.append(thread)
        thread.start()

        # 等待所有线程完成
        for thread in threads:
            thread.join()


