"""
1. celery
2. 任务
3. broker
4. worker
"""
from celery import Celery

# 一. celery

# 1. celery 即插即用的任务队列
# 在使用的时候 需要使用到当前工程的配置信息
# 需要加载当前工程的配置信息

# 第一种方式:
# import os
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mall.settings")

# 第二种方式:
import os
if not os.getenv('DJANGO_SETTINGS_MODULE'):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'mall.settings'


#2. 创建一个 celery实例对象
# main 一般就是设置 文件夹的名字(路径)
app = Celery('celery_tasks')

# 3.让celery加载配置broker文件
# 设置config的路径就可以
app.config_from_object('celery_tasks.config')

# 4.  celery 会自动检测 tasks 的任务
# 列表
# 元素: 任务的包路径
app.autodiscover_tasks(['celery_tasks.sms','celery_tasks.email','celery_tasks.html'])



# worker
# 我们需要在虚拟环境中 执行以下指令
# celery -A celery的实例对象文件路径 worker -l info

# celery -A celery_tasks.main worker -l info
