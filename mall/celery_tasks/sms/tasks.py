

"""
任务:
    1. 就是普通函数
    2. 该函数必须通过 celery的实例对象的 task装饰器装饰
    3. 该任务需要让 celery实例对象 自动检测
    4. 任务(函数) 需要使用 任务(函数名)名.delay() 调用

"""
from libs.yuntongxun.sms import CCP
from celery_tasks.main import app

@app.task
def send_sms_code(mobile,sms_code):

    CCP().send_template_sms(mobile, [sms_code, 5], 1)
