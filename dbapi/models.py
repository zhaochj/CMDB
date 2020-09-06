from django.db import models
import json
from .types import get_instance


class Schema(models.Model):
    class Meta:
        db_table = 'schema'

    name = models.CharField(max_length=48)
    desc = models.CharField(max_length=128, blank=True, null=True)
    deleted = models.BooleanField(default=False)
    delete_date = models.DateTimeField(null=True, help_text="逻辑表删除时间")

    def __str__(self):
        return str('<{}>'.format(self.name))


class reference:
    """虚拟表外键约束解析"""
    def __init__(self, ref: dict):
        self.schema = ref['schema']
        self.field = ref['field']
        self.on_delete = ref.get('on_delete', 'disable')
        self.on_update = ref.get('on_update', 'disable')


class FieldMeta:
    """解析meta字符串"""
    def __init__(self, meta_str: str):
        # {'type': {'name': 'dbapi.types.IP', 'option': {'prefix': '192.168'}}, 'nullable': True, 'unique': False, 'default': '', 'multi': True}
        meta = json.loads(meta_str)
        if isinstance(meta['type'], str):  # type如果是简写的方式
            self.instance = get_instance(meta['type'])
        else:
            option = meta['type'].get('option')  #
            type_str = json.dumps(meta['type']['name'])
            if option:
                self.instance = get_instance(type_str, option)
            else:
                self.instance = get_instance(type_str)
        self.nullable = meta.get('nullable', False)  # 默认不可为空
        self.unique = meta.get('unique', True)   # 默认为唯一
        self.default = meta.get('default')
        self.multi = meta.get('multi', False)  # 默认不可存放多值

        ref = meta.get('reference')
        if ref:
            self.reference = reference(ref)
        else:
            self.reference = None


class Field(models.Model):
    """字段表，记录虚拟表的对应的字段名称
        meta字段是对字段的属性定义以及各种约束，格式如下：
        {
            "type":{
                "name":"dbapi.types.IP",
                "option":{
                    "prefix":"192.168"
                }
            },
            "nullable":true,
            "unique":false,
            "default":"",
            "multi":true,
            "reference":{
                "schema":"ippool",
                "field":"ip",
                "on_delete":"cascade|set_null|disable",   表示取一个值
                "on_update":"cascade|disable"     表示取一个值
            }

        }
        如果没有option，还可以简写为：
        {
            "type":"dbapi.types.IP",
            "unique":true,
            ...
        }
        """

    class Meta:
        db_table = 'field'

    name = models.CharField(max_length=48)
    meta = models.TextField(blank=True, null=True)
    ref_id = models.ForeignKey('Field', null=True, on_delete=models.DO_NOTHING, help_text='自关联字段')
    schema = models.ForeignKey('Schema', on_delete=models.DO_NOTHING)
    deleted = models.BooleanField(default=False)

    def __str__(self):
        return str('<{}>'.format(self.name))


class Entity(models.Model):
    class Meta:
        db_table = 'entity'

    key = models.CharField(max_length=48)
    schema = models.ForeignKey('Schema', on_delete=models.DO_NOTHING)
    deleted = models.BooleanField(default=False)


class Value(models.Model):
    class Meta:
        db_table = 'value'

    value = models.TextField()
    field = models.ForeignKey('Field', on_delete=models.DO_NOTHING)
    entity = models.ForeignKey('Entity', on_delete=models.DO_NOTHING)
    deleted = models.BooleanField(default=False)
