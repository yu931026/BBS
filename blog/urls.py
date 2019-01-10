#!/usr/bin/env python
# _*_ encoding:utf-8 _*_
__author__ = '于sir'
__date__ = '2019/1/2 18:34'

from django.conf.urls import url
from blog import views

urlpatterns = [
    url(r'^up_down/$', views.up_down),  # 点赞，踩
    url(r'^comment/$', views.comment),  # 评论
    url(r'^comment_tree/(\d+)/$', views.comment_tree),  # 评论树
    url(r'^add_article/$', views.add_article),  # 添加文章管理（富文本）
    url(r'^upload/$', views.upload),  # 添加文章管理（富文本）
    url(r'^(?P<username>\w+)/article/(?P<pk>\d+)/$', views.article_detail),  # 文章详情
    url(r'^(?P<username>\w+)/$', views.home),  # 个人主页


]