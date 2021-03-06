"""django_rest URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
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
from django.contrib import admin
from django.conf.urls import url, include
from api import views

urlpatterns = [
    url(r'^o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^sign_up/$', views.SignUp.as_view(), name="sign_up"),
    url(r'^user_activation_link/(?P<user_id>(\w+))/(?P<token>([A-Za-z0-9]+)-([A-Za-z0-9]+)-([A-Za-z0-9]+)-([A-Za-z0-9]+)-([A-Za-z0-9]+))+/$',
        views.UserActivation.as_view(), name="user_activation_link"),
    url(r'^login/$', views.UserAPILoginView.as_view(), name="login"),
    url(r'^users/$', views.UserList.as_view()),
    url(r'^change-password/$',
        views.ChangePassword.as_view(), name='change-password'),
]
