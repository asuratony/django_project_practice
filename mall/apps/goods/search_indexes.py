from haystack import indexes

from .models import SKU

# 类 需要继承自  indexes.SearchIndex, indexes.Indexable
class SKUIndex(indexes.SearchIndex, indexes.Indexable):
    """
    SKU索引数据模型类
    """
    # text 是习惯的命名
    # 需要有一个（也是唯一一个）字段 document=True
    # use_template=True 可以使用模板 来设置 搜索的字段
    text = indexes.CharField(document=True, use_template=True)


    id = indexes.IntegerField(model_attr='id')
    name = indexes.CharField(model_attr='name')
    price = indexes.CharField(model_attr='price')
    default_image_url = indexes.CharField(model_attr='default_image_url')
    comments = indexes.IntegerField(model_attr='comments')

    def get_model(self):
        """返回建立索引的模型类"""
        return SKU

    def index_queryset(self, using=None):
        """返回要建立索引的数据查询集"""
        return self.get_model().objects.filter(is_launched=True)