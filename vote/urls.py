from django.conf.urls import include, patterns, url

from . import views

pollpatterns = [
    url(r'^$', views.poll, name='poll'),
    url(r'^vote$', views.vote, name='vote'),
    url(r'^success$', views.success, name='success'),
    url(r'^manage$', views.manage, name='manage'),
]

urlpatterns = [
    url(r'^$', views.create, name='create'),
    url(r'^(?P<poll_identifier>[a-zA-Z]+)/', include(pollpatterns)),
]
