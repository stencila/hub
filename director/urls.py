"""
URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/

Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path

from views import (
    HomeView,
    OpenView
)
from projects.views import (
    ProjectListView,
    ProjectReadView,
    ProjectCreateView,
    ProjectUpdateView,
    ProjectDeleteView,
    ProjectArchiveView
)

urlpatterns = [

    path('projects/', include([
        path('',                  ProjectListView.as_view(),     name='project_list'),
        path('create/',           ProjectCreateView.as_view(),   name='project_create'),
        path('<int:pk>/',         ProjectReadView.as_view(),     name='project_read'),
        path('<int:pk>/update/',  ProjectUpdateView.as_view(),   name='project_update'),
        path('<int:pk>/delete/',  ProjectDeleteView.as_view(),   name='project_delete'),
        path('<int:pk>/archive/', ProjectArchiveView.as_view(),  name='project_archive')
    ])),

    path('admin/', admin.site.urls),
    path('me/', include('allauth.urls')),

    path('open',   OpenView.as_view(), name='open'),
    path('',       HomeView.as_view(), name='home')
]
