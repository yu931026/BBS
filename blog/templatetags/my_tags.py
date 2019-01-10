#!/usr/bin/env python
# _*_ encoding:utf-8 _*_
__author__ = '于sir'
__date__ = '2019/1/3 10:44'


from django import template
from blog import models
from django.db.models import Count
from django.shortcuts import HttpResponse

register = template.Library()

@register.inclusion_tag("left_menu.html")
def get_left_menu(username):
    user = models.UserInfo.objects.filter(username=username).first()
    if not user:
        return HttpResponse("404")
    # 取用户的博客信息
    blog = user.blog
    # category_list = models.Category.objects.filter(blog=blog)  # 拿到所有的文章分类
    category_list = models.Category.objects.filter(blog=blog).annotate(c=Count("article")).values("title",
                                                                                                  "c")  # 分组查询拿到分类和各分类数量

    # 统计当前站点下有哪一些标签，并且按标签统计出文章数
    tag_list = models.Tag.objects.filter(blog=blog).annotate(c=Count("article")).values("title", "c")

    # 按日期归档
    archive_list = models.Article.objects.filter(user=user).extra(
        select={"archive_ym": "date_format(create_time,'%%Y-%%m')"}  # 将时间格式化为 年-月
    ).values("archive_ym").annotate(c=Count("nid")).values("archive_ym", "c")  # 按时间分组，并计数
    return {
        "category_list": category_list,
        "tag_list": tag_list,
        "archive_list": archive_list,
    }