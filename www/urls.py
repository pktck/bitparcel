from django.conf.urls.defaults import patterns, include, url
from django.conf import settings

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'www.views.home', name='home'),
    # url(r'^www/', include('www.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),

    url(r'^$', 'main.views.front'),
    url(r'^upload$', 'main.views.upload'),
    url(r'^files/(?P<download_key>.*?)/(?P<file_key>.*?)/(?P<download_session_key>.*?)/(?P<filename>.*?)$', 'main.views.downloadFile'),
    url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_DIR}),
    url(r'^progress/(?P<download_session_key>.*?)$', 'main.views.progress'),
    url(r'^(?P<download_key>.*?)(/(?P<filename>.*))?$', 'main.views.download'),
)
