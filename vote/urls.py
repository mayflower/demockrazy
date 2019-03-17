from django.conf.urls import include, url

from . import views

pollpatterns = [
    url(r'^$', views.poll, name='poll'),
    url(r'^vote$', views.vote, name='vote'),
]

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^create$', views.create, name='create'),
    url(r'^success$', views.success, name='success'),
    url(r'^manage$', views.manage, name='manage'),
    url(r'^results$', views.results, name='result'),
    url(r'^(?P<poll_identifier>[a-zA-Z0-9]+)/', include((pollpatterns, 'poll'), namespace='poll')),
]
