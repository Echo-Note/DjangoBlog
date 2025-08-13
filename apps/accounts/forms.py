from django import forms
from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.exceptions import ValidationError
from django.forms import widgets
from django.utils.translation import gettext_lazy as _

from . import utils
from .models import BlogUser


class LoginForm(AuthenticationForm):

    def __init__(self, *args, **kwargs):
        """
        设置username和password字段的占位符和类。

        在创建类的实例时调用此方法。

        参数:
        * args: 传递给方法的位置参数。
        ** kwargs: 传递给方法的关键字参数。
        """
        super(LoginForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget = widgets.TextInput(
            attrs={'placeholder': "username", "class": "form-control"}
        )
        self.fields['password'].widget = widgets.PasswordInput(
            attrs={'placeholder': "password", "class": "form-control"}
        )


class RegisterForm(UserCreationForm):

    def __init__(self, *args, **kwargs):
        """
        初始化RegisterForm。

        此方法为username、email、password1和password2设置表单字段
        使用自定义小部件，包括占位符和CSS类的样式。

        参数:
        * args: 传递给父类的位置参数。
        ** kwargs: 传递给父类的关键字参数。
        """
        super(RegisterForm, self).__init__(*args, **kwargs)

        self.fields['username'].widget = widgets.TextInput(
            attrs={'placeholder': "username", "class": "form-control"}
        )
        self.fields['email'].widget = widgets.EmailInput(
            attrs={'placeholder': "email", "class": "form-control"}
        )
        self.fields['password1'].widget = widgets.PasswordInput(
            attrs={'placeholder': "password", "class": "form-control"}
        )
        self.fields['password2'].widget = widgets.PasswordInput(
            attrs={'placeholder': "repeat password", "class": "form-control"}
        )

    def clean_email(self):
        """
        验证email是否已经存在。

        email字段的自定义清理方法。

        检查email是否已经存在于数据库中，如果存在，引发ValidationError。
        """
        email = self.cleaned_data['email']
        if get_user_model().objects.filter(email=email).exists():
            raise ValidationError(_("email already exists"))
        return email

    class Meta:
        model = get_user_model()
        fields = ("username", "email")


class ForgetPasswordForm(forms.Form):
    new_password1 = forms.CharField(
        label=_("New password"),
        widget=forms.PasswordInput(
            attrs={
                "class":       "form-control",
                'placeholder': _("New password")
            }
        ),
    )

    new_password2 = forms.CharField(
        label="确认密码",
        widget=forms.PasswordInput(
            attrs={
                "class":       "form-control",
                'placeholder': _("Confirm password")
            }
        ),
    )

    email = forms.EmailField(
        label='邮箱',
        widget=forms.TextInput(
            attrs={
                'class':       'form-control',
                'placeholder': _("Email")
            }
        ),
    )

    code = forms.CharField(
        label=_('Code'),
        widget=forms.TextInput(
            attrs={
                'class':       'form-control',
                'placeholder': _("Code")
            }
        ),
    )

    def clean_new_password2(self):
        """
        验证new_password2是否和new_password1相同，如果不同引发ValidationError。

        在form.is_valid()时调用此方法。

        也会调用password_validation.validate_password()来验证密码的合法性。
        """
        password1 = self.data.get("new_password1")
        password2 = self.data.get("new_password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError(_("passwords do not match"))
        password_validation.validate_password(password2)

        return password2

    def clean_email(self):
        """
        验证电子邮件是否存在于数据库中。

        此方法从清理的数据中检索电子邮件，并检查它是否存在
        在BlogUser模型中。如果电子邮件不存在，则会引发ValidationError。
        这可用于验证电子邮件是否已注册，并且错误消息可以
        如果您不想公开此信息，请修改。

        退货:
        已验证的电子邮件 (如果存在)。

        加注:
        ValidationError: 如果电子邮件在数据库中不存在。
        """
        user_email = self.cleaned_data.get("email")
        if not BlogUser.objects.filter(
            email=user_email
        ).exists():
            # todo 这里的报错提示可以判断一个邮箱是不是注册过，如果不想暴露可以修改
            raise ValidationError(_("email does not exist"))
        return user_email

    def clean_code(self):
        """
        验证验证码是否正确。

        在form.is_valid()时调用此方法。

        params:
            code: 验证码
            email: 电子邮件

        returns:
        如果验证码正确，返回验证码。

        variables:
        ValidationError: 验证码不正确。
        """
        code = self.cleaned_data.get("code")
        error = utils.verify(
            email=self.cleaned_data.get("email"),
            code=code,
        )
        if error:
            raise ValidationError(error)
        return code


class ForgetPasswordCodeForm(forms.Form):
    email = forms.EmailField(
        label=_('Email'),
    )
