"""pol_harvester URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.views.decorators.csrf import csrf_exempt
from django.contrib.sitemaps.views import sitemap

from rest_framework.authtoken import views as rest_views

from pol_harvester import views
from pol_harvester.models.documents import DocumentSitemap
from search.urls import router as search_router


api_urlpatterns = [
    url(r'^document/(?P<pk>\d+)/content/$', views.DocumentContentView.as_view(), name="document-content"),
    url(r'^document/(?P<pk>\d+)/$', views.DocumentView.as_view(), name="document"),
    url(r'^arrangement/(?P<pk>\d+)/content/$', views.ArrangementContentView.as_view(), name="arrangement-content"),
    url(r'^arrangement/(?P<pk>\d+)/$', views.ArrangementView.as_view(), name="arrangement"),
    url(r'^collection/(?P<pk>\d+)/content/$', views.CollectionContentView.as_view(), name="collection-content"),
    url(r'^collection/(?P<pk>\d+)/$', views.CollectionView.as_view(), name="collection"),
    url(r'^freeze/(?P<pk>\d+)/content/$', views.FreezeContentView.as_view(), name="freeze-content"),
    url(
        r'^freeze/(?P<pk>\d+)/annotate/(?P<annotation_name>[A-Za-z0-9\-_: +"]+)/$',
        views.AnnotationView.as_view(),
        name="freeze-annotation"
    ),
    url(r'^freeze/(?P<pk>\d+)/$', views.FreezeDetailView.as_view(), name="freeze"),
    url(r'^freeze/$', views.FreezeListView.as_view(), name="freeze"),
    url(r'^search/', include(search_router.urls)),
]


urlpatterns = [
    url(r'^health/?$', views.health, name="health-check"),
    url(r'^admin/', admin.site.urls),
    url(r'^content/sitemap.xml', sitemap, {'sitemaps': {"alpha": DocumentSitemap("alpha")}},
        name='django.contrib.sitemaps.views.sitemap'),
    url(r'^content/documents/(?P<pk>\d+)/$', views.document_html_view, name="content-document-html"),
    url(r'^api/v1/', include(api_urlpatterns, namespace="api-v1")),
    url(r'^api/v1/auth/token/?$', csrf_exempt(rest_views.obtain_auth_token)),
]
