from django_redis import get_redis_connection
from rest_framework import serializers

# serializers.Serializer
# serializers.ModelSerializer
from oauth.models import OAuthQQUser
from oauth.utils import check_access_token
from users.models import User


class OauthQQUserSerializer(serializers.Serializer):

    access_token = serializers.CharField(label='操作凭证')
    mobile = serializers.RegexField(label='手机号', regex=r'^1[3-9]\d{9}$')
    password = serializers.CharField(label='密码', max_length=20, min_length=8)
    sms_code = serializers.CharField(label='短信验证码')

    """
    前端传递  手机号,密码,短信验证码和 加密的openid
    保存的数据是 user,openid

    """

    # def validate(self, data):
    def validate(self, attrs):
        #     1.openid
        access_token = attrs.get('access_token')
        openid = check_access_token(access_token)
        if openid is None:
            raise serializers.ValidationError('绑定失败')

        attrs['openid']=openid

        #     2.短信验证码
        # 2.1 获取用户提交
        mobile = attrs['mobile']
        sms_code = attrs['sms_code']
        # 2.2 获取redis的
        redis_conn = get_redis_connection('code')

        redis_sms_code = redis_conn.get('sms_' + mobile)
        if redis_sms_code is None:
            raise serializers.ValidationError('短信验证码已过期')

        # 最好将获取到redis的短信删除
        redis_conn.delete('sms_' + mobile)

        # 2.3 比对
        if redis_sms_code.decode() != sms_code:
            raise serializers.ValidationError('短信验证码不一致')

        #     3.根据手机号进行判断,判断手机号是否注册过
        try:
            user = User.objects.get(mobile=mobile)
        except User.DoesNotExist:
            #该手机号没有注册过,我们应该创建一个新用户
            # user = User.objects.create()
            # 我们这个方法主要是验证的 ,所以将创建用户的代码 写在 create中
            pass
        else:
            # 该手机号注册过,已经有用户
            # 我们需要验证密码是否输入正确
            if not user.check_password(attrs['password']):
                raise serializers.ValidationError('密码不正确')

            attrs['user']=user

        # del attrs['password2']

        return attrs

    #  request.data --> 序列化器(data=request.data)
    #  data --> attrs --> validated_data
    def create(self, validated_data):

        user = validated_data.get('user')

        if user is None:

            user = User.objects.create(
                username=validated_data.get('mobile'),
                mobile=validated_data.get('mobile'),
                password=validated_data.get('password')
            )
            # 对密码进行加密
            user.set_password(validated_data.get('password'))
            user.save()


        qquser = OAuthQQUser.objects.create(
            user=user,
            openid=validated_data.get('openid')
        )

        return qquser


