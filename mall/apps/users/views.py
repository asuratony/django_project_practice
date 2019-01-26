from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import exception_handler, APIView

# Create your views here.
# from mall.apps.users.models import User
# from apps.users.models import User
from goods.models import SKU
from users.models import User
from users.serializers import RegisterUserSerializer, UserCenterInfoSerializer, UserEmailSerializer, AddressSerializer, \
    AddUserBrowsingHistorySerializer, SKUSerializer
from users.utils import check_token

"""
1.  明确需求 (要知道我们要干什么)
2.  梳理思路
3. 确定请求方式和路由
4. 确定视图
5. 按照步骤进行开发
"""


"""
判断用户名是否注册

当光标已开用户名之后,我们需要将用户名传递给后端

1. 接收参数  usename
2. 查询数据库  根据查询结果的个数 count
    count: 0 没有注册
    count: 1 注册过
3. 返回数据

GET        /users/usernames/(?P<username>\w{5,20})/count/

 提取URL的特定部分，如/weather/beijing/2018，可以在服务器端的路由中用正则表达式截取；
查询字符串（query string)，形如key1=value1&key2=value2；

GET    /users/usernames/?username=xxxx


POST  /users/usernames/
"""
# APIView                       基类
# GeneriAPIView                 对列表视图和详情视图做了通用支持,一般和mixin配合使用
# ListAPIView,RetrieveAPIView   连 get方法都不用写

from rest_framework.generics import ListAPIView,RetrieveAPIView
class RegisterUsernameAPIView(APIView):

    def get(self,request,username):
        # 1. 接收参数  usename
        # 2. 查询数据库  根据查询结果的个数 count
        count = User.objects.filter(username=username).count()
        #     count: 0 没有注册
        #     count: 1 注册过
        # 3. 返回数据
        return Response({'count':count,
                         'username':username})

"""
1.  明确需求 (要知道我们要干什么)
2.  梳理思路
3. 确定请求方式和路由
4. 确定视图
5. 按照步骤进行开发
"""


"""

当用户点击注册的时候 需要将 用户名,密码,确认密码,手机号,短信验证码,是否同意协议
发送给后端

1. 接收数据
2. 校验数据
3. 数据入库
4. 返回相应

POST        /users/
"""
from rest_framework.mixins import CreateModelMixin

# APIView                       基类
# GeneriAPIView                 对列表视图和详情视图做了通用支持,一般和mixin配合使用
# CreateAPIView                  连 get方法都不用写

class RegisterUserAPIView(APIView):

    def post(self,request):
        # 1. 接收数据
        data = request.data
        # 2. 校验数据
        serializer = RegisterUserSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        # 3. 数据入库
        serializer.save()
        # 4. 返回相应
        # serializer.data 序列化操作(将模型转换位字典/JSON)
        # 原理:  序列化器根据序列化器的字段来获取模型中数据
        # 如果 序列化器中的字段位 write_only 则不会对该字段进行序列化操作


        return Response(serializer.data)



"""
当用户注册成功之后,自动实现登陆

因为我们现在是采用的 JWT-Token
也就是说 用户注册成功之后 我们应该返回一个token给相应,同时
浏览器把接收到的token保存起来

用户注册成功之后 我们应该返回一个token

# 序列化的时候 多一个token
# 序列化器根据序列化器的字段  token  来获取模型  token 中数据
"""

# class Person(object):
#     name='itcast'


# p = Person()
# print(p.name)
# p.age=12
# print(p.age)
#
# p2 = Person()
# print(p2.age)



"""

1.  明确需求 (要知道我们要干什么)
2.  梳理思路
3. 确定请求方式和路由
4. 确定视图
5. 按照步骤进行开发

个人中心

个人中心的接口必须是登陆用户才可以访问的

前端需要传递用户的信息

# 1.接收用户的信息
# 2.查询用户的信息,user
# 3. 将User转换为字典(JSON)数据

GET     /users/infos/

"""
# APIView                       基类
# GeneriAPIView                 对列表视图和详情视图做了通用支持,一般和mixin配合使用
# ListAPIView,RetrieveAPIView   连 get方法都不用写
from rest_framework.permissions import IsAuthenticated
# class UserCenterInfoAPIView(APIView):
#
#     # 在当前的视图中 设置权限
#     permission_classes = [IsAuthenticated]
#
#     def get(self,request):
#         # 1.接收用户的信息
#         user = request.user
#         # 2.查询用户的信息,user
#         # 3. 将User转换为字典(JSON)数据
#         serializer = UserCenterInfoSerializer(user)
#
#         return Response(serializer.data)

from rest_framework.generics import RetrieveAPIView
class UserCenterInfoAPIView(RetrieveAPIView):

    permission_classes = [IsAuthenticated]

    serializer_class = UserCenterInfoSerializer

    # queryset = User.objects.all()
    # 通过我们分析三级视图的 原理: 当前的 get_object不能满足我们的需求
    def get_object(self):

        return self.request.user


"""
需要添加一个 邮件激活的状态

1.当用户点击保存的时候,我们首先把用户的邮箱内容更新到数据库中
2.  2.1同时我们需要给这个邮箱发送一封激活邮件        2.2 激活邮件的内容
3. 当用户点击邮件的时候 会激活

"""

#当用户点击保存的时候,我们首先把用户的邮箱内容更新到数据库中
"""
前端将用户输入的 邮箱内容 通过axios请求发送给后端

这个接口也 必须是登陆用户才可以访问

1. 后端需要先接收数据
2. 验证数据
3. 更新数据
4. 返回相应

PUT     /users/emails/
"""
# APIView                       基类
# GeneriAPIView                 对列表视图和详情视图做了通用支持,一般和mixin配合使用
# UpdateAPIVIew                    连 put方法都不用写
# class UserEmailAPIView(APIView):
#
#     permission_classes = [IsAuthenticated]
#
#     def put(self,request):
#
#         # 1. 后端需要先接收数据
#         data = request.data
#         # 2. 验证数据
#         serializer = UserEmailSerializer(instance=request.user,
#                                          data=data)
#         serializer.is_valid(raise_exception=True)
#         # 3. 更新数据
#         serializer.save()
#           发送激活邮件
#         # 4. 返回相应
#         return Response(serializer.data)
from rest_framework.generics import UpdateAPIView
class UserEmailAPIView(UpdateAPIView):

    permission_classes = [IsAuthenticated]

    def get_object(self):

        return self.request.user

    serializer_class = UserEmailSerializer


"""
当用户点击激活连接的时候,会调转到 我们的网页中 我们的网页通过 axios 来
发送 token

1. 接收token
2. 验证token,获取user_id
3. 查询用户信息
4. 改变用户的激活状态
5. 返回相应

GET     /users/emails/verification/?token=xxxxxx



"""
from rest_framework import status
class UserEmailActiveAPIView(APIView):

    def get(self,request):
        # 1. 接收token
        token = request.query_params.get('token')
        if token is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        # 2. 验证token,获取user_id
        user_id = check_token(token)
        if user_id is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        # 3. 查询用户信息
        user = User.objects.get(pk=user_id)
        # 4. 改变用户的激活状态
        user.email_active=True
        user.save()
        # 5. 返回相应
        return Response({'msg':'ok'})



"""
新增地址


1.  明确需求 (要知道我们要干什么)
2.  梳理思路
3. 确定请求方式和路由
4. 确定视图
5. 按照步骤进行开发


1. 接收数据
2. 校验数据
3. 数据入库
4. 返回相应

POST        /users/addresses/


"""

# APIView                       基类
# GeneriAPIView                 对列表视图和详情视图做了通用支持,一般和mixin配合使用
# CreateAPIView                  连 post方法都不用写

# from rest_framework.generics import CreateAPIView,GenericAPIView
# class AddressAPIView(CreateAPIView):
#
#     serializer_class = AddressSerializer

    # queryset =   新增数据 不需要 必须设置该属性


from rest_framework.decorators import action
from .serializers import AddressTitleSerializer
from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet
class AddressViewSet(mixins.ListModelMixin,mixins.CreateModelMixin,mixins.UpdateModelMixin,GenericViewSet):
    """
    用户地址新增与修改
    list GET: /users/addresses/
    create POST: /users/addresses/
    destroy DELETE: /users/addresses/
    action PUT: /users/addresses/pk/status/
    action PUT: /users/addresses/pk/title/
    """

    #制定序列化器
    serializer_class = AddressSerializer
    #添加用户权限
    permission_classes = [IsAuthenticated]
    #由于用户的地址有存在删除的状态,所以我们需要对数据进行筛选
    def get_queryset(self):
        return self.request.user.addresses.filter(is_deleted=False)

    def create(self, request, *args, **kwargs):
        """
        保存用户地址数据
        """
        count = request.user.addresses.count()
        if count >= 20:
            return Response({'message':'保存地址数量已经达到上限'},status=status.HTTP_400_BAD_REQUEST)

        return super().create(request,*args,**kwargs)

    def list(self, request, *args, **kwargs):
        """
        获取用户地址列表
        """
        # 获取所有地址
        queryset = self.get_queryset()
        # 创建序列化器
        serializer = self.get_serializer(queryset, many=True)
        user = self.request.user
        # 响应
        return Response({
            'user_id': user.id,
            'default_address_id': user.default_address_id,
            'limit': 20,
            'addresses': serializer.data,
        })

    def destroy(self, request, *args, **kwargs):
        """
        处理删除
        """
        address = self.get_object()

        # 进行逻辑删除
        address.is_deleted = True
        address.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['put'], detail=True)
    def title(self, request, pk=None, address_id=None):
        """
        修改标题
        """
        address = self.get_object()
        serializer = AddressTitleSerializer(instance=address, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(methods=['put'], detail=True)
    def status(self, request, pk=None, address_id=None):
        """
        设置默认地址
        """
        address = self.get_object()
        request.user.default_address = address
        request.user.save()
        return Response({'message': 'OK'}, status=status.HTTP_200_OK)



"""

添加浏览历史记录

1.必须是登陆用户调用

2.我们接收前端提交的sku_id
3.对数据进行校验
4.数据入库(Redis)
5.返回相应

POST    /users/histroies/

"""
# APIView                       基类
# GeneriAPIView                 对列表视图和详情视图做了通用支持,一般和mixin配合使用
# CreateAPIView                  连 post方法都不用写
from rest_framework.mixins import CreateModelMixin
from rest_framework.generics import CreateAPIView
from django_redis import get_redis_connection
class UserHistoryAPIView(CreateAPIView):

    permission_classes = [IsAuthenticated]

    serializer_class = AddUserBrowsingHistorySerializer

    # def get_serializer_class(self):
    #     if self.request.method == 'GET':
    #         return SKUSerializer
    #     else:
    #         AddUserBrowsingHistorySerializer

    # def get_queryset(self):
    #     return

    #  1. 获取redis的数据  [1,2,3,4,]
    # 2.  根据id获取商品数据  [SKU,SKU,SKU]
    # 3. 返回字典(JSON数据)
    def get(self,request):

        user = request.user
        #  1. 获取redis的数据  [1,2,3,4,]
        redis_conn = get_redis_connection('history')
        ids = redis_conn.lrange('history_%s'%user.id,0,4)

        # 2.  根据id获取商品数据  [SKU,SKU,SKU]
        # skus = SKU.objects.filter(pk__in=ids)

        skus = []

        for id in ids:
            sku = SKU.objects.get(pk=id)
            skus.append(sku)

        # 3. 返回字典(JSON数据)
        serializer = SKUSerializer(skus,many=True)

        return Response(serializer.data)

from rest_framework_jwt.views import ObtainJSONWebToken
class MergeLoginView(ObtainJSONWebToken):
    # 代码不需要自己写,能够分析出 继承父类 重写 方法就可以
    def post(self, request, *args, **kwargs):

        #1.先调用父类
        response = super().post(request,*args,**kwargs)

        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            user = serializer.object.get('user') or request.user

            from carts.utils import merge_cookie_to_redis
            response = merge_cookie_to_redis(request,user,response)

        return response




class Changepassword(APIView):

    permission_classes = [IsAuthenticated]


    def put(self, request, user_id):
        user = request.user
        data = request.data
        old_password = data.get('old_password')
        password = data.get('password')
        password2 = data.get('password2')

        if not all([old_password,password,password2]):
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if user.check_password(old_password):
            user.set_password(password)
            user.save()

            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

