from django.conf.urls import include, url

from vote.views import *

pollpatterns = [
    url(r'^$', poll, name='poll'),
    url(r'^vote$', vote, name='vote'),
    url(r'^success$', success, name='success'),
    url(r'^manage$', manage, name='manage'),
    url(r'^results$', results, name='result'),
]

urlpatterns = [
    url(r'^$', index, name='index'),
    url(r'^create$', create, name='create'),
    url(r'^(?P<poll_identifier>[a-zA-Z0-9]+)/', include(pollpatterns)),
]
