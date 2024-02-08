from django.urls import include, re_path

from . import views

app_name = 'vote'

pollpatterns = ([
    re_path(r'^$', views.poll, name='poll'),
    re_path(r'^vote$', views.vote, name='vote'),
    re_path(r'^success$', views.success, name='success'),
    re_path(r'^manage$', views.manage, name='manage'),
    re_path(r'^results$', views.results, name='result'),
], 'polls')

urlpatterns = [
    re_path(r'^$', views.index, name='index'),
    re_path(r'^create$', views.create, name='create'),
    re_path(r'^(?P<poll_identifier>[a-zA-Z0-9]+)/', include(pollpatterns)),
]
