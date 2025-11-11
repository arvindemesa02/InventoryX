from django.contrib import admin
from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from modules.graphene_custom.custom_view import CustomGraphQLView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("graphql/", csrf_exempt(CustomGraphQLView.as_view(graphiql=True))),
]
