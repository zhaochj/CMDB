from django.urls import path
from . import views

urlpatterns = [
    path('v1/schema/list/', views.list_all_schema),
    path('v1/schema/add/', views.add_schema),
    path('v1/schema/get_fields/', views.get_schema_fields),
    path('v1/schema/drop/', views.drop_schema),
    path('v1/schema/used/', views.schema_is_used),


    path('v1/schema/field/add/', views.add_field_for_schema),
]
