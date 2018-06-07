from django.conf.urls import include, url

from vote.views import index, poll

pollpatterns = [
    url(r'^$', poll, name='poll'),
    url(r'^vote$', views.vote, name='vote'),
    url(r'^success$', views.success, name='success'),
    url(r'^manage$', views.manage, name='manage'),
    url(r'^results$', views.results, name='result'),
]

urlpatterns = [
    url(r'^$', index, name='index'),
    url(r'^create$', views.create, name='create'),
    url(r'^(?P<poll_identifier>[a-zA-Z0-9]+)/', include(pollpatterns)),
]
