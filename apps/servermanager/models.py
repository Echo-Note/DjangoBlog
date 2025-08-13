from django.db import models


# Create your models here.
class commands(models.Model):
    """服务器命令模板。"""

    title = models.CharField("命令标题", max_length=300, db_comment="命令的简短标题")
    command = models.CharField("命令", max_length=2000, db_comment="命令内容/脚本")
    describe = models.CharField(
        "命令描述", max_length=300, db_comment="命令用途或备注说明"
    )
    creation_time = models.DateTimeField(
        "创建时间", auto_now_add=True, db_comment="创建时间"
    )
    last_modify_time = models.DateTimeField(
        "修改时间", auto_now=True, db_comment="最后修改时间"
    )

    def __str__(self) -> str:
        """返回命令标题。"""
        return self.title

    class Meta:
        verbose_name = "命令"
        verbose_name_plural = verbose_name


class EmailSendLog(models.Model):
    """邮件发送日志。"""

    emailto = models.CharField(
        "收件人", max_length=300, db_comment="收件人邮箱（可多邮箱分隔）"
    )
    title = models.CharField("邮件标题", max_length=2000, db_comment="邮件标题")
    content = models.TextField("邮件内容", db_comment="邮件内容正文")
    send_result = models.BooleanField(
        "结果", default=False, db_comment="发送结果：True=成功，False=失败"
    )
    creation_time = models.DateTimeField(
        "创建时间", auto_now_add=True, db_comment="创建时间"
    )

    def __str__(self) -> str:
        return self.title

    class Meta:
        verbose_name = "邮件发送log"
        verbose_name_plural = verbose_name
        ordering = ["-creation_time"]
