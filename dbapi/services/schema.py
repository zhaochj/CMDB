from django.db.models import Q
from ..models import Schema
from ..utils import get_logger, paginate
from ..settings import LOG_DIR
import datetime


logger = get_logger(__name__, '{}/{}.log'.format(LOG_DIR, __name__))


def get_schema_by_name(name: str, deleted=False):
    """
    根据表名称查询接口
    :param name: 表名称
    :param deleted: 是否删除
    :return: query对象
    """
    qs = Schema.objects.filter(name=name.strip())
    if not deleted:
        qs = qs.filter(deleted=False, delete_date__isnull=True)
    return qs.first()   # 当qs为空queryset时返回 None


def add_schema(name: str, desc: str = None):
    """
    增加一虚拟表接口
    :param name: 表名称
    :param desc: 表描述信息
    :return: 表对象
    """
    if not get_schema_by_name(name):
        schema = Schema()
        schema.name = name
        schema.desc = desc
        try:
            schema.save()
            logger.info('Add a schema. id:{} name:{}'.format(schema.id, schema.name))
            return schema
        except Exception as e:
            logger.error('Failed to add schema {}. Error: {}'.format(name, e))


def drop_schema(schema_id: int):
    """
    删除一张虚拟表接口，使用id来删除比使用name要好
    :param schema_id: 表的id
    :return: 表对象
    """
    try:
        obj = Schema.objects.get(Q(id=schema_id) & Q(deleted=False))
        if obj:
            obj.deleted = True
            obj.delete_date = datetime.datetime.now()
            try:
                obj.save()
                logger.info('Delete a schema. id:{} name:{}'.format(obj.id, obj.name))
                return obj
            except Exception as e:
                raise e  # 外层有捕获，直接raise
        else:
            raise ValueError('Wrong ID {}'.format(id))  # 不是在try...except中不能直接raise，需要有具体的错误类型
    except Exception as e:
        logger.error('Failed to drop schema {}. Error: {}'.format(schema_id, e))


def list_schema(page: int, size: int, deleted=False):
    """
    列表逻辑表，列表正在使用的，即未删除的表
    :param page: 第几页
    :param size: 一页显示数据量
    :param deleted: 删除状态
    :return:
    """
    query = Schema.objects
    if not deleted:
        query.filter(deleted=False)
    try:
        result = paginate(page, size, query)
        return result
    except Exception as e:
        logger.error('Failed to paginate. Error: {}'.format(e))