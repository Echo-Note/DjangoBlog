import logging
import os
import shlex
import subprocess
from typing import List

import openai

from apps.servermanager.models import Commands

logger = logging.getLogger(__name__)

openai.api_key = os.environ.get("OPENAI_API_KEY")
if os.environ.get("HTTP_PROXY"):
    openai.proxy = os.environ.get("HTTP_PROXY")


class ChatGPT:
    """封装 OpenAI ChatCompletion 的简单客户端。"""

    @staticmethod
    def chat(prompt: str) -> str:
        """
        调用 OpenAI ChatCompletion 接口生成回复。

        :param prompt: 输入提示词
        :return: 模型返回的文本内容；如出错则返回通用错误提示
        """
        try:
            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo", messages=[{"role": "user", "content": prompt}]
            )
            return completion.choices[0].message.content
        except Exception as e:
            logger.error(e)
            return "服务器出错了"


class CommandHandler:
    """命令处理器：根据标题查找并执行预设命令。"""

    def __init__(self) -> None:
        """初始化命令集合。"""
        self.commands = Commands.objects.all()

    def run(self, title: str) -> str:
        """运行指定标题的预设命令。

        :param title: 命令标题
        :return: 命令执行结果文本
        """
        cmd = list(filter(lambda x: x.title.upper() == title.upper(), self.commands))
        if cmd:
            return self.__run_command__(cmd[0].command)
        else:
            return "未找到相关命令，请输入hepme获得帮助。"

    def __run_command__(self, cmd: str) -> str:
        """以安全方式执行命令字符串。

        安全策略：
        - 禁用 shell 执行（shell=False），避免命令注入（修复 Bandit B605）。
        - 使用 shlex.split 对命令行进行安全拆分。
        - 拒绝包含管道、重定向等高危字符的命令（如需支持请改为显式参数形式并评估安全）。
        - 设置超时，捕获 stdout/stderr 并返回。

        :param cmd: 数据库中保存的命令字符串
        :return: 执行结果（stdout 与 stderr 合并文本）。
        """
        # 基础字符黑名单（仅当 shell=False 时理论上不会执行这些操作，但提前拒绝能更直观地规避风险）
        forbidden_chars: List[str] = ["|", "&", ";", ">", "<", "`"]
        if any(ch in cmd for ch in forbidden_chars):
            return "命令包含不被允许的特殊字符，已被拒绝执行"

        try:
            args: List[str] = shlex.split(cmd)
        except ValueError:
            return "命令解析失败!"

        if not args:
            return "命令为空，无法执行!"

        try:
            proc = subprocess.run(
                args,
                shell=False,  # 关键：关闭 shell
                capture_output=True,
                text=True,
                timeout=15,
            )
            stdout = proc.stdout or ""
            stderr = proc.stderr or ""
            output = stdout + ("\n" + stderr if stderr else "")
            return output.strip()
        except FileNotFoundError:
            return "命令不可用或未找到可执行文件!"
        except subprocess.TimeoutExpired:
            return "命令执行超时!"
        except Exception:
            return "命令执行出错!"

    def get_help(self) -> str:
        """生成命令帮助信息。"""
        rsp = ""
        for cmd in self.commands:
            rsp += "{c}:{d}\n".format(c=cmd.title, d=cmd.describe)
        return rsp


if __name__ == "__main__":
    chatbot = ChatGPT()
    prompt = "写一篇1000字关于AI的论文"
    print(chatbot.chat(prompt))
