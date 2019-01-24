from rest_framework import serializers

from areas.models import Area


class AreaSerializer(serializers.ModelSerializer):

    class Meta:
        model = Area
        fields = ['id','name']



# 市,区县序列化器中
class SubsAreaSerialzier(serializers.ModelSerializer):


    # area_set = AreaSerializer(many=True)
    subs = AreaSerializer(many=True)

    class Meta:
        model=Area
        fields=['subs','id','name']
        # fields=['area_set']

