"""mysite URL Configuration

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
from django.conf.urls import url,include
from django.contrib import admin
from . import views


urlpatterns = [
    url(r'^$', views.google_contacts_app, name='google_contacts_app'),
    url(r'^google/login$', views.login, name='login'),
    url(r'^google/auth$', views.google_auth_redirect, name='google_auth_redirect'),
    url(r'^google_contacts_app$', views.google_contacts_app, name='google_contacts_app'),
    url(r'^add_contact$', views.add_contact, name='add_contact'),
    url(r'^privacy_policy$', views.privacy_policy, name='privacy_policy'),
    url(r'^send_mail$', views.send_mail, name='send_mail'),

]
