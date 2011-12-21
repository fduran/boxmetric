from django.conf.urls.defaults import patterns, include, url
from django.views.generic.simple import direct_to_template
#from django.contrib import admin
#admin.autodiscover()

urlpatterns = patterns('',
    #(r'^admin2/', include(admin.site.urls)),
    (r'^api/(?P<command>\S+)/$', 'boxmetric.app.views.api'),
    #(r'^', 'django.views.generic.simple.redirect_to', {'url': 'http://opentelligent.com/media/prod/index.html'}),
    (r'^', direct_to_template, {'template': 'index.html', }),
    #(r'^', 'boxmetric.app.views.index'),
)
