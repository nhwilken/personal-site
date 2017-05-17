from django.conf.urls import url
from . import views

urlpatterns = [

    # recipe_list urls
    url(r'^$', views.recipe_list,
        name='recipe_list'),
    url(r'^searchrecipelist/$',
        views.search_recipe_list,
        name='recipe_filter'),
    url(r'^newrecipe/$',
        views.recipe_new,
        name='recipe_new'),

    # recipe_detail urls
    url(r'^(?P<pk>\d+)/$',
        views.recipe_detail,
        name='recipe_detail'),
    url(r'^(?P<pk>\d+)V(?P<version_num>\d+)/edit/$',
        views.recipe_edit,
        name='recipe_edit'),
    url(r'^(?P<version_id>\d+)/deleteversion/$',
        views.delete_version,
        name='delete_version'),
    url(r'^(?P<recipe_id>\d+)/addversion/$',
        views.add_version,
        name='add_version'),


    # recipe edit urls
    url(r'^(?P<recipe_id>\d+)/convertform/$',
        views.list_to_form,
        name='list_to_form'),



]
