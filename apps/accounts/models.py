from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

from djangoblog.utils import get_current_site

# Create your models here.


class BlogUser(AbstractUser):
    """站内用户模型，继承自 Django AbstractUser。"""

    nickname = models.CharField(
        _("nick name"), max_length=100, blank=True, db_comment="用户昵称，可为空"
    )
    creation_time = models.DateTimeField(
        _("creation time"), default=now, db_comment="创建时间"
    )
    last_modify_time = models.DateTimeField(
        _("last modify time"), default=now, db_comment="最后修改时间"
    )
    source = models.CharField(
        _("create source"),
        max_length=100,
        blank=True,
        db_comment="用户创建来源，如注册/导入/第三方绑定",
    )

    def get_absolute_url(self) -> str:
        """获取用户详细信息视图的url。"""
        return reverse("blog:author_detail", kwargs={"author_name": self.username})

    def __str__(self) -> str:
        """返回邮箱作为显示名称。"""
        return self.email

    def get_full_url(self) -> str:
        """
        获取用户详细信息页面的完整URL。

        :return: URL字符串。
        """
        site = get_current_site().domain
        url = "https://{site}{path}".format(site=site, path=self.get_absolute_url())
        return url

    class Meta:
        ordering = ["-id"]
        verbose_name = _("user")
        verbose_name_plural = verbose_name
        get_latest_by = "id"
