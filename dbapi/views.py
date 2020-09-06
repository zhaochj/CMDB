from django.shortcuts import render
from .utils import get_logger
from django.http import JsonResponse, HttpRequest, HttpResponse, HttpResponseBadRequest
import simplejson, json
from .models import Schema, Field
from django.views.decorators.http import require_http_methods
from .settings import LOG_DIR
from .services import schema, field


logger = get_logger(__name__, '{}/{}.log'.format(LOG_DIR, __name__))


@require_http_methods(['POST'])
def list_all_schema(request: HttpRequest):
    """获取schema逻辑表"""
    payloads = simplejson.loads(request.body)
    page = payloads['page']
    size = payloads['size']
    result = schema.list_schema(page, size)
    if result:
        res, page_info = result
        return JsonResponse({
            "schema": list(res.values()),
            "page_info": page_info
        })
    else:
        return HttpResponseBadRequest()


@require_http_methods(["POST"])
def add_schema(request):
    """增加资产表"""
    payloads = simplejson.loads(request.body)
    name = payloads['name']
    desc = payloads.get('desc')
    obj = schema.add_schema(name, desc)
    if obj:
        return JsonResponse({
            "id": obj.id,
            "name": obj.name
        })
    else:
        return HttpResponseBadRequest()


@require_http_methods(['POST'])
def drop_schema(request: HttpRequest):
    payloads = simplejson.loads(request.body)
    drop_schema_id = payloads['id']
    res = schema.drop_schema(drop_schema_id)
    if res:
        return JsonResponse({
            "is_drop": True
        })
    else:
        return JsonResponse({
            "is_drop": False
        })


@require_http_methods(['POST'])
def get_schema_fields(request: HttpRequest):
    """获取逻辑表的字段列表"""
    payloads = simplejson.loads(request.body)
    try:
        name = payloads["name"]
    except Exception as e:
        return HttpResponseBadRequest('Params error')

    res = field.get_fields(name)
    return JsonResponse({
        "fields": [(q.pk, q.name) for q in res]
    })


@require_http_methods(['POST'])
def schema_is_used(request: HttpRequest):
    """判断逻辑表是否已使用"""
    payloads = simplejson.loads(request.body)
    try:
        schema_id = payloads["name"]
    except Exception as e:
        return HttpResponseBadRequest('Params error')
    res = field.table_used(schema_id)
    if res:
        return JsonResponse({
            "name": schema_id,
            "is_used": True
        })
    else:
        return JsonResponse({
            "name": schema_id,
            "is_used": False
        })


@require_http_methods(['POST'])
def add_field_for_schema(request: HttpRequest):
    # 表增加字段
    try:
        payloads = simplejson.loads(request.body)
        schema_name = payloads['schema_name']
        field_name = payloads['field_name']
        meta = payloads['meta']
    except Exception as e:
        return HttpResponseBadRequest()
    field_obj = field.add_field(schema_name.strip(), field_name.strip(), json.dumps(meta))
    if field_obj:
        return JsonResponse({
            "field_id": field_obj.id,
            "field_name": field_obj.name
        })
    else:
        return JsonResponse({
            "state": "error"
        })






    # try:
    #     schema = payloads['schema']
    #     qs = Schema.objects.filter(name=schema)
    #     schema_id = qs.get().id
    #     fields = payloads['fields']
    #     try:
    #         for f in fields:
    #             Field.objects.create(name=f['name'], meta=f['meta'], schema_id=schema_id)
    #         return JsonResponse({"field": "ok"})
    #     except Exception as e:
    #         raise
    # except Exception as e:
    #     return HttpResponseBadRequest()
