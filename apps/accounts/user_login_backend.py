from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


class EmailOrUsernameModelBackend(ModelBackend):
    """
    允许使用用户名或邮箱登录
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        通过用户名或邮箱进行身份验证

        :param request: HttpRequest对象
        :param username: 用户名或邮箱
        :param password: 密码
        :param kwargs: 其他关键字参数
        :return: 已经身份验证的用户对象，如果身份验证失败则返回None
        """
        if '@' in username:
            kwargs = {'email': username}
        else:
            kwargs = {'username': username}
        try:
            user = get_user_model().objects.get(**kwargs)
            if user.check_password(password):
                return user
            return None
        except get_user_model().DoesNotExist:
            return None

    def get_user(self, username):
        """
        通过ID获取用户对象

        :param username: 用户ID
        :return: 已经身份验证的用户对象，如果身份验证失败则返回None
        """
        try:
            return get_user_model().objects.get(pk=username)
        except get_user_model().DoesNotExist:
            return None
