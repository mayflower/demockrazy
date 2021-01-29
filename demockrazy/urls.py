from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic.base import RedirectView

urlpatterns = [
    url(r'^$', RedirectView.as_view(url="vote/", permanent=False)),
    url(r'^vote/', include('vote.urls')),
    url(r'^admin/', admin.site.urls),
]
