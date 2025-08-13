from django import forms
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UsernameField
from django.utils.translation import gettext_lazy as _
from django.contrib import admin

from djangoblog.admin_site import admin_site

# Register your models here.
from .models import BlogUser


class BlogUserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label=_("password"), widget=forms.PasswordInput)
    password2 = forms.CharField(
        label=_("Enter password again"), widget=forms.PasswordInput
    )

    class Meta:
        model = BlogUser
        fields = ("email",)

    def clean_password2(self):
        """
        验证输入到两个密码字段中的值是否匹配。
        请注意，仅当两个字段不为空时才会引发错误。
        如果任一字段为空，则验证成功。
        """
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(_("passwords do not match"))
        return password2

    def save(self, commit=True):
        """
        保存用户对象，使用提供的password1的值设置raw_password。
        如果commit=True，则将更改保存到数据库。
        """
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.source = "adminsite"
            user.save()
        return user


class BlogUserChangeForm(UserChangeForm):
    class Meta:
        """
        指定模型和字段
        """

        model = BlogUser
        fields = "__all__"
        field_classes = {"username": UsernameField}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


@admin.register(BlogUser, site=admin_site)
class BlogUserAdmin(UserAdmin):
    form = BlogUserChangeForm
    add_form = BlogUserCreationForm
    list_display = (
        "id",
        "nickname",
        "username",
        "email",
        "last_login",
        "date_joined",
        "source",
    )
    list_display_links = ("id", "username")
    ordering = ("-id",)
