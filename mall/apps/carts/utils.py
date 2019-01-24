"""

登陆的时候 将cookie数据合并到redis中

cookie
{sku_id:{count:xxx,selected:xxxx}}

redis
    hash:       cart_userid:        sku_id:count
    set         cart_selected_userid  sku_id,sku_id

#1.获取cookie数据
cookie:
    {
        1:{count:100,selected:True},
        3:{count:100,selected:False},
    }

#2.获取redis数据
Redis:
    hash:       {2:50,3:50}
    set:        {2}

#3.做数据的初始化
    {2:50,3:50}
    []
#4. 合并
合并:
    {2:50,3:100,1:100}
    [1]




1. 如果redis中没有的数据 sku_id ,cookie中有,则 将cookie中的sku_id 添加进来
2. 如果redis中有的数据 ,cookie中有,则数量怎么处理?
        如果以cookie为主,数量覆盖redis数量     v
        如果以redis位主,则忽略cookie数量
        如果累加,则累加

"""
import pickle

import base64
from django_redis import get_redis_connection


def merge_cookie_to_redis(request,user,response):

    """
    1. 获取cookie数据
    2. 获取redis数据
    3. 做数据的初始化
        hash数据 (将redis的bytes类型进行转换)
        set数据  初始化一个空列表 用于记录选中的id
    4. 对cookie数据进行遍历

    5. 将合并的数据保存到redis中

    6. 删除cookie数据

    :return:
    """
    # 1. 获取cookie数据
    cookie_str = request.COOKIES.get('cart')
    if cookie_str is not None:
        cookie_cart = pickle.loads(base64.b64decode(cookie_str))

        # 2. 获取redis数据
        redis_conn = get_redis_connection('cart')
        redis_id_count = redis_conn.hgetall('cart_%s'%user.id)
        # {b'1':b'5',}

        # 3. 做数据的初始化
        #     hash数据 (将redis的bytes类型进行转换)
        merge_cart = {}  #  {2:50,3:50}
        for sku_id,count in redis_id_count.items():
            merge_cart[int(sku_id)]=int(count)
        #     set数据  初始化一个空列表 用于记录选中的id
        selected_ids = []  # [1]
        # 4. 对cookie数据进行遍历
        """
        {
            1:{count:100,selected:True},
            3:{count:100,selected:False},
        }
        """
        for sku_id,count_selected_dict in cookie_cart.items():
            # if sku_id not in merge_cart:
            #     merge_cart[sku_id]=count_selected_dict['count']
            # else:
            #     #id重复, 我们以cookie数据为准
            #     merge_cart[sku_id]=count_selected_dict['count']

            merge_cart[sku_id]=count_selected_dict['count']

            #选中的状态
            if count_selected_dict['selected']:
                selected_ids.append(sku_id)

        # 5. 将合并的数据保存到redis中
        # merge_cart   {sku_id:count,sku_id:count}
        redis_conn.hmset('cart_%s'%user.id,merge_cart)

        # selected_ids  [sku_id,sku_id]
        if len(selected_ids)>0:
            redis_conn.sadd('cart_selected_%s'%user.id,*selected_ids)
        # 6. 删除cookie数据
        response.delete_cookie('cart')

        return response

    return response

