"""BBS URL Configuration

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
from django.views.static import serve  # 处理静态文件，上传的文件在HTML中显示
from blog import views
from BBS.settings import MEDIA_ROOT
from blog import urls as blog_urls

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    url(r'^login/', views.login),
    url(r'^reg/', views.register),
    url(r'^index/', views.index),
    url(r'^logout/', views.logout),
    url(r'^blog/', include(blog_urls)),


    # 极验滑动验证码 获取验证码的url
    url(r'^pc-geetest/register', views.get_geetest),
    # 验证用户名是否存在
    url(r'^check_username_exist/$', views.check_username_exist),
    url(r'^media/(?P<path>.*)$', serve, {"document_root": MEDIA_ROOT}),  # 上传静态文件的查找路径
]