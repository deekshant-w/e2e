from django.contrib import admin
from django.urls import path
from main import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.landing,name='landing'),
    path('user/<slug:uid>', views.user,name='user'),
    path('ajax/<slug:uid>', views.ajax,name='ajax'),
    path('e1/<slug:uid>',views.exchange1,name='exchange1'),
    path('server/save/',views.serverSave,name='serverSave'),
    path('server/all/',views.serverGetAll,name='serverGetAll'),
    path('server/fromTS/',views.serverFromTS,name='serverFromTS'),
    path('test/',views.test),
]
