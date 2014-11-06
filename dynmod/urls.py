from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

ajaxpatterns = patterns('dynmod.ajax',
    url(r'^get_models/$', 'get_models'),
    url(r'^model/(?P<model_name>\w+)/$', 'model'),
    url(r'^model_objects/(?P<model_name>\w+)/$', 'model_objects'),
)

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'dynmod.views.home', name='home'),
    url(r'^restart/$', 'dynmod.views.restart', name='restart'),
    url(r'^models_editor/$', 'dynmod.views.models_editor', name='models_editor'),
    url(r'^ajax/', include(ajaxpatterns)),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
)
