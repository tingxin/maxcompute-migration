import os
from odps import ODPS



def get_conn():
    o = ODPS(
        os.getenv('ALIYUN_AK'),
        os.getenv('ALIYUN_SK'),
        project=os.getenv('TARGET_PROJECT_NAME'),
        endpoint=os.getenv('TARGET_ENDPOINT')
    )
    return o

def get_table_schema(table_name:str):
    o = get_conn()
    tb = o.get_table(table_name)
    print(tb.name)
    print(tb.table_schema)



def get_table_partitions(table_name)->list:
    # 初始化ODPS连接
    o = get_conn()
    sql = f"SHOW PARTITIONS {table_name};"
    with o.execute_sql(sql).open_reader() as reader:
        # 获取查询结果
        partition_info  = str(reader.raw)
        partitions =[item for item in partition_info.split("\n") if item !='']
        return partitions

    



