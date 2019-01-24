from django.core.files.storage import Storage
from fdfs_client.client import Fdfs_client
from django.utils.deconstruct import deconstructible
from mall import settings

#1.您的自定义存储系统必须是以下子类 django.core.files.storage.Storage

#4.您的存储类必须是可解构的， 以便在迁移中的字段上使用它时可以对其进行序列化。
# 只要您的字段具有可自行序列化的参数，
# 就 可以使用 django.utils.deconstruct.deconstructible类装饰器（
# 这就是Django在FileSystemStorage上使用的)


@deconstructible
class MyStorage(Storage):
    #2.Django必须能够在没有任何参数的情况下实例化您的存储系统。
    # 这意味着任何设置都应该来自django.conf.settings
    # def __init__(self, option=None):
    #     if not option:
    #         option = settings.CUSTOM_STORAGE_OPTIONS

    def __init__(self,client_config=None,client_url=None):
        if not client_config:
            client_config=settings.FDFS_CLIENT_CONF
            self.client_config=client_config
        if not client_url:
            client_url=settings.FDFS_URL
            self.client_url=client_url




    #3.您的存储类必须实现_open()和_save() 方法以及
    # 适用于您的存储类的任何其他方法
    # open 打开
    # 因为我们是通过 http 来获取 Fdfs 图片的
    # 所以 不需要打开
    def _open(self, name, mode='rb'):
        pass

    # save 保存
    def _save(self, name, content, max_length=None):

        #name,                  图片的名字
        # content,              内容 上传的图片的内容
        #  max_length=None


        #1.创建Fdfs的客户端,创建客户端的时候加载配置信息
        # client = Fdfs_client('utils/fastdfs/client.conf')
        # client = Fdfs_client(settings.FDFS_CLIENT_CONF)
        client = Fdfs_client(self.client_config)
        #2.获取上传的图片
        # 读取 图片的二进制数据
        data = content.read()
        #3.上传,并接收上传结果
        # upload_by_buffer   上传二进制
        result = client.upload_by_buffer(data)
        #4.根据上传状态 获取file_id
        """
        {'Local file name': '/home/python/Desktop/images/1.jpg',
        'Storage IP': '192.168.229.148',
         'Status': 'Upload successed.',
         'Group name': 'group1',
         'Uploaded size': '183.00KB',
         'Remote file_id': 'group1/M00/00/02/wKjllFw9jeKAQxYPAALd0X8OZb4106.jpg'}

        """
        if result.get('Status') == 'Upload successed.':
            # 说明上传成功
            file_id = result.get('Remote file_id')
        else:
            raise Exception('上传失败')

        # 一定要记得返回
        return file_id

    # exists 存在
    # 因为Fdfs已经做了重名的处理,我们不需要判断是否存在
    def exists(self, name):
        return False

    # 默认的url 会将 name(file_id) 返回回去
    # 但是我们在访问 Fdfs的时候 是通过 ip:port + name(file_id)
    def url(self, name):

        # return 'http://192.168.229.148:8888/'+name
        # return settings.FDFS_URL + name
        return self.client_url + name


# class Person(object):
#
#
#     def __init__(self,name=None):
#         pass
#
# p = Person()

