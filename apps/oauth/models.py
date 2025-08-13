# Create your models here.
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _


class OAuthUser(models.Model):
    """第三方登录用户信息。"""

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("author"),
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        db_comment="关联站内用户（可为空）",
    )
    openid = models.CharField(max_length=50, db_comment="第三方平台用户唯一标识 openid")
    nickname = models.CharField(
        max_length=50, verbose_name=_("nick name"), db_comment="第三方昵称"
    )
    token = models.CharField(
        max_length=150, null=True, blank=True, db_comment="访问令牌/刷新令牌等信息"
    )
    picture = models.CharField(
        max_length=350, blank=True, null=True, db_comment="头像 URL"
    )
    type = models.CharField(
        blank=False,
        null=False,
        max_length=50,
        db_comment="第三方平台类型，如 github/google/qq 等",
    )
    email = models.CharField(
        max_length=50, null=True, blank=True, db_comment="邮箱（可能由第三方返回）"
    )
    metadata = models.TextField(
        null=True, blank=True, db_comment="第三方原始数据（JSON/文本）"
    )
    creation_time = models.DateTimeField(
        _("creation time"), default=now, db_comment="创建时间"
    )
    last_modify_time = models.DateTimeField(
        _("last modify time"), default=now, db_comment="最后修改时间"
    )

    def __str__(self) -> str:
        """返回用户昵称。"""
        return self.nickname

    class Meta:
        verbose_name = _("oauth user")
        verbose_name_plural = verbose_name
        ordering = ["-creation_time"]


class OAuthConfig(models.Model):
    """第三方登录平台配置。"""

    TYPE = (
        ("weibo", _("weibo")),
        ("google", _("google")),
        ("github", "GitHub"),
        ("facebook", "FaceBook"),
        ("qq", "QQ"),
    )
    type = models.CharField(
        _("type"),
        max_length=10,
        choices=TYPE,
        default="a",
        db_comment="配置类型（平台标识）",
    )
    appkey = models.CharField(
        max_length=200, verbose_name="AppKey", db_comment="第三方平台 AppKey/ClientID"
    )
    appsecret = models.CharField(
        max_length=200,
        verbose_name="AppSecret",
        db_comment="第三方平台 AppSecret/ClientSecret",
    )
    callback_url = models.CharField(
        max_length=200,
        verbose_name=_("callback url"),
        blank=False,
        default="",
        db_comment="回调地址",
    )
    is_enable = models.BooleanField(
        _("is enable"),
        default=True,
        blank=False,
        null=False,
        db_comment="是否启用该平台登录",
    )
    creation_time = models.DateTimeField(
        _("creation time"), default=now, db_comment="创建时间"
    )
    last_modify_time = models.DateTimeField(
        _("last modify time"), default=now, db_comment="最后修改时间"
    )

    def clean(self) -> None:
        """限制相同类型的配置只能存在一条。"""
        if OAuthConfig.objects.filter(type=self.type).exclude(id=self.id).count():
            raise ValidationError(_(self.type + _("already exists")))

    def __str__(self) -> str:
        """返回配置类型标识。"""
        return self.type

    class Meta:
        verbose_name = "oauth配置"
        verbose_name_plural = verbose_name
        ordering = ["-creation_time"]
