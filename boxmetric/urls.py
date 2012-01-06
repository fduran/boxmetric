from django.conf.urls.defaults import patterns, include, url
from django.views.generic.simple import direct_to_template
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    #(r'^test/$', 'boxmetric.app.views.testservices'),
    (r'^cp/$', 'boxmetric.app.views.dashboard'),
    (r'^admin2/', include(admin.site.urls)),
    (r'^api/(?P<command>\S+)/$', 'boxmetric.app.views.api'),
    (r'^api/(?P<command>\S+)$', 'boxmetric.app.views.api'),
#    (r'^login', 'django.contrib.auth.views.login'),
    (r'^login', 'boxmetric.app.views.login'),
    (r'^logout', 'boxmetric.app.views.logout_page'),
    #(r'^', 'django.views.generic.simple.redirect_to', {'url': 'http://opentelligent.com/media/prod/index.html'}),
    (r'^', 'boxmetric.app.views.index'),
    #(r'^', 'boxmetric.app.views.index'),
)
