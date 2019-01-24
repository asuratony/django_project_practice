from django.db import models

# 省
class Area(models.Model):
    name = models.CharField(max_length=20, verbose_name='名称')
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True,related_name='subs', blank=True, verbose_name='上级行政区划')
    # area_set = [Area,Area]
    # subs = [Area,Area]
    class Meta:
        db_table = 'tb_areas'
        verbose_name = '行政区划'
        verbose_name_plural = '行政区划'
    def __str__(self):
        return self.name

# class Area(models.Model):
#     # 市
#     # area_set = [Area,Area]
#     class Meta:
#         db_table = 'tb_areas'


"""
id          name        parent_id

1000        北京省         NULL

1010        北京市         1000


1011        昌平区         1010
1012        海淀区         1010
1013        朝阳区         1010


"""



