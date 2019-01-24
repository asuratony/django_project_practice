from rest_framework import serializers
from django_redis import get_redis_connection

# ModelSerializer 可以自动生成字段,实现了 create和update方法
# 但是 必须有Model

# serializers.Serializer
# serializers.ModelSerializer

# 使用Serialzier  因为没有Model

class RegisterSmscodeSerializer(serializers.Serializer):

   text=serializers.CharField(label='图片验证码',max_length=4,min_length=4,required=True)
   image_code_id=serializers.UUIDField(label='uuid',required=True)

   """
   序列化的验证:
   1. 字段类型
   2. 字段选项
   3. 单个字段
   4. 多个字段

   """
   # text是用户输入的  我们需要通过 iamge_code_id 获取redis的
   # 所以需要使用 多个字段

   # 断点加哪里:  每行都加
   #            在程序(函数)的入口处
   #            哪里有问题加哪里
   #            实现了一个功能
   def validate(self, attrs):

       # 1. 获取用户提交的
       text = attrs['text']
       #2. 获取redis的
       #2.1 连接redis
       redis_conn = get_redis_connection('code')
       #2.2 获取数据
       image_code_id=attrs['image_code_id']
       redis_text = redis_conn.get('img_'+str(image_code_id))

       if redis_text is None:
           raise serializers.ValidationError('图片验证码已过期')
       #3. 比对
       #  ① redis的数据是bytes类型
       # ② 注意大小写
       if redis_text.decode().lower() != text.lower():
           raise serializers.ValidationError('数据输入不一致')

       return attrs
