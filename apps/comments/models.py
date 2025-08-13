from django.conf import settings
from django.db import models
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

from apps.blog.models import Article

# Create your models here.


class Comment(models.Model):
    """文章评论。"""

    body = models.TextField("正文", max_length=300, db_comment="评论正文，最多300字符")
    creation_time = models.DateTimeField(
        _("creation time"), default=now, db_comment="创建时间"
    )
    last_modify_time = models.DateTimeField(
        _("last modify time"), default=now, db_comment="最后修改时间"
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("author"),
        on_delete=models.CASCADE,
        db_comment="评论作者",
    )
    article = models.ForeignKey(
        Article,
        verbose_name=_("article"),
        on_delete=models.CASCADE,
        db_comment="所属文章",
    )
    parent_comment = models.ForeignKey(
        "self",
        verbose_name=_("parent comment"),
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        db_comment="父级评论（用于楼中楼）",
    )
    is_enable = models.BooleanField(
        _("enable"),
        default=False,
        blank=False,
        null=False,
        db_comment="是否已启用/审核通过",
    )

    class Meta:
        ordering = ["-id"]
        verbose_name = _("comment")
        verbose_name_plural = verbose_name
        get_latest_by = "id"

    def __str__(self) -> str:
        """返回评论正文作为显示名称。"""
        return self.body
