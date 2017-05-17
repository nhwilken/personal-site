from django.conf.urls import url
from . import views

urlpatterns = [

    # main page url
    url(r'^$', views.main_page,
        name='main_page'),
]