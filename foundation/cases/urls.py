# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url
from . import views

urlpatterns = [
   url(r'^$', views.CaseListView.as_view(), name="list"),
   url(r'^~create$', views.CaseCreateView.as_view(), name="create"),
   url(r'^sprawa-(?P<slug>[\w-]+)$', views.CaseDetailView.as_view(), name="details"),
   url(r'^sprawa-(?P<slug>[\w-]+)/~update$', views.CaseUpdateView.as_view(), name="update"),
   url(r'^sprawa-(?P<slug>[\w-]+)/~delete$', views.CaseDeleteView.as_view(), name="delete"),
]
