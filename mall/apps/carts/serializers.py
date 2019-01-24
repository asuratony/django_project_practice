from rest_framework import serializers

# serializers.ModelSerializer
# serializers.Serializer
from goods.models import SKU


class CartSerialzier(serializers.Serializer):

    sku_id=serializers.IntegerField(label='商品id',required=True)
    count=serializers.IntegerField(label='商品个数',required=True)
    selected=serializers.BooleanField(label='选中状态',required=False,default=True)


    def validate(self, attrs):
        sku_id = attrs.get('sku_id')
        #1判断商品是否存在,
        try:
            sku = SKU.objects.get(pk=sku_id)
        except SKU.DoesNotExist:
            raise serializers.ValidationError('商品存在')

        # 2判断库存
        count = attrs['count']
        if sku.stock < count:
            raise serializers.ValidationError('库存不足')

        return attrs



class CartSKUSerializer(serializers.ModelSerializer):

    count = serializers.IntegerField(label='个数')
    selected=serializers.BooleanField(label='选中状态')

    class Meta:
        model=SKU
        fields = ['id','name','price','default_image_url','count','selected']



class CartDeleteSerializer(serializers.Serializer):

    sku_id = serializers.IntegerField(label='商品id',required=True)

    def validate(self, attrs):
        sku_id = attrs.get('sku_id')
        #1判断商品是否存在,
        try:
            SKU.objects.get(pk=sku_id)
        except SKU.DoesNotExist:
            raise serializers.ValidationError('商品存在')


        return attrs