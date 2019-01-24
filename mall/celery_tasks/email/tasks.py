from django.core.mail import send_mail
from celery_tasks.main import app

# name 就是给任务起名字
@app.task(name='lalala')
def send_celery_email(subject, message, from_email, recipient_list,html_message):

    send_mail(subject=subject,
              message=message,
              from_email=from_email,
              recipient_list=recipient_list,
              html_message=html_message)