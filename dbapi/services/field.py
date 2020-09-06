from ..utils import get_logger
from ..settings import LOG_DIR
from .schema import get_schema_by_name
from ..models import Field, Entity, Value
from ..models import FieldMeta


logger = get_logger(__name__, '{}/{}.log'.format(LOG_DIR, __name__))


def get_fields(schema_name: str, deleted=False):
    """
    根据表名获取一个表的所有字段信息
    :param schema_name: 表名称
    :param deleted:
    :return:
    """
    schema = get_schema_by_name(schema_name)
    if not schema:
        raise ValueError('Error: schema name {} not exists.'.format(schema_name))
    qs = Field.objects.filter(schema_id=schema.id)
    if not deleted:
        qs = qs.filter(deleted=False)
    return qs.all()


def table_used(schema_id, deleted=False):
    """
    判断一个逻辑表是否已经在使用
    :param schema_id:
    :param deleted:
    :return:
    """
    query = Entity.objects.filter(schema_id=schema_id)
    if not deleted:
        query = query.filter(deleted=False)
    return query.first()  # None表示表未使用，非None表示该表已有记录


def get_field_info(schema_name: str, field_name: str, deleted=False):
    """
    获取一个表的一个字段信息
    :param schema_name:
    :param field_name:
    :param deleted:
    :return:
    """
    schema = get_schema_by_name(schema_name)
    if not schema:
        raise ValueError('Error: schema name {} not exists.'.format(schema_name))
    query = Field.objects.filter(schema_id=schema.id, name=field_name)
    if not deleted:
        query = query.filter(deleted=False)
    return query.first()


def _add_field(field: Field):
    """
    增加字段
    :param field:
    :return:
    """
    try:
        field.save()
        return field
    except Exception as e:
        logger.error('Failed to add a field {}. Error: {}'.format(field.name, e))


def iter_entities(schema_id, path=50):
    """
    分批处理优化函数，类似分页处理的代码
    :param schema_id: 逻辑表id
    :param path: 一批处理数据量
    :return: QuerySet
    """
    page = 1
    while True:
        query = Entity.objects.filter(schema_id=schema_id, deleted=False)
        result = query.all()[path*(page-1): path*page]
        if not result:
            return None
        yield from result
        page += 1


def add_field(schema_name: str, field_name: str, meta: str):
    """
    在一个表上增加一个字段需要考虑的因素很多：
    1. 定义的meta格式是否正确，需要对传入的meta进行解析
    2. 增加的字段是否和其他字段有外键约束，即meta中是否有reference
    3. 增加字段的表是否已经有数据记录，即是否已经在使用，没使用直接增加字段
    4. 增加字段的表已经在使用时，meta中要求nullable可为空时，直接增加
    5. 表已经在使用，nullable要求不为空，且要求unique时，直接抛错，违反常理
    6. 表已经在使用，nullable要求不为空，不要求unique，且提供default值时，可以增加
    :param schema_name:
    :param field_name:
    :param meta:
    :return:
    """

    # 先检查schema是否存在
    schema = get_schema_by_name(schema_name)
    if not schema:
        raise ValueError('Error: schema name {} not exists.'.format(schema_name))

    # 检查schema中是否有field存在
    # field_obj = get_field_info(schema_name, field_name)
    # if field_obj:
    #     raise ValueError('Error: field name {} already exists.'.format(field_obj))

    # 先解析meta
    meta_data = FieldMeta(meta)  # 实例化，能解析成功格式才符合要求
    field = Field()
    field.name = field_name.strip()
    field.meta = meta
    field.schema_id = schema.id

    # ref_id引用
    if meta_data.reference:
        # 获得引用的字段
        ref = get_field_info(meta_data.reference.schema, meta_data.reference.field)
        if not ref:
            raise TypeError('Wrong reference {}.{}.'.format(meta_data.reference.schema, meta_data.reference.field))
        field.ref_id_id = ref.id  # 数据库实体上动态绑定ref.id

    # 判断逻辑表是否在使用
    if not table_used(schema.id):  # 逻辑表没有使用时，直接增加字段
        return _add_field(field)

    # 隐含逻辑表已使用
    # 字段允许为空值
    if meta_data.nullable:  # 允许为空，直接增加
        return _add_field(field)

    # 已使用逻辑表，隐含字段不允许为空
    if meta_data.unique:  # 还要求unique，不合理，做不到
        raise TypeError('This field is required an unique.')

    # 已使用逻辑表，且不允许为空，可以不唯一，那就看是否有default值了
    if not meta_data.default:
        raise TypeError('This field need a default value.')
    else:
        # 有默认值时，且有外键引用，抛异常
        if field.ref_id_id:
            raise ValueError('Error: You give a default value')
        # 为逻辑表所有记录增加字段
        field_obj = _add_field(field)
        value_insert = []
        for entity in iter_entities(schema.id):
            value_insert.append(Value(value=meta_data.default, entity=entity, field=field_obj))
        Value.objects.bulk_create(value_insert)  # 批量插入数据
        return field_obj
