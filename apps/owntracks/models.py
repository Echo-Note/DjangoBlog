from django.db import models
from django.utils.timezone import now


# Create your models here.


class OwnTrackLog(models.Model):
    """OwnTracks 客户端上报的轨迹日志。"""

    tid = models.CharField(
        max_length=100, null=False, verbose_name="用户", db_comment="终端/用户标识"
    )
    lat = models.FloatField(verbose_name="纬度", db_comment="纬度坐标")
    lon = models.FloatField(verbose_name="经度", db_comment="经度坐标")
    creation_time = models.DateTimeField(
        "创建时间", default=now, db_comment="记录创建时间"
    )

    def __str__(self) -> str:
        """返回终端/用户标识。"""
        return self.tid

    class Meta:
        ordering = ["creation_time"]
        verbose_name = "OwnTrackLogs"
        verbose_name_plural = verbose_name
        get_latest_by = "creation_time"
