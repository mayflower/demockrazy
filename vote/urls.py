from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^(?P<poll_identifier>[a-zA-Z]+)/$', views.poll, name='poll'),
]