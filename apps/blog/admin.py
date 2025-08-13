from django import forms
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

# Register your models here.
from .models import Article


class ArticleForm(forms.ModelForm):
    """
    文章表单类，用于在Django Admin中管理文章内容。
    当前未启用AdminPagedownWidget富文本编辑器。
    """

    # body = forms.CharField(widget=AdminPagedownWidget())  # 注释掉的富文本编辑器配置

    class Meta:
        """
        元类配置：
        - model: 绑定的模型类Article
        - fields: 包含所有字段
        """

        model = Article
        fields = "__all__"


def makr_article_publish(modeladmin, request, queryset):
    """
    将选中的文章状态批量更新为已发布。

    参数:
        modeladmin (ModelAdmin): 管理界面实例
        request (HttpRequest): 当前请求对象
        queryset (QuerySet): 被选中的文章集合
    """
    queryset.update(status="p")


def draft_article(modeladmin, request, queryset):
    """
    将选中的文章状态批量更新为草稿。

    参数:
        modeladmin (ModelAdmin): 管理界面实例
        request (HttpRequest): 当前请求对象
        queryset (QuerySet): 被选中的文章集合
    """
    queryset.update(status="d")


def close_article_commentstatus(modeladmin, request, queryset):
    """
    关闭选中文章的评论功能。

    参数:
        modeladmin (ModelAdmin): 管理界面实例
        request (HttpRequest): 当前请求对象
        queryset (QuerySet): 被选中的文章集合
    """
    queryset.update(comment_status="c")


def open_article_commentstatus(modeladmin, request, queryset):
    """
    开启选中文章的评论功能。

    参数:
        modeladmin (ModelAdmin): 管理界面实例
        request (HttpRequest): 当前请求对象
        queryset (QuerySet): 被选中的文章集合
    """
    queryset.update(comment_status="o")


makr_article_publish.short_description = _("Publish selected articles")
draft_article.short_description = _("Draft selected articles")
close_article_commentstatus.short_description = _("Close article comments")
open_article_commentstatus.short_description = _("Open article comments")


class ArticlelAdmin(admin.ModelAdmin):
    """
    文章管理类，配置Django Admin界面的展示和交互逻辑。

    属性：
        list_per_page (int): 每页显示20条记录
        search_fields (tuple): 可搜索字段（正文、标题）
        list_display (tuple): 列表页展示字段
        list_filter (tuple): 可过滤字段
        filter_horizontal (tuple): 水平筛选的多对多字段
        exclude (tuple): 排除自动显示的字段
        view_on_site (bool): 是否显示“在站点查看”按钮
        actions (list): 可用的批量操作
    """

    list_per_page = 20
    search_fields = ("body", "title")
    form = ArticleForm
    list_display = (
        "id",
        "title",
        "author",
        "link_to_category",
        "creation_time",
        "views",
        "status",
        "type",
        "article_order",
    )
    list_display_links = ("id", "title")
    list_filter = ("status", "type", "category")
    filter_horizontal = ("tags",)
    exclude = ("creation_time", "last_modify_time")
    view_on_site = True
    actions = [
        makr_article_publish,
        draft_article,
        close_article_commentstatus,
        open_article_commentstatus,
    ]
    readonly_fields = ("views", "creation_time", "last_modify_time")

    def link_to_category(self, obj):
        """
        生成指向分类编辑页面的超链接。

        参数：
            obj (Article): 当前文章对象

        返回：
            str: 格式化后的HTML链接
        """
        info = (obj.category._meta.app_label, obj.category._meta.model_name)
        link = reverse("admin:%s_%s_change" % info, args=(obj.category.id,))
        return format_html('<a href="%s">%s</a>' % (link, obj.category.name))

    link_to_category.short_description = _("category")  # 列表页列标题显示

    def get_form(self, request, obj=None, **kwargs):
        """
        获取表单实例并限制作者选择范围，设置默认作者为当前登录用户。

        参数：
            request (HttpRequest): 当前请求对象
            obj (Article, optional): 当前编辑的文章对象

        返回：
            ModelForm: 过滤后的表单实例
        """
        form = super(ArticlelAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields["author"].queryset = get_user_model().objects.filter(
            is_superuser=True
        )
        # 设置默认作者为当前登录用户
        if not obj:  # 只在创建新文章时设置默认值
            form.base_fields["author"].initial = request.user
        return form

    def save_model(self, request, obj, form, change):
        """
        保存模型时的额外处理，确保新文章的作者为当前登录用户。

        参数：
            request (HttpRequest): 当前请求对象
            obj (Article): 要保存的文章对象
            form (ModelForm): 当前使用的表单
            change (bool): 是否为修改操作
        """
        # 如果是新建文章且没有设置作者，则设置为当前登录用户
        if not change and not obj.author:
            obj.author = request.user
        super(ArticlelAdmin, self).save_model(request, obj, form, change)

    def get_view_on_site_url(self, obj=None):
        """
        获取文章在站点的访问URL。

        参数：
            obj (Article, optional): 当前文章对象

        返回：
            str: 文章的完整URL或站点域名
        """
        if obj:
            url = obj.get_full_url()
            return url
        else:
            from djangoblog.utils import get_current_site

            site = get_current_site().domain
            return site


class TagAdmin(admin.ModelAdmin):
    """
    标签管理类，排除自动生成的字段。

    排除字段：
        - slug: 自动生成的URL别名
        - last_modify_time: 最后修改时间
        - creation_time: 创建时间
    """

    exclude = ("slug", "last_modify_time", "creation_time")


class CategoryAdmin(admin.ModelAdmin):
    """
    分类管理类，配置列表展示和字段排除。

    列表展示：
        - name: 分类名称
        - parent_category: 父分类
        - index: 排序索引

    排除字段：
        - slug: 自动生成的URL别名
        - last_modify_time: 最后修改时间
        - creation_time: 创建时间
    """

    list_display = ("name", "parent_category", "index")
    exclude = ("slug", "last_modify_time", "creation_time")


class LinksAdmin(admin.ModelAdmin):
    """
    友情链接管理类，排除自动生成的时间字段。

    排除字段：
        - last_mod_time: 最后修改时间
        - creation_time: 创建时间
    """

    exclude = ("last_mod_time", "creation_time")


class SideBarAdmin(admin.ModelAdmin):
    """
    侧边栏管理类，配置列表展示和字段排除。

    列表展示：
        - name: 侧边栏名称
        - content: 内容
        - is_enable: 是否启用
        - sequence: 排序序号

    排除字段：
        - last_mod_time: 最后修改时间
        - creation_time: 创建时间
    """

    list_display = ("name", "content", "is_enable", "sequence")
    exclude = ("last_mod_time", "creation_time")


class BlogSettingsAdmin(admin.ModelAdmin):
    """
    博客设置管理类，暂无特殊配置。
    """

    pass
