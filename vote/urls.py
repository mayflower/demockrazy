from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.create, name='create'),
    url(r'^(?P<poll_identifier>[a-zA-Z]+)/$', views.poll, name='poll'),
    url(r'^(?P<poll_identifier>[a-zA-Z]+)/vote/$', views.vote, name='vote'),
    url(r'^(?P<poll_identifier>[a-zA-Z]+)/success/$', views.success, name='success'),
]