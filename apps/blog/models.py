import logging
import re
from abc import abstractmethod

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from mdeditor.fields import MDTextField
from uuslug import slugify

from djangoblog.utils import cache, cache_decorator, get_current_site

logger = logging.getLogger(__name__)


class LinkShowType(models.TextChoices):
    I = ("i", _("index"))  # noqa: E741
    L = ("l", _("list"))
    P = ("p", _("post"))
    A = ("a", _("all"))
    S = ("s", _("slide"))


class BaseModel(models.Model):
    id = models.AutoField(primary_key=True, db_comment="主键ID")
    creation_time = models.DateTimeField(
        _("creation time"), default=now, db_comment="创建时间"
    )
    last_modify_time = models.DateTimeField(
        _("modify time"), default=now, db_comment="最后修改时间"
    )

    def save(self, *args, **kwargs):
        """重写保存逻辑。

        - 若仅更新浏览量（views），走定制更新路径以避免触发其他变更；
        - 若包含 slug 字段，根据 title 或 name 自动生成 slug；
        - 其余情况按默认保存。
        """
        is_update_views = (
            isinstance(self, Article)
            and "update_fields" in kwargs
            and kwargs["update_fields"] == ["views"]
        )
        if is_update_views:
            Article.objects.filter(pk=self.pk).update(views=self.views)
        else:
            if "slug" in self.__dict__:
                slug = (
                    getattr(self, "title")
                    if "title" in self.__dict__
                    else getattr(self, "name")
                )
                setattr(self, "slug", slugify(slug))
            super().save(*args, **kwargs)

    def get_full_url(self):
        """返回对象可访问的完整 URL（含站点域名）。"""
        site = get_current_site().domain
        url = "https://{site}{path}".format(site=site, path=self.get_absolute_url())
        return url

    class Meta:
        abstract = True

    @abstractmethod
    def get_absolute_url(self):
        pass


class Article(BaseModel):
    """文章模型。

    用于存储博客文章正文、元信息、作者与分类/标签关系等。
    """

    STATUS_CHOICES = (
        ("d", _("Draft")),
        ("p", _("Published")),
    )
    COMMENT_STATUS = (
        ("o", _("Open")),
        ("c", _("Close")),
    )
    TYPE = (
        ("a", _("Article")),
        ("p", _("Page")),
    )
    title = models.CharField(
        _("title"), max_length=200, unique=True, db_comment="文章标题，要求唯一"
    )
    # 摘要
    summary = models.CharField(
        _("summary"),
        max_length=500,
        blank=True,
        null=True,
        db_comment="文章摘要，可为空",
    )
    body = MDTextField(_("body"), db_comment="文章正文（Markdown）")
    pub_time = models.DateTimeField(
        _("publish time"), blank=False, null=False, default=now, db_comment="发布时间"
    )
    status = models.CharField(
        _("status"),
        max_length=1,
        choices=STATUS_CHOICES,
        default="p",
        db_comment="发布状态：d=草稿，p=已发布",
    )
    comment_status = models.CharField(
        _("comment status"),
        max_length=1,
        choices=COMMENT_STATUS,
        default="o",
        db_comment="评论状态：o=开放，c=关闭",
    )
    type = models.CharField(
        _("type"),
        max_length=1,
        choices=TYPE,
        default="a",
        db_comment="类型：a=文章，p=页面",
    )
    views = models.PositiveIntegerField(_("views"), default=0, db_comment="浏览次数")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("author"),
        blank=False,
        null=False,
        on_delete=models.CASCADE,
        db_comment="作者（关联用户）",
    )
    article_order = models.IntegerField(
        _("order"),
        blank=False,
        null=False,
        default=0,
        db_comment="文章排序（数值越大越靠前）",
    )
    show_toc = models.BooleanField(
        _("show toc"),
        blank=False,
        null=False,
        default=False,
        db_comment="是否显示目录（TOC）",
    )
    category = models.ForeignKey(
        "Category",
        verbose_name=_("category"),
        on_delete=models.CASCADE,
        blank=False,
        null=False,
        db_comment="所属分类",
    )
    tags = models.ManyToManyField("Tag", verbose_name=_("tag"), blank=True)

    def body_to_string(self):
        """以字符串形式返回正文。"""
        return self.body

    def __str__(self):
        """返回对象可读名称。"""
        return self.title

    class Meta:
        ordering = ["-article_order", "-pub_time"]
        verbose_name = _("article")
        verbose_name_plural = verbose_name
        get_latest_by = "id"

    def get_absolute_url(self):
        """返回文章详情页的相对 URL。"""
        return reverse(
            "blog:detailbyid",
            kwargs={
                "article_id": self.id,
                "year": self.creation_time.year,
                "month": self.creation_time.month,
                "day": self.creation_time.day,
            },
        )

    @cache_decorator(60 * 60 * 10)
    def get_category_tree(self):
        """获取当前文章的分类树（含父级路径）。"""
        tree = self.category.get_category_tree()
        names = list(map(lambda c: (c.name, c.get_absolute_url()), tree))

        return names

    def save(self, *args, **kwargs):
        """保存文章，继承父类默认行为。"""
        super().save(*args, **kwargs)

    def viewed(self):
        """文章被查看一次，增加浏览量并仅更新该字段。"""
        self.views += 1
        self.save(update_fields=["views"])

    def comment_list(self):
        """获取已启用的评论列表（带缓存）。"""
        cache_key = "article_comments_{id}".format(id=self.id)
        value = cache.get(cache_key)
        if value:
            logger.info("get article comments:{id}".format(id=self.id))
            return value
        else:
            comments = self.comment_set.filter(is_enable=True).order_by("-id")
            cache.set(cache_key, comments, 60 * 100)
            logger.info("set article comments:{id}".format(id=self.id))
            return comments

    def get_admin_url(self):
        """返回该文章在 Django Admin 中的修改页链接。"""
        info = (self._meta.app_label, self._meta.model_name)
        return reverse("admin:%s_%s_change" % info, args=(self.pk,))

    @cache_decorator(expiration=60 * 100)
    def next_article(self):
        """获取下一篇已发布文章。"""
        return Article.objects.filter(id__gt=self.id, status="p").order_by("id").first()

    @cache_decorator(expiration=60 * 100)
    def prev_article(self):
        """获取上一篇已发布文章。"""
        return Article.objects.filter(id__lt=self.id, status="p").first()

    def get_first_image_url(self):
        """从正文中提取第一张图片的 URL，若不存在返回空字符串。"""
        match = re.search(r"!\[.*?\]\((.+?)\)", self.body)
        if match:
            return match.group(1)
        return ""


class Category(BaseModel):
    """文章分类"""

    name = models.CharField(
        _("category name"), max_length=30, unique=True, db_comment="分类名称，要求唯一"
    )
    parent_category = models.ForeignKey(
        "self",
        verbose_name=_("parent category"),
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        db_comment="父级分类",
    )
    slug = models.SlugField(
        default="no-slug",
        max_length=60,
        blank=True,
        db_comment="URL 友好名（自动生成）",
    )
    index = models.IntegerField(
        default=0, verbose_name=_("index"), db_comment="排序权重（越大越靠前）"
    )

    class Meta:
        ordering = ["-index"]
        verbose_name = _("category")
        verbose_name_plural = verbose_name

    def get_absolute_url(self):
        """返回分类详情页的相对 URL。"""
        return reverse("blog:category_detail", kwargs={"category_name": self.slug})

    def __str__(self):
        return self.name

    @cache_decorator(60 * 60 * 10)
    def get_category_tree(self):
        """
        递归获得分类目录的父级
        :return:
        """
        categorys = []

        def parse(category):
            categorys.append(category)
            if category.parent_category:
                parse(category.parent_category)

        parse(self)
        return categorys

    @cache_decorator(60 * 60 * 10)
    def get_sub_categorys(self):
        """
        获得当前分类目录所有子集
        :return:
        """
        categorys = []
        all_categorys = Category.objects.all()

        def parse(category):
            if category not in categorys:
                categorys.append(category)
            childs = all_categorys.filter(parent_category=category)
            for child in childs:
                if category not in categorys:
                    categorys.append(child)
                parse(child)

        parse(self)
        return categorys


class Tag(BaseModel):
    """文章标签"""

    name = models.CharField(
        _("tag name"), max_length=30, unique=True, db_comment="标签名称，要求唯一"
    )
    slug = models.SlugField(
        default="no-slug",
        max_length=60,
        blank=True,
        db_comment="URL 友好名（自动生成）",
    )

    def __str__(self):
        """返回对象可读名称。"""
        return self.name

    def get_absolute_url(self):
        """返回标签详情页的相对 URL。"""
        return reverse("blog:tag_detail", kwargs={"tag_name": self.slug})

    @cache_decorator(60 * 60 * 10)
    def get_article_count(self):
        """获取使用该标签的文章数量。"""
        return Article.objects.filter(tags__name=self.name).distinct().count()

    class Meta:
        ordering = ["name"]
        verbose_name = _("tag")
        verbose_name_plural = verbose_name


class Links(models.Model):
    """友情链接"""

    name = models.CharField(
        _("link name"), max_length=30, unique=True, db_comment="友情链接名称，要求唯一"
    )
    link = models.URLField(_("link"), db_comment="友情链接地址（URL）")
    sequence = models.IntegerField(
        _("order"), unique=True, db_comment="显示顺序，数值越小越靠前"
    )
    is_enable = models.BooleanField(
        _("is show"), default=True, blank=False, null=False, db_comment="是否启用显示"
    )
    show_type = models.CharField(
        _("show type"),
        max_length=1,
        choices=LinkShowType.choices,
        default=LinkShowType.I,
        db_comment="展示位置：i=首页，l=列表页，p=文章页，a=全部，s=幻灯片",
    )
    creation_time = models.DateTimeField(
        _("creation time"), default=now, db_comment="创建时间"
    )
    last_mod_time = models.DateTimeField(
        _("modify time"), default=now, db_comment="最后修改时间"
    )

    class Meta:
        ordering = ["sequence"]
        verbose_name = _("link")
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class SideBar(models.Model):
    """侧边栏,可以展示一些html内容"""

    name = models.CharField(_("title"), max_length=100, db_comment="侧边栏标题")
    content = models.TextField(_("content"), db_comment="侧边栏内容（支持 HTML）")
    sequence = models.IntegerField(
        _("order"), unique=True, db_comment="显示顺序，数值越小越靠前"
    )
    is_enable = models.BooleanField(
        _("is enable"), default=True, db_comment="是否启用显示"
    )
    creation_time = models.DateTimeField(
        _("creation time"), default=now, db_comment="创建时间"
    )
    last_mod_time = models.DateTimeField(
        _("modify time"), default=now, db_comment="最后修改时间"
    )

    class Meta:
        ordering = ["sequence"]
        verbose_name = _("sidebar")
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class BlogSettings(models.Model):
    """blog的配置"""

    site_name = models.CharField(
        _("site name"),
        max_length=200,
        null=False,
        blank=False,
        default="",
        db_comment="站点名称",
    )
    site_description = models.TextField(
        _("site description"),
        max_length=1000,
        null=False,
        blank=False,
        default="",
        db_comment="站点描述",
    )
    site_seo_description = models.TextField(
        _("site seo description"),
        max_length=1000,
        null=False,
        blank=False,
        default="",
        db_comment="SEO 描述",
    )
    site_keywords = models.TextField(
        _("site keywords"),
        max_length=1000,
        null=False,
        blank=False,
        default="",
        db_comment="站点关键词",
    )
    article_sub_length = models.IntegerField(
        _("article sub length"), default=300, db_comment="文章摘要长度（字符数）"
    )
    sidebar_article_count = models.IntegerField(
        _("sidebar article count"), default=10, db_comment="侧边栏文章数量"
    )
    sidebar_comment_count = models.IntegerField(
        _("sidebar comment count"), default=5, db_comment="侧边栏评论数量"
    )
    article_comment_count = models.IntegerField(
        _("article comment count"), default=5, db_comment="文章页评论分页大小"
    )
    show_google_adsense = models.BooleanField(
        _("show adsense"), default=False, db_comment="是否显示 Google AdSense"
    )
    google_adsense_codes = models.TextField(
        _("adsense code"),
        max_length=2000,
        null=True,
        blank=True,
        default="",
        db_comment="AdSense 代码片段",
    )
    open_site_comment = models.BooleanField(
        _("open site comment"), default=True, db_comment="全站是否开启评论"
    )
    global_header = models.TextField(
        "公共头部",
        null=True,
        blank=True,
        default="",
        db_comment="全站公共 HTML 头部代码",
    )
    global_footer = models.TextField(
        "公共尾部",
        null=True,
        blank=True,
        default="",
        db_comment="全站公共 HTML 尾部代码",
    )
    beian_code = models.CharField(
        "备案号",
        max_length=2000,
        null=True,
        blank=True,
        default="",
        db_comment="工信部备案号",
    )
    analytics_code = models.TextField(
        "网站统计代码",
        max_length=1000,
        null=False,
        blank=False,
        default="",
        db_comment="统计/分析代码",
    )
    show_gongan_code = models.BooleanField(
        "是否显示公安备案号",
        default=False,
        null=False,
        db_comment="是否显示公安备案信息",
    )
    gongan_beiancode = models.TextField(
        "公安备案号",
        max_length=2000,
        null=True,
        blank=True,
        default="",
        db_comment="公安备案号",
    )
    comment_need_review = models.BooleanField(
        "评论是否需要审核", default=False, null=False, db_comment="评论是否需要人工审核"
    )

    class Meta:
        verbose_name = _("Website configuration")
        verbose_name_plural = verbose_name

    def __str__(self):
        """返回配置名称。"""
        return self.site_name

    def clean(self):
        """限制全站仅存在一条配置记录。"""
        if BlogSettings.objects.exclude(id=self.id).count():
            raise ValidationError(_("There can only be one configuration"))

    def save(self, *args, **kwargs):
        """保存后清理站点缓存。"""
        super().save(*args, **kwargs)
        from djangoblog.utils import cache

        cache.clear()
