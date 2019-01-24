import re

from rest_framework import serializers

# serializers.ModelSerializer
# serializers.Serializer
from rest_framework_jwt.settings import api_settings

from mall import settings
from users.models import User, Address
from django_redis import get_redis_connection

from users.utils import generic_verify_url


class RegisterUserSerializer(serializers.ModelSerializer):
    """
    用户名,密码,确认密码,手机号,短信验证码,是否同意协议
    """
    """
    ModelSerializer 自动生成字段的原理:
    它会对 fields 进行遍历, 如果 模型中有相应的字段 会自动生成
    如果没有 则查看当前类 是否有自己实现
    """
    # write_only 只写入(反序列化的时候使用) 进行 序列化操作的时候 忽略此字段
    password2=serializers.CharField(label='确认密码',write_only=True,max_length=20,min_length=5,required=True)

    sms_code=serializers.CharField(label='短信',write_only=True,min_length=6,max_length=6,required=True)

    allow = serializers.CharField(label='是否同意协议',write_only=True,required=True)

    token = serializers.CharField(label='token',read_only=True)

    class Meta:
        model = User
        fields = ['id','token','username','password','password2','sms_code','allow','mobile']

        extra_kwargs = {
            'id': {'read_only': True},
            'username': {
                'min_length': 5,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许5-20个字符的用户名',
                    'max_length': '仅允许5-20个字符的用户名',
                }
            },
            'password': {
                'write_only': True,
                'min_length': 8,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许8-20个字符的密码',
                    'max_length': '仅允许8-20个字符的密码',
                }
            }
        }

    """
    序列化器的校验:
    1. 字段类型校验
    2. 字段选项验证
    3. 单个字段验证
    4. 多个字段验证

    单个字段
    手机号,
    是否同意协议

    多个字段
    密码,确认密码,
    短信验证码,

    """
    #手机号
    def validate_mobile(self,value):

        if not re.match(r'1[3-9]\d{9}',value):
            raise serializers.ValidationError('手机号不满足要求')
        return value

    #是否同意协议
    def validate_allow(self,value):
        if value != 'true':
            raise serializers.ValidationError('您未同意协议')
        return value

    def validate(self, attrs):
        #1.密码,确认密码
        password = attrs.get('password')
        password2 = attrs.get('password2')
        if password != password2:
            raise serializers.ValidationError('密码不一致')

        #2.短信验证码
        #2.1 获取用户提交
        mobile = attrs['mobile']
        sms_code = attrs['sms_code']
        #2.2 获取redis的
        redis_conn = get_redis_connection('code')

        redis_sms_code = redis_conn.get('sms_'+mobile)
        if redis_sms_code is None:
            raise serializers.ValidationError('短信验证码已过期')

        #最好将获取到redis的短信删除
        redis_conn.delete('sms_'+mobile)

        #2.3 比对
        if redis_sms_code.decode() != sms_code:
            raise serializers.ValidationError('短信验证码不一致')

        return attrs


    def create(self, validated_data):

        # validated_data
        # 当所有的验证都没有问题的时候 validated_data = data
        # 这里多3个数据
        del validated_data['sms_code']
        del validated_data['password2']
        del validated_data['allow']

        #1. 第一种方式
        # User.objects.create(**validated_data)

        #2. 第二种方式
        user = super().create(validated_data)


        # 修改用户的密码
        user.set_password(validated_data['password'])
        user.save()

        #1. 导入 jwt的配置文件
        from rest_framework_jwt.settings import api_settings

        #2.我们需要使用 jwt的2个方法
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        #3. 使用这2个方法
        # 3.1 将用户信息 存放在 payload
        payload = jwt_payload_handler(user)
        #3.2 对payload进行编码
        token = jwt_encode_handler(payload)

        user.token = token

        return user


# class Person(object):
#     name ='itcast'
#
#
# p = Person()
# p.name = 'abc'
# p.age = 13
#
# p2 = Person()
# print(p2.age)


# serializers.Serializer
# serializers.ModelSerializer
class UserCenterInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'mobile', 'email')

# serializers.ModelSerializer
# serializers.Serializer
class UserEmailSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'email')
        extra_kwargs = {
            'email': {
                'required': True
            }
        }


    def update(self, instance, validated_data):
        email = validated_data.get('email')
        # 保存完之后
        instance.email=email
        instance.save()
        # 再发送邮件
        from django.core.mail import send_mail
        #subject, message, from_email, recipient_list,
        #subject        主题
        subject = '美多商城激活邮件'
        # message,      内容
        message = ''
        # from_email,   发件人
        from_email = settings.EMAIL_FROM
        # recipient_list, 收件人列表
        recipient_list = [email]

        # 封装的思想
        verify_url = generic_verify_url(instance.id)

        html_message = '<p>尊敬的用户您好！</p>' \
                   '<p>感谢您使用美多商城。</p>' \
                   '<p>您的邮箱为：%s 。请点击此链接激活您的邮箱：</p>' \
                   '<p><a href="%s">%s<a></p>' % (email, verify_url, verify_url)

        # send_mail(subject=subject,
        #           message=message,
        #           from_email=from_email,
        #           recipient_list=recipient_list,
        #           html_message=html_message)

        from celery_tasks.email.tasks import send_celery_email
        send_celery_email.delay(subject=subject,
                  message=message,
                  from_email=from_email,
                  recipient_list=recipient_list,
                  html_message=html_message)


        return instance


# class AddressSerializer(serializers.ModelSerializer):
#
#     province = serializers.StringRelatedField(read_only=True)
#     city = serializers.StringRelatedField(read_only=True)
#     district = serializers.StringRelatedField(read_only=True)
#     province_id = serializers.IntegerField(label='省ID', required=True)
#     city_id = serializers.IntegerField(label='市ID', required=True)
#     district_id = serializers.IntegerField(label='区ID', required=True)
#     mobile = serializers.RegexField(label='手机号', regex=r'^1[3-9]\d{9}$')
#
#     class Meta:
#         model = Address
#         exclude = ('user', 'is_deleted', 'create_time', 'update_time')
#
#     def create(self, validated_data):
#         # GenericAPIVew 会给序列化器传递 context
#         # context 中就有 view, request
#         user = self.context['request'].user
#         validated_data['user'] = user
#
#         return super().create(validated_data)

        # return Address.objects.create(**validated_data)


class AddressSerializer(serializers.ModelSerializer):

    province = serializers.StringRelatedField(read_only=True)
    city = serializers.StringRelatedField(read_only=True)
    district = serializers.StringRelatedField(read_only=True)
    province_id = serializers.IntegerField(label='省ID', required=True)
    city_id = serializers.IntegerField(label='市ID', required=True)
    district_id = serializers.IntegerField(label='区ID', required=True)
    mobile = serializers.RegexField(label='手机号', regex=r'^1[3-9]\d{9}$')

    class Meta:
        model = Address
        exclude = ('user', 'is_deleted', 'create_time', 'update_time')


    def create(self, validated_data):
        #Address模型类中有user属性,将user对象添加到模型类的创建参数中
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class AddressTitleSerializer(serializers.ModelSerializer):
    """
    地址标题
    """
    class Meta:
        model = Address
        fields = ('title',)

from goods.models import SKU


class AddUserBrowsingHistorySerializer(serializers.Serializer):
    """
    添加用户浏览记录序列化器
    """
    sku_id = serializers.IntegerField(label='商品编号',min_value=1,required=True)

    def validate_sku_id(self,value):
        """
        检查商品是否存在
        """
        try:
            SKU.objects.get(pk=value)
        except SKU.DoesNotExist:
            raise serializers.ValidationError('商品不存在')

        return value



    def create(self, validated_data):

        sku_id = validated_data['sku_id']

        user = self.context['request'].user
        #1. 连接redis
        redis_conn = get_redis_connection('history')

        #2.判断数据是否重复
        # redis_conn.lrem(key,count,value)
        redis_conn.lrem('history_%s'%user.id,0,sku_id)

        #3.添加数据
        redis_conn.lpush('history_%s'%user.id,sku_id)

        #4.对列数据进行裁剪
        redis_conn.ltrim('history_%s'%user.id,0,4)

        return validated_data


class SKUSerializer(serializers.ModelSerializer):

    class Meta:
        model = SKU
        fields = ('id', 'name', 'price', 'default_image_url', 'comments')



