import pickle

import base64
from django.shortcuts import render

# Create your views here.
from django_redis import get_redis_connection
from rest_framework.response import Response
from rest_framework.views import APIView

from carts.serializers import CartSerialzier, CartSKUSerializer, CartDeleteSerializer
from goods.models import SKU
from rest_framework import status

"""

1. 未登录用户也是可以保存购物车信息的 cookie
  登录用户 保存购物车信息到 Redis

.

2. 我们需要保存 商品id,商品个数,以及选中状态


3. 组织cookie的数据格式

    cart: {
        sku_id:{'count':4,'selected':True},
        sku_id:{'count':8,'selected':False},
    }

    组织 Redis的数据结构

    登陆用户的信息

    Redis的数据是保存在内存中的,
    尽量占用少的内存来实现功能

    sku_id,count,selected


    hash        hash_key:   property:value
                cart_userid: sku_id:count

                cart_user1:  1:5
                              2:3
                              3:5
                我们只记录选中商品的id
                2

                cart_user2:  3:10

    set         set_key:    [value2,value1]

                cart_selected_user1: {2}


4.  如何区分登陆还是未登录用户
    request.user

    # user.is_authenticated
    # user.is_authenticated 为False 表示用户没有认证登陆
    # user.is_authenticated 为True 表示用户认证登陆


5. base64

1G = 1024M
1M = 1024KB
1KB = 1024B
1B = 8 byte

0100 0001  0100 0001   0100 0001
A           A           A

010000      010100      000101       000001
X               y       z               h



"""

class CartAPIView(APIView):


    """

    POST        cart/       添加购物车数据
    GET         cart/       获取购物车数据
    PUT         cart/       修改购物车数据
    DELETE      cart/       删除购物车数据

    """


    # 因为用户提交了token 这个token如果过期了/被篡改了
    # 这个时候 它就不能实现 添加购物车的功能
    # 我们应该先让用户 添加到购物车中
    # 就不能应该先认证

    #重写 perform_authentication 视图就不会进行认证了
    # 当我们需要的时候再去认证
    def perform_authentication(self, request):
        pass


    """
    当用户在点击 添加购物车的时候 ,前端 需要将:
    商品id,商品数量以及用户的信息(如果登陆) 传递给后端

    1. 接收数据 sku_id,count    选中状态可以不用传,默认为 选中
    2. 对数据进行校验 (判断商品是否存在,判断库存)
    3. 获取验证的数据(为了要将验证的数据 保存到指定的地方)
    4. 获取用户信息
    5. 判断用户的登陆状态
    6. 登陆用户redis
        6.1 连接redis
        6.2 hash
            set
        6.3 返回相应
    7. 未登录用户cookie
        7.1 获取cookie中 购物车的数据
        7.2 判断是否存在
        7.3 如果存在相同的商品,则我们需要对商品的数量进行累加
        7.4 如果不存在相同的商品,则我们添加商品
        7.5 返回相应




    """
    def post(self,request):

        # 1. 接收数据 sku_id,count    选中状态可以不用传,默认为 选中
        data = request.data
        # 2. 对数据进行校验 (判断商品是否存在,判断库存)
        serializer = CartSerialzier(data=data)
        serializer.is_valid(raise_exception=True)
        # 3. 获取验证的数据(为了要将验证的数据 保存到指定的地方)
        sku_id=serializer.validated_data.get('sku_id')
        count=serializer.validated_data.get('count')
        selected=serializer.validated_data.get('selected')
        # 4. 获取用户信息
        try:
            user = request.user
        except Exception as e:
            user = None
        # 5. 判断用户的登陆状态
        # request.user.is_authenticated
        if user is not None and user.is_authenticated:
            # 6. 登陆用户redis
            #     6.1 连接redis
            redis_conn = get_redis_connection('cart')
            #     6.2 hash
            # 先获取到之前的数据,然后进行累加操作
            # redis_conn.hset('cart_%s'%user.id,sku_id,count)
            # hincrby 增量操作
            # redis_conn.hincrby('cart_%s'%user.id,sku_id,count)
            # #         set
            # if selected:
            #     redis_conn.sadd('cart_selected_%s'%user.id,sku_id)


            #① 创建管道
            pl = redis_conn.pipeline()
            #② 将指令缓存到管道中
            pl.hincrby('cart_%s' % user.id, sku_id, count)
            #         set
            if selected:
                pl.sadd('cart_selected_%s' % user.id, sku_id)
            #③ 执行管道
            pl.execute()

            """
            A: 在吗?
            A: 吃了吗?
            B:

            A: 在吗? 吃了吗?
            B:

            """
            #     6.3 返回相应
            return Response(serializer.data)

        else:
            # 7. 未登录用户cookie
            #     7.1 获取cookie中 购物车的数据
            cookie_str = request.COOKIES.get('cart')
            #     7.2 判断是否存在
            if cookie_str is not None:
                #说明有数据

                #① 将base64的数据进行解码
                decode = base64.b64decode(cookie_str)
                #② 将二进制转换为字典
                cookie_cart=pickle.loads(decode)

            else:
                #说明没有数据
                # 初始化一个空字典
                cookie_cart = {}

            #     7.3 如果存在相同的商品,则我们需要对商品的数量进行累加
            # cookie_cart = {1: {count:10,selected:True}}
            if sku_id in cookie_cart:
                # 原个数获取
                original_count = cookie_cart[sku_id]['count']
                #再累加
                # count = original_count + count
                count += original_count

            #     7.4 如果不存在相同的商品,则我们添加商品
            # cookie_cart = {sku_id: {count:10,selected:True}}

            cookie_cart[sku_id]={
                'count':count,
                'selected':selected
            }

            #7.5  对字典数据进行 base64的处理

            #7.5.1  pickle.dumps  将字典转换为二进制
            dumps = pickle.dumps(cookie_cart)

            #7.5.2  base64.b64encode  将二进制进行 base64编码
            encode = base64.b64encode(dumps)

            #7.5.3 将bytes类型转换位 str
            value = encode.decode()


            #     7.6 返回相应
            response = Response(serializer.data)

            response.set_cookie('cart',value)

            return response




        # try:
        #     user=request.user
        # except Exception as e:
        #     user = None

        #user.is_authenticated
        # user.is_authenticated 为False 表示用户没有认证登陆
        # user.is_authenticated 为True 表示用户认证登陆
        # print(user)
        pass


    """
    当用户获取购物车数据的时候,我们需要让前端传递一个用户信息过来(如果登陆则传递)

    1.接收用户信息
    2.根据用户信息进行判断
    3.登陆用户从redis中获取数据
        3.1 连接redis
        3.2 获取hash          cart_userid:            sku_id:count
            获取set数据       cart_selected_userid:     sku_id
        3.3 需要根据skuid 获取商品的详细信息 [SKU,SKU,SKU]
        3.4 对列表数据进行序列化器处理
        3.5 返回相应
    4.未登录用户从cookie中获取数据
        4.1 获取cookie中的 cart数据
        4.2 判断cart数据是否存在
            如果存在需要进行base64解码        {sku_id:{count:4,selected:True}}
            如果不存在 初始化 cookie_cart
        4.3 需要根据skuid 获取商品的详细信息 [SKU,SKU,SKU]
        4.4 对列表数据进行序列化器处理
        4.5 返回相应


    1.接收用户信息
    2.根据用户信息进行判断
    3.登陆用户从redis中获取数据
        3.1 连接redis
        3.2 获取hash          cart_userid:            sku_id:count
            获取set数据       cart_selected_userid:     sku_id
    4.未登录用户从cookie中获取数据
        4.1 获取cookie中的 cart数据
        4.2 判断cart数据是否存在
            如果存在需要进行base64解码        {sku_id:{count:4,selected:True}}
            如果不存在 初始化 cookie_cart

    5 需要根据skuid 获取商品的详细信息 [SKU,SKU,SKU]
    6 对列表数据进行序列化器处理
    7 返回相应
    """

    def get(self,request):
        # 1.接收用户信息
        try:
            user = request.user
        except Exception as e:
            user = None
        # 2.根据用户信息进行判断
        if user is not None and user.is_authenticated:

            # 3.登陆用户从redis中获取数据
            #     3.1 连接redis
            redis_conn = get_redis_connection('cart')
            #     3.2 获取hash          cart_userid:            sku_id:count
            # 要获取 当前这个用户的所有数据
            redis_sku_id_count = redis_conn.hgetall('cart_%s'%user.id)
            #         获取set数据       cart_selected_userid:     sku_id
            redis_selected_ids = redis_conn.smembers('cart_selected_%s'%user.id)

            # {sku_id:count}            {1:5,12:3}
            # [sku_id,]                 [1]
            # 将 redis数据转换为 和 cookie数据一样的格式
            # {sku_id:{count:4,selected:True}}

            #   {1:{count:5,selected:true},12:{count:3,selected:False}}

            cookie_cart = {}
            # 需要对 redis_sku_id_count 进行便利
            for sku_id,count in redis_sku_id_count.items():

                if sku_id in redis_selected_ids:
                    selected=True
                else:
                    selected=False
                # redis的数据是bytes类型 我们需要进行转换
                cookie_cart[int(sku_id)]={
                    'count':int(count),
                    # 'selected':sku_id in redis_selected_ids
                    'selected':selected
                }


        else:
            # 4.未登录用户从cookie中获取数据
            #     4.1 获取cookie中的 cart数据
            cookie_str = request.COOKIES.get('cart')
            #     4.2 判断cart数据是否存在
            if cookie_str is not None:
                #         如果存在需要进行base64解码
                #① 对base64字符串进行解码
                decode = base64.b64decode(cookie_str)
                #②将二进制转换为 字典
                cookie_cart = pickle.loads(decode)
            else:
                #         如果不存在 初始化 cookie_cart
                cookie_cart = {}
            # {sku_id:{count:4,selected:True}}


        # {sku_id:{count:4,selected:True}}

        ids = cookie_cart.keys()
        # [1,2,3,4]

        # 5 需要根据skuid 获取商品的详细信息 [SKU,SKU,SKU]
        skus = SKU.objects.filter(pk__in=ids)


        for sku in skus:
            sku.count = cookie_cart[sku.id]['count']
            sku.selected=cookie_cart[sku.id]['selected']

        # 6 对列表数据进行序列化器处理
        serializer = CartSKUSerializer(skus,many=True)
        # 7 返回相应
        return Response(serializer.data)


    """
    修改购物车的数据

    1.后端接收数据 sku_id,count,selected
    2.验证数据
    3. 获取验证之后的数据
    4. 获取用户信息
    5. 根据用户信息进行判断
    6. 登陆用户redis
        6.1 连接redis
        6.2 更新数据
            hash
            set
        6.3 返回相应
    7. 未登录用户cookie
        7.1 获取cookie数据
        7.2 判断cart数据是否存在
        7.3 更新数据
        7.4 返回相应

    """

    def put(self,request):

        # 1.后端接收数据 sku_id,count,selected
        data = request.data
        # 2.验证数据
        serialzier = CartSerialzier(data=data)
        serialzier.is_valid(raise_exception=True)
        # 3. 获取验证之后的数据
        sku_id = serialzier.validated_data.get('sku_id')
        count = serialzier.validated_data.get('count')
        selected = serialzier.validated_data.get('selected')
        # 4. 获取用户信息
        try:
            user = request.user
        except Exception as e:
            user = None
        # 5. 根据用户信息进行判断
        # request.user.is_authenticated
        if user is not None and user.is_authenticated:

            # 6. 登陆用户redis
            #     6.1 连接redis
            redis_conn = get_redis_connection('cart')
            #     6.2 更新数据
            #         hash
            redis_conn.hset('cart_%s'%user.id,sku_id,count)
            #         set  选中状态
            if selected:
                redis_conn.sadd('cart_selected_%s'%user.id,sku_id)
            else:
                # 移除sku_id
                redis_conn.srem('cart_selected_%s'%user.id,sku_id)

            #     6.3 返回相应
            return Response(serialzier.data)

        else:

            # 7. 未登录用户cookie
            #     7.1 获取cookie数据
            cookie_str = request.COOKIES.get('cart')
            #     7.2 判断cart数据是否存在
            if cookie_str is not None:

                # ① 对base64编码之后的数据进行解码  base64.b64decode
                decode =  base64.b64decode(cookie_str)
                # ②  将二进制转换位字典
                cookie_cart = pickle.loads(decode)
            else:
                cookie_cart = {}

            #     7.3 更新数据
            # {sku_id: {count:xxx,selected:xxx}}
            if sku_id in cookie_cart:
                cookie_cart[sku_id]= {
                    'count':count,
                    'selected':selected
                }
            #     7.4 返回相应
            response = Response(serialzier.data)

            # ① 将字典转换为二进制
            dumps = pickle.dumps(cookie_cart)
            # ②将二进制进行base64编码
            encode = base64.b64encode(dumps)

            #③ 将bytes类型的数据转换为 字符串
            value = encode.decode()

            response.set_cookie('cart',value)

            return response


    """
    当用户点击删除按钮的时候,前端需要将 用户信息(登陆用户)和商品id
    提交给后端

    1. 接收数据
    2. 校验数据
    3. 获取校验的数据
    4. 获取用户信息
    5. 根据用户信息进行判断
    6. 登陆用户redis
        6.1 连接redis
        6.2 删除数据
            hash
            set
        6.3 返回相应
    7. 未登录用户cookie
        7.1 获取cookie数据
        7.2 判断cart数据是否存在
        7.3 删除数据
        7.4 返回相应

    """

    def delete(self,request):
        # 1. 接收数据
        data = request.data
        # 2. 校验数据
        serialzier = CartDeleteSerializer(data=data)
        serialzier.is_valid(raise_exception=True)
        # 3. 获取校验的数据
        sku_id = serialzier.validated_data.get('sku_id')
        # 4. 获取用户信息
        try:
            user = request.user
        except Exception as e:
            user = None
        # 5. 根据用户信息进行判断
        # request.user.is_authenticated
        if user is not None and user.is_authenticated:

            # 6. 登陆用户redis
            #     6.1 连接redis
            redis_conn = get_redis_connection('cart')
            #     6.2 删除数据
            #         hash
            redis_conn.hdel('cart_%s'%user.id,sku_id)
            #         set 移除
            redis_conn.srem('cart_selected_%s'%user.id,sku_id)
            #     6.3 返回相应

            return Response(status=status.HTTP_204_NO_CONTENT)

        else:
            # 7. 未登录用户cookie
            #     7.1 获取cookie数据
            cookie_str = request.COOKIES.get('cart')
            #     7.2 判断cart数据是否存在
            if cookie_str is not None:
                cookie_cart = pickle.loads(base64.b64decode(cookie_str))
            else:
                cookie_cart = {}
            #     7.3 删除数据
            if sku_id in cookie_cart:
                del cookie_cart[sku_id]
            #     7.4 返回相应
            response = Response(status=status.HTTP_204_NO_CONTENT)

            value = base64.b64encode(pickle.dumps(cookie_cart)).decode()

            response.set_cookie('cart',value)

            return response

