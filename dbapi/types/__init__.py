import importlib
import ipaddress

classes_cache = {}
instances_cache = {}


def get_cls(meta_type: str):
    """
    :param meta_type: 数据库中field表中meta字段中json字符串中的type值
    :return: class
    """
    cls = classes_cache.get(meta_type.strip('"'))
    if cls:
        return cls
    # 如果缓存里未注入的类都视为非法的
    raise TypeError('Wrong Type {}. Not subclass of BaseType.'.format(meta_type))


def get_instance(meta_type: str, option: dict = None):
    """
    :param meta_type:
    :param option: meta中的option
    :return: 通过对type字串的解析处理后返回一个类型转换的实例
    """
    if option is not None and option:  # option字典不为None且不为空字典
        key = ",".join("{}={}".format(k, v) for k, v in sorted(option.items()))
        key = "{}|{}".format(meta_type, key)
        obj = instances_cache.get(key)
        if obj:
            return obj
        obj = get_cls(meta_type)(option)
        instances_cache[key] = obj
        return obj
    else:
        key = meta_type
        obj = get_cls(meta_type)(option)
        instances_cache[key] = obj
        return obj


class BaseType:
    def __init__(self, option):
        self.option = option

    def __getattr__(self, item):
        return self.option.get(item)

    def stringify(self, value):
        # 从用户端拿到数据，转换成字符串，基类未实现
        raise NotImplementedError()

    def destringify(self, value):
        # 从数据库拿数据，返回。还原数据的过程，基类不实现
        raise NotImplementedError()


class Int(BaseType):
    """
    整形类型及满园较验
    """
    def stringify(self, value):
        try:
            val = int(value)
        except Exception as e:
            raise TypeError('{} is not like digit.'.format(value))
        if self.option is not None and self.option:
            _max = self.max
            _min = self.min
            if _max and val > _max:
                raise ValueError('Too big.')
            if _min and val < _min:
                raise ValueError('Too small.')
        return str(val)  # 最后要存放在value表的value字段里，所以要str

    def destringify(self, value):
        return value


class IP(BaseType):
    # 检验IP地址
    def stringify(self, value):
        try:
            val = ipaddress.ip_address(value)
        except Exception as e:
            raise ValueError('{} does not look like ip address.'.format(value))
        if self.option is not None and self.option:
            print(self.option)
            if not str(val).startswith(str(self.prefix)):
                raise ValueError('Must startswith {}'.format(self.prefix))
            return str(val)
        return str(val)  # 无前缀约束时返回

    def destringify(self, value):
        return value


def inject_classes_cache():
    """
    类缓存函数
    :return: None
    """
    for k, v in globals().items():
        if type(v) == type and issubclass(v, BaseType) and not k.startswith('BaseType'):
            classes_cache[k] = v  # 短名称缓存
            classes_cache['{}.{}'.format(__name__, k)] = v  # 长名称缓存


# 此模块被导入时注入较验数据类型的class
inject_classes_cache()
