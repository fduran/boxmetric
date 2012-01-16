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
    (r'^signup', 'boxmetric.app.views.signup'),
    # timeline URLs
    (r'^timeline/(?P<year>\d{4})/(?P<month>\d{2})$', 'boxmetric.app.views.timeline_by_year_month'),
    (r'^timeline/(?P<year>\d{4})/$', 'boxmetric.app.views.timeline_by_year'),
    (r'^timeline/', 'boxmetric.app.views.timeline_all'),
    # email view URLs
    (r'^emails/(?P<folder>\S+)/(?P<year>\d{4})/(?P<month>\d{2})/week/(?P<week>\d{1})$', 'boxmetric.app.views.emails_by_folder_year_month_week'),
    (r'^emails/(?P<folder>\S+)/(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})$', 'boxmetric.app.views.emails_by_folder_year_month_day'),
    (r'^emails/(?P<folder>\S+)/(?P<year>\d{4})/(?P<month>\d{2})$', 'boxmetric.app.views.emails_by_folder_year_month'),
    (r'^emails/(?P<folder>\S+)/(?P<year>\d{4})/$', 'boxmetric.app.views.emails_by_folder_year'),
    (r'^emails/(?P<folder>\S+)/', 'boxmetric.app.views.emails_by_folder'),
    (r'^emails/', 'boxmetric.app.views.emails_summary'),
    # email data URLs
    (r'^emaildata/(?P<type>\S+)/(?P<year>\d{4})/(?P<month>\d{2})/week/(?P<week>\d{1})$', 'boxmetric.app.views.emaildata_by_type_year_month_week'),
    (r'^emaildata/(?P<type>\S+)/(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})$', 'boxmetric.app.views.emaildata_by_type_year_month_day'),
    (r'^emaildata/(?P<type>\S+)/(?P<year>\d{4})/(?P<month>\d{2})$', 'boxmetric.app.views.emaildata_by_type_year_month'),
    (r'^emaildata/(?P<type>\S+)/(?P<year>\d{4})/$', 'boxmetric.app.views.emaildata_by_type_year'),
    (r'^emaildata/(?P<type>\S+)', 'boxmetric.app.views.emaildata_by_type'),
    (r'^emaildata/', 'boxmetric.app.views.emaildata_summary'),
    # smart email views 
    (r'^smart-emails/(?P<email_pattern_name>\S+)', 'boxmetric.app.views.smart_emails'),
    # static web page URLs
    (r'^page/(?P<page_name>\S+)$', 'boxmetric.app.views.page'),
    # account configuration settings URLs
    (r'^account-settings/(?P<section_name>\S+)', 'boxmetric.app.views.account_settings_by_section'),
    # root URLs
    #(r'^', 'django.views.generic.simple.redirect_to', {'url': 'http://opentelligent.com/media/prod/index.html'}),
    (r'^', 'boxmetric.app.views.index'),
    #(r'^', 'boxmetric.app.views.index'),
)
