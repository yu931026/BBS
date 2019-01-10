from django.shortcuts import render, redirect, HttpResponse
from django.http import JsonResponse
from django.contrib import auth
from geetest import GeetestLib
from blog import forms, models
from django.db.models import Count, F
import json
from django.contrib.auth.decorators import login_required



# 使用极验滑动验证码的登录

def login(request):
    # if request.is_ajax():  # 如果是AJAX请求
    if request.method == "POST":
        # 初始化一个给AJAX返回的数据
        ret = {"status": 0, "msg": ""}
        # 从提交过来的数据中 取到用户名和密码
        username = request.POST.get("username")
        pwd = request.POST.get("password")
        # 获取极验 滑动验证码相关的参数
        gt = GeetestLib(pc_geetest_id, pc_geetest_key)
        challenge = request.POST.get(gt.FN_CHALLENGE, '')
        validate = request.POST.get(gt.FN_VALIDATE, '')
        seccode = request.POST.get(gt.FN_SECCODE, '')
        status = request.session[gt.GT_STATUS_SESSION_KEY]
        user_id = request.session["user_id"]

        if status:
            result = gt.success_validate(challenge, validate, seccode, user_id)
        else:
            result = gt.failback_validate(challenge, validate, seccode)
        if result:
            # 验证码正确
            # 利用auth模块做用户名和密码的校验
            user = auth.authenticate(username=username, password=pwd)
            if user:
                # 用户名密码正确
                # 给用户做登录
                auth.login(request, user)
                ret["msg"] = "/index/"
            else:
                # 用户名密码错误
                ret["status"] = 1
                ret["msg"] = "用户名或密码错误！"
        else:
            ret["status"] = 1
            ret["msg"] = "验证码错误"

        return JsonResponse(ret)
    return render(request, "login.html")


def index(request):
    article_list = models.Article.objects.all()
    return render(request, "index.html", {"article_list": article_list})


# 请在官网申请ID使用，示例ID不可使用
pc_geetest_id = "b46d1900d0a894591916ea94ea91bd2c"
pc_geetest_key = "36fc3fe98530eea08dfc6ce76e3d24c4"


# 处理极验 获取验证码的视图
def get_geetest(request):
    user_id = 'test'
    gt = GeetestLib(pc_geetest_id, pc_geetest_key)
    status = gt.pre_process(user_id)
    request.session[gt.GT_STATUS_SESSION_KEY] = status
    request.session["user_id"] = user_id
    response_str = gt.get_response_str()
    return HttpResponse(response_str)


# 注册
def register(request):
    if request.method == "POST":
        ret = {"status": 0, "msg": ""}
        form_obj = forms.RegForm(request.POST)
        # 帮我做校验
        if form_obj.is_valid():

            # 校验通过，去数据库创建一个新的用户
            form_obj.cleaned_data.pop("re_password")
            avatar_img = request.FILES.get("avatar")  # 文件需要单独取出
            models.UserInfo.objects.create_user(**form_obj.cleaned_data, avatar=avatar_img)  # auth的内置创建用户方法
            ret["msg"] = "/index/"
            return JsonResponse(ret)
        else:
            ret["status"] = 1
            ret["msg"] = form_obj.errors
            return JsonResponse(ret)
    form_obj = forms.RegForm()
    return render(request, "register.html", {"form_obj": form_obj})


# 验证用户名是否存在的ajax
def check_username_exist(request):
    username = request.GET.get("username")
    is_exist = models.UserInfo.objects.filter(username=username)
    if is_exist:
        return JsonResponse({"status": 1, "msg": "用户已被注册！"})
    else:
        return JsonResponse({"status": 0, "msg": ""})


# 注销
def logout(request):
    auth.logout(request)
    return redirect("/index/")


# 个人博客主页
def home(request, username):
    # 取用户
    user = models.UserInfo.objects.filter(username=username).first()
    if not user:
        return HttpResponse("404")
    # 取用户的博客信息
    blog = user.blog
    # 文章列表
    article_list = models.Article.objects.filter(user=user)

    # # category_list = models.Category.objects.filter(blog=blog)  # 拿到所有的文章分类
    # category_list = models.Category.objects.filter(blog=blog).annotate(c=Count("article")).values("title", "c")  # 分组查询拿到分类和各分类数量
    #
    # # 统计当前站点下有哪一些标签，并且按标签统计出文章数
    # tag_list = models.Tag.objects.filter(blog=blog).annotate(c=Count("article")).values("title", "c")
    #
    # # 按日期归档
    # archive_list = models.Article.objects.filter(user=user).extra(
    #     select={"archive_ym": "date_format(create_time,'%%Y-%%m')"}  # 将时间格式化为 年-月
    # ).values("archive_ym").annotate(c=Count("nid")).values("archive_ym", "c")  # 按时间分组，并计数

    return render(request, "home.html", {
        "blog": blog,
        "username": username,
        "article_list": article_list,
        # "category_list": category_list,
        # "tag_list": tag_list,
        # "archive_list": archive_list,
    })


# # 获取用户的相关内容的方法, 用自定义的tag 代替
# def get_self_menu(username):
#     user = models.UserInfo.objects.filter(username=username).first()
#     if not user:
#         return HttpResponse("404")
#     # 取用户的博客信息
#     blog = user.blog
#     # category_list = models.Category.objects.filter(blog=blog)  # 拿到所有的文章分类
#    分组查询拿到分类和各分类数量
#     category_list = models.Category.objects.filter(blog=blog).annotate(c=Count("article")).values("title", "c")
#
#     # 统计当前站点下有哪一些标签，并且按标签统计出文章数
#     tag_list = models.Tag.objects.filter(blog=blog).annotate(c=Count("article")).values("title", "c")
#
#     # 按日期归档
#     archive_list = models.Article.objects.filter(user=user).extra(
#         select={"archive_ym": "date_format(create_time,'%%Y-%%m')"}  # 将时间格式化为 年-月
#     ).values("archive_ym").annotate(c=Count("nid")).values("archive_ym", "c")  # 按时间分组，并计数
#     return category_list, tag_list, archive_list


# 文章详情
def article_detail(request, username, pk):
    user = models.UserInfo.objects.filter(username=username).first()
    if not user:
        return HttpResponse("404")
    # 取用户的博客信息
    blog = user.blog
    article_obj = models.Article.objects.filter(pk=pk).first() # 找到当前文章

    # 评论列表
    comment_list = models.Comment.objects.filter(article_id=pk)

    return render(request, "detail.html", {
        "article_obj": article_obj,
        "blog": blog,
        "username": username,
        "comment_list": comment_list
    })


# 点赞或反对
def up_down(request):
    if request.method == 'POST':
        article_id = request.POST.get("article_id")
        is_up = json.loads(request.POST.get("is_up"))
        user = request.user
        response = {"status": True}
        try:
            models.ArticleUpDown.objects.create(user=user, article_id=article_id, is_up=is_up)  # 新建一个点赞数据
            if is_up:
                models.Article.objects.filter(pk=article_id).update(up_count=F("up_count")+1)  # 点赞数+1
            else:
                models.Article.objects.filter(pk=article_id).update(down_count=F("down_count") + 1)  # 踩+1
        except Exception as e:
            response["status"] = False
            response["msg"] = models.ArticleUpDown.objects.filter(user=user, article_id=article_id).first().is_up
        return JsonResponse(response)


# 评论
def comment(request):
    pid= request.POST.get("pid")
    article_id = request.POST.get("article_id")
    content = request.POST.get("content")
    user = request.user
    response = {}
    if pid:
        comment_obj = models.Comment.objects.create(article_id=article_id, user=user, content=content, parent_comment_id=pid)
    else:
        comment_obj = models.Comment.objects.create(article_id=article_id, user=user, content=content)  # 根评论的对象及创建
    response["content"] = comment_obj.content
    response["create_time"] = comment_obj.create_time.strftime("%Y-%m-%d %H:%M")  # 将时间的datatime对象转换成字符串再json
    response["username"] = comment_obj.user.username
    return JsonResponse(response)


# 评论树
def comment_tree(request, article_id):
    ret = list(models.Comment.objects.filter(article_id=article_id).values("pk", "content", "parent_comment_id"))
    return JsonResponse(ret, safe=False)  # 发送非字典时需要设置safe=False


# 添加文章，富文本
def add_article(request):
    if request.method == 'POST':

        title = request.POST.get('title')
        article_content = request.POST.get("article_content")
        user = request.user

        from bs4 import BeautifulSoup

        bs = BeautifulSoup(article_content, 'html.parser')
        desc = bs.text[0:150]+"..."  # 得到纯文本的前150个字符作为文章描述
        # 过滤非法字符串，防止xss攻击
        for tag in bs.find_all():
            if tag.name in ["script", "link"]:  # 如果标签名字在
                tag.decompose()  # 删除

        article_obj = models.Article.objects.create(user=user,title=title,desc=desc)  # 创建文章对象，保存
        models.ArticleDetail.objects.create(content=str(bs),article=article_obj)  # 文章详情  str(bs)处理后的bs

        return HttpResponse("ok")
    return render(request, "add_article.html")

from BBS import settings
import os
# 富文本编辑器的图片上传及在输入框里预览
def upload(request):
    obj = request.FILES.get("upload_img")
    add_path = os.path.join(settings.MEDIA_ROOT, "add_article_img", obj.name)
    with open(add_path, 'wb') as f:
        for chunk in obj.chunks():
            f.write(chunk)
    res={  # 图片上传后在输入框预览
        "error":0,
        "url": "/media/add_article_img/"+obj.name,
    }
    return HttpResponse(json.dumps(res))


