
import os
from tools import conf, unload

conf.load_env()

table_names = os.getenv("TABLE_NAME").split(",")

unload.run("test1", table_names)
