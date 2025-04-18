import os
import json
from .maxcompute import get_table_partitions


def get_tasks(table_name:str)->list:
    # filter method可以有如下类型：EACH,STARTWITH,ENDWITH,RANGE
    task_filter = os.getenv("TASK_FILTER", "")
    select_p = None
    begin = None
    end = None
    if task_filter:
        if task_filter.startswith("EACH("):
            parts = task_filter[len("EACH("):-1].split(",")
            select_p = {item:True for item in parts}
        elif task_filter.startswith("RANGE("):
            parts = task_filter[len("RANGE("):-1].split(",")
            begin = parts[0]
            end = parts[-1]
        elif task_filter.startswith("STARTWITH("):
            parts = task_filter[len("STARTWITH("):-1].split(",")
            begin = parts[0]
            end = ""
        elif task_filter.startswith("ENDWITH("):
            parts = task_filter[len("ENDWITH("):-1].split(",")
            begin = ""
            end = parts[-1]


    result = list()
    partitions=get_table_partitions(table_name)
    result = list()
    for item in partitions:
        parts = item.split("=")
        value = parts[1]
        if begin:
            if value < begin:
                    continue

        if end:
            if value >= end:
                    break

        if (select_p and value in select_p) or not select_p:
             result.append(item)
 
    return result

    