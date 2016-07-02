from django.conf.urls import include, patterns, url

from . import views

pollpatterns = [
    url(r'^$', views.poll, name='poll'),
    url(r'^vote$', views.vote, name='vote'),
    url(r'^success$', views.success, name='success'),
    url(r'^manage$', views.manage, name='manage'),
    url(r'^results$', views.results, name='result'),
]

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^create$', views.create, name='create'),
    url(r'^validation$', views.validation_request, name='validation_request'),
    url(r'^validate$', views.process_validation_request, name='validate'),
    url(r'^(?P<poll_identifier>[a-zA-Z0-9]+)/', include(pollpatterns)),
]
