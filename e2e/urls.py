from django.contrib import admin
from django.urls import path
from main import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.landing),
    path('user/<slug:uid>', views.user),
    path('ajax/<slug:uid>', views.ajax),
    path('e1/<slug:uid>',views.exchange1),
    path('server/save/',views.serverSave),
    path('server/all/',views.serverGetAll),
    path('test/',views.test),
]
