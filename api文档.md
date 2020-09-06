### 接口文档

- 创建逻辑表

```
url 
    /dbapi/v1/schema/add/
method
    post
params
{
    "name": "phone",
    "desc": "手机"
}
return
{
    "id": 4,
    "name": "phone"
}
```

- 查询逻辑表

提交显示第几页及一面显示的条数，返回逻辑表信息及分页信息。

```
url
    /dbapi/v1/schema/list/
method
    post
params
{
    "page": 1,
    "size": 2
}
return
{
    "schema": [
        {
            "id": 1,
            "name": "host",
            "desc": null,
            "deleted": false,
            "delete_date": null
        },
        {
            "id": 2,
            "name": "ippool",
            "desc": null,
            "deleted": false,
            "delete_date": null
        }
    ],
    "page_info": [
        1,
        2,
        4,
        2
    ]
}
```

- 删除逻辑表

```
url
    /dbapi/v1/schema/drop/
method
    post
params
    {
        "id": 3
    }
return 
    {
        "is_drop": true
    }
```

- 获取逻辑表字段信息

```
url
    /v1/schema/get_fields/
method
    post
params
    {
        "name": "host"
    }
return
    {
        "fields": [
            [
                2,
                "hostname"
            ],
            [
                3,
                "ip"
            ],
            [
                27,
                "dns"
            ]
        ]
    }
```

- 逻辑表增加字段

```
url
    /dbapi/v1/schema/field/add/
method
    post
params
{
    "schema_name": "host",
    "field_name": "dns",
    "meta": {
        "type": {
            "name": "dbapi.types.IP",
            "option": {
                    "prefix": "192.168"
                }
        },
        "nullable": true,
        "unique": false,
        "default": "",
        "multi": true,
        "reference": {
            "schema":"ippool",
            "field":"ip",
            "on_delete": "disable",
            "on_update": "disable"
        }
    }
}
return
    {
        "field_id": 27,
        "field_name": "dns"
    }
```


