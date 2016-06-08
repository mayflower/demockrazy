from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^vote/', include('vote.urls', namespace='vote')),
    url(r'^admin/', admin.site.urls),
]