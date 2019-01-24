from decimal import Decimal

from django_redis import get_redis_connection
from rest_framework import serializers

from goods.models import SKU


class PlaceOrderSerializer(serializers.ModelSerializer):
    count = serializers.IntegerField(label='个数')

    class Meta:
        model = SKU
        fields = ['id', 'name', 'price', 'default_image_url', 'count']


class PlaceSerializer(serializers.Serializer):

    freight = serializers.DecimalField(label='运费',max_digits=10,decimal_places=2)
    skus = PlaceOrderSerializer(many=True)


from orders.models import OrderInfo, OrderGoods


class OrderCommitSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderInfo
        fields = ('order_id', 'address', 'pay_method')
        read_only_fields = ('order_id',)
        extra_kwargs = {
            'address': {
                'write_only': True,
                'required': True,
            },
            'pay_method': {
                'write_only': True,
                'required': True
            }
        }


    def create(self, validated_data):

        """

        当点击订单按钮的时候 需要 先 生成订单信息
        再保存订单商品

        1.订单信息
            1.1 获取用户信息
            1.2 获取地址信息
            1.3 获取支付方式
            1.4 order_id 自己生成 不采用系统的自增方式
            1.5 商品的总数量(0),总价格(0) 和运费信息
            1.6 订单状态
            order = OrderInfo.objects.create()
        2.保存订单商品
            2.1 连接redis
            2.2  hash   {b'sku_id':b'count'}
                set  选中的商品id  [b'sku_id']
            2.3 重写组织数据选中的商品的id {sku_id:count,sku_id:count,}
            2.4  [sku_id,sku_id,sku_id]
            2.5  [SKU,SKU,SKU]
            2.6 遍历商品列表
                sku
                先判断库存

                如果库存充足,则可以售卖
                库存减少
                销量增加

                再累加计算总价格和总数量

                将售卖的sku添加到
                订单商品中
                OrderGoods.objects.create()


        3. 订单和商品列表生成了之后,需要将 redis中选中商品删除

        """

        # 有一堆 数据库的操作

        # 1.订单信息
        #     1.1 获取用户信息
        user = self.context['request'].user
        #     1.2 获取地址信息
        address = validated_data.get('address')

        #     1.3 获取支付方式
        pay_method = validated_data.get('pay_method')

        #     1.4 order_id 自己生成 不采用系统的自增方式
        # 时间(年月日时分秒) + 6位用户id
        from django.utils import timezone
        # Year年 month月 day 日 Hour 时 Minute分 Second
        order_id = timezone.now().strftime('%Y%m%d%H%M%S') + '%06d'%user.id

        #     1.5 商品的总数量(0),总价格(0) 和运费信息
        #总运费
        freight = Decimal('10.00')
        #总数量
        total_count = 0
        # 总价格
        total_amount = Decimal('0')
        #     1.6 订单状态
        # if pay_method == 1:
        #
        #     status = 2
        # else:
        #
        #     status = 1

        if pay_method == OrderInfo.PAY_METHODS_ENUM['CASH']:

            status = OrderInfo.ORDER_STATUS_ENUM['UNSEND']
        else:

            status = OrderInfo.ORDER_STATUS_ENUM['UNPAID']

        from django.db import transaction
        with transaction.atomic():

            #如果出现问题,则回滚到这里
            save_point = transaction.savepoint()

            order = OrderInfo.objects.create(
                order_id=order_id,
                user=user,
                address=address,
                total_count=total_count,
                total_amount=total_amount,
                freight=freight,
                pay_method=pay_method,
                status=status
            )
            # 2.保存订单商品
            #     2.1 连接redis
            redis_conn = get_redis_connection('cart')
            #     2.2  hash   {b'sku_id':b'count'}
            redis_count_id = redis_conn.hgetall('cart_%s'%user.id)
            #         set  选中的商品id  [b'sku_id']
            selected_ids = redis_conn.smembers('cart_selected_%s'%user.id)

            #     2.3 重写组织数据选中的商品的id {sku_id:count,sku_id:count,}
            selected_cart  = {}
            for sku_id in selected_ids:
                selected_cart[int(sku_id)]=int(redis_count_id[sku_id])

            #     2.4  [sku_id,sku_id,sku_id]
            ids = selected_cart.keys()
            #     2.5  [SKU,SKU,SKU]
            skus = SKU.objects.filter(pk__in=ids)
            #     2.6 遍历商品列表
            for sku in skus:
                #         sku
                #         先判断库存
                count = selected_cart[sku.id]
                if sku.stock < count:

                    #如果出现问题,则进行回滚,
                    # 回滚到 save_point 这里 当时记录的 回滚点
                    transaction.savepoint_rollback(save_point)

                    raise serializers.ValidationError('库存不足')
                #         如果库存充足,则可以售卖
                #         库存减少
                #         销量增加

                import time

                # time.sleep(10)

                # sku.stock -= count
                # sku.sales += count
                # sku.save()

                # 乐观锁
                # 1. 先记录(查询)数据
                old_stock=sku.stock         # 20
                old_sales=sku.sales

                #2.更新的数据 组织出来
                new_stock = sku.stock - count
                new_sales = sku.sales + count

                #3. 在更新前 再次查询数据
                # 返回受影响的行数 如果是0 则表明更新失败
                rect = SKU.objects.filter(pk=sku.id,stock=old_stock).update(stock=new_stock,sales=new_sales)

                if rect == 0:

                    transaction.savepoint_rollback(save_point)

                    raise serializers.ValidationError('下单失败')

                """
                一锅肉包子  20
                甲乙2个人

                甲看了一眼: 20
                乙看了一眼: 20

                甲: 想吃的时候看一下是否是20个 吃了10   剩下10个
                乙: 不吃了

                """

                #
                #         再累加计算总价格和总数量
                order.total_count += count
                order.total_amount += (count*sku.price)
                #         将售卖的sku添加到
                #         订单商品中
                #         OrderGoods.objects.create()
                OrderGoods.objects.create(
                    order=order,
                    sku=sku,
                    count=count,
                    price=sku.price
                )

            order.save()


            # 如果没有问题,则提交
            transaction.savepoint_commit(save_point)
        #
        #
        # 3. 订单和商品列表生成了之后,需要将 redis中选中商品删除


        return order
