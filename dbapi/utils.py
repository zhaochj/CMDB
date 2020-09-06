import logging
import math


def get_logger(mod_name: str, filepath: str):
    """
    日志函数
    :param mod_name: 模块名称
    :param filepath: 文件路径
    :return: logger对象
    """
    logger = logging.getLogger(mod_name)
    logger.setLevel(logging.INFO)
    logger.propagate = False  # 阻止传递给父logger
    handler = logging.FileHandler(filepath)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter(fmt='%(asctime)s [%(name)s %(funcName)s] %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


def paginate(page, size, query):
    """
    分页函数
    :param page: 页码
    :param size: 一页显示数据条数
    :param query: query对象
    :return: query对象以及分页信息返回
    """
    # 分页信息
    page = page if page > 0 else 1  # 第几页，前端传递，需要做一次简单验证
    size = size if 0 < size < 100 else 10  # 一页显示条数，前端传递，需要做一次简单验证
    count = query.count()  # 数据集总数
    pages = math.ceil(count / size)  # 总页数
    result = query.all()[size*(page-1): size*page]
    return result, [page, size, count, pages]  # query对象以及分页信息返回

