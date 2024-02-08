from django.urls import include, re_path
from django.contrib import admin
from django.views.generic.base import RedirectView

urlpatterns = [
    re_path(r'^$', RedirectView.as_view(url="vote/", permanent=False)),
    re_path(r'^vote/', include('vote.urls')),
    re_path(r'^admin/', admin.site.urls),
]
