# -*- coding: utf-8 -*-  # pylint: disable=too-many-lines

# SPDX-FileCopyrightText: 2023 UnionTech Software Technology Co., Ltd.

from youqu3.cmd import Cmd
from config import config
from youqu3 import setting
from youqu3 import logger
from youqu3 import log
from youqu3 import sleep
from youqu3.gui import pylinuxauto
from functools import wraps

from youqu3 import log
from youqu3 import logger
from youqu3 import setting
from youqu3 import sleep
from youqu3.exceptions import ApplicationError
from youqu3.exceptions import ApplicationStartError
from youqu3.exceptions import TemplateElementNotFound

# SPDX-License-Identifier: GPL-2.0-only
from youqu3.gui import pylinuxauto

APPS = {
    "文件管理器": {"package": "dde-file-manager", "dock_btn": "Btn_文件管理器"},
    "音乐": {"package": "deepin-music", "dock_btn": "Btn_音乐"},
    "影院": {"package": "deepin-movie", "dock_btn": "Btn_影院"},
    "相册": {"package": "deepin-album", "dock_btn": "Btn_相册"},
    "画板": {"package": "deepin-draw", "dock_btn": "Btn_画板"},
    "看图": {"package": "deepin-image-viewer", "dock_btn": "Btn_看图"},
    "截图录屏": {
        "package": "deepin-screen-recorder",
        "dock_btn": "Btn_截图录屏",
    },
    "相机": {"package": "deepin-camera", "dock_btn": "Btn_相机"},
    "控制中心": {"package": "dde-control-center", "dock_btn": "Btn_控制中心"},
    "文本编辑器": {"package": "deepin-editor", "dock_btn": "Btn_文本编辑器"},
    "全局搜索": {
        "package": "dde-grand-search-daemon",
        "dock_btn": "Btn_grand-search",
    },
    "浏览器": {"package": "org.deepin.browser", "dock_btn": "Btn_浏览器"},
    "日历": {"package": "dde-calendar", "dock_btn": "Btn_日历"},
    "应用商店": {
        "ui": "deepin-home-appstore-client",
        "package": "deepin-app-store",
        "dock_btn": "Btn_应用商店",
    },
    "日志收集工具": {"package": "deepin-log-viewer", "dock_btn": "Btn_日志收集工具"},
    "帮助手册": {"ui": "dman", "package": "deepin-manual", "dock_btn": "Btn_帮助手册"},
    "字体管理器": {"package": "deepin-font-manager", "dock_btn": "Btn_字体管理器"},
    "归档管理器": {"package": "deepin-compressor", "dock_btn": "Btn_归档管理器"},
    "文档查看器": {"package": "deepin-reader", "dock_btn": "Btn_文档查看器"},
    "系统监视器": {"package": "deepin-system-monitor", "dock_btn": "Btn_系统监视器"},
    "终端": {"package": "deepin-terminal", "dock_btn": "Btn_终端"},
    "计算器": {"package": "deepin-calculator", "dock_btn": "Btn_计算器"},
    "启动盘制作工具": {
        "package": "deepin-boot-maker",
        "dock_btn": "Btn_启动盘制作工具",
    },
    "软件包安装器": {"package": "deepin-deb-installer", "dock_btn": "Btn_软件包安装器"},
    "语音记事本": {"package": "deepin-voice-note", "dock_btn": "Btn_语音记事本"},
    "设备管理器": {"package": "deepin-devicemanager", "dock_btn": "Btn_设备管理器"},
    "安全中心": {"package": "deepin-defender", "dock_btn": "Btn_安全中心"},
    "服务与支持": {"package": "uos-service-support", "dock_btn": "Btn_服务与支持"},
    "连连看": {"package": "deepin-lianliankan", "dock_btn": "Btn_连连看"},
    "五子棋": {"package": "deepin-gomoku", "dock_btn": "Btn_五子棋"},
    "磁盘管理器": {"package": "deepin-diskmanager", "dock_btn": "Btn_磁盘管理器"},
    "下载器": {"package": "downloader", "dock_btn": "Btn_下载器"},
    "桌面智能助手": {"package": "DeepinAIAssistant"},
}


# 检查应用是否配置
def check_application_config(func):
    """check_application_config"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            application = args[1]
        except IndexError:
            application = kwargs.get("application")
        # pylint: disable=consider-iterating-dictionary
        if application not in APPS.keys():
            logger.error("应用不存在或未加入配置")
        else:
            func(*args, **kwargs)

    return wrapper


# 检查应用是否开启状态
def check_process_function(func):
    """check_process_function"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            application = args[1]
        except IndexError:
            application = kwargs.get("application")
        # 文管进程监控与其他多媒体区别
        if application == "dde-file-manager":
            status = Cmd.monitor_process(APPS[application]["package"])
        else:
            status = Cmd.get_process_status(APPS[application]["package"])

        if status:
            func(*args, **kwargs)
        else:
            raise ApplicationError("应用程序未启动,无法进行此操作")

    return wrapper


# 检查应用是否关闭状态
def check_process_close(func):
    """check_process_close"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            application = args[1]
        except IndexError:
            application = kwargs.get("application")
        # 文管进程监控与其他多媒体区别
        if application == "dde-file-manager":
            status = Cmd.monitor_process(APPS[application]["package"])
        else:
            status = Cmd.get_process_status(APPS[application]["package"])

        if not status:
            func(*args, **kwargs)
        else:
            raise ApplicationError("应用程序已启动，无法进行此操作")

    return wrapper


class BaseMethod:
    """BaseMethod"""

    APP_NAME = "dde-dock"
    DESC = "/usr/bin/dde-dock"

    def __init__(self, check_start=True):
        kwargs = {}
        kwargs["name"] = "dde-dock"
        kwargs["description"] = "/usr/bin/dde-dock"
        kwargs["check_start"] = check_start
        kwargs["config_path"] = config.UI_INI_PATH

    @classmethod
    def find_dock_image(cls, *elements, rate=0.9):
        """
         通过图片查找任务栏元素坐标
        :param elements:
        :return:
        """
        element = tuple(map(lambda x: f"{config.PIC_RES_PATH}/{x}", elements))
        return pylinuxauto.find_element_by_image(*element, rate=rate).center().center()

    def send_link_to_dock(self, application):
        """
         发送快捷方式到任务栏
        :param application:
        :return:
        """
        btn = APPS[application]["dock_btn"]
        if not pylinuxauto.find_element_by_attr_path("Form_mainwindow").isChild(btn):
            cmd = (
                "dbus-send --session --print-reply "
                "--dest=com.deepin.dde.daemon.Dock /com/deepin/dde/daemon/"
                "Dock com.deepin.dde.daemon.Dock.RequestDock string:/usr/share/applications/"
                f"{APPS[application]['package']}.desktop int32:0"
            )
            Cmd.run(cmd, interrupt=False, timeout=5, print_log=False, command_log=False)
            sleep(1)
        logger.debug(f"发送<{application}>快捷方式到任务栏")

    @check_application_config
    # @check_process_close
    def click_and_focus_application_in_dock_by_attr(self, application: str):
        """
         在dock启动应用
        :param application: 应用名
        :return:
        """
        # 如果任务栏没有文管，则将文管发送到任务栏
        self.click_application_in_dock_by_attr(application)
        sleep(3)
        # 磁盘管理器比较特殊，启动时会弹用户密码输入框，在 x11 上此时是拿不到 app_id 的
        # 故不进入 focus_windows 流程
        if application == "磁盘管理器":
            pylinuxauto.input_message(config.PASSWORD)
            pylinuxauto.press_key("enter")
            sleep(1)
            return
        self.ui.focus_windows(
            APPS[application]["ui"]
            if APPS[application].get("ui")
            else APPS[application]["package"]
        )

    @check_application_config
    def close_app(self, application: str):
        """
         关闭应用：{{application}}
        :param application: 应用名
        """
        package = APPS[application]["package"]
        self.kill_process(package)
        # if package == "dde-file-manager":
        #     Cmd.run(f"echo '{setting.PASSWORD}' | "
        #                  "sudo -S kill -9 `pidof dde-file-manager`",
        #                  interrupt=False,
        #                  print_log=False,
        #                  command_log=False
        #                  )
        #     Cmd.run(f"echo '{setting.PASSWORD}' | "
        #                  "sudo -S kill -9 `pidof dde-dconfig-daemon`",
        #                  interrupt=False,
        #                  print_log=False,
        #                  command_log=False)
        #     Cmd.run(
        #         (
        #             f"echo '{setting.PASSWORD}' | sudo -S rm "
        #             "~/.config/dsg/configs/org.deepin.dde.file-manager/"
        #             "org.deepin.dde.file-manager.json"
        #         ),
        #         interrupt=False)
        #     # 临时解决文管隐藏最近使用的Bug
        #     Cmd.run(
        #         "dde-dconfig --set -a org.deepin.dde.file-manager -r "
        #         "org.deepin.dde.file-manager -k dfm.recent.hidden -v false"
        #     )
        #
        # 删除窗口大小配置文件
        Cmd.run(
            f"rm -rf /home/{setting.USERNAME}/.config/deepin/{package}/{package}*",
            command_log=False,
        )
        # 删除书签配置文件
        Cmd.run(
            f"rm -f /home/{setting.USERNAME}/.config/deepin/{package}.json",
            command_log=False,
        )

    @check_application_config
    def click_application_in_dock_by_attr(self, application: str):
        """
         点击 dock 栏应用图标
        :param application: 应用名
        """
        btn = APPS[application]["dock_btn"]
        self.send_link_to_dock(application)
        pylinuxauto.find_element_by_attr_path(btn).click()
        logger.debug(f"在任务栏点击 <{btn}> 按钮")
        sleep(2)

    @check_application_config
    def right_click_application_in_dock_by_attr(self, application: str):
        """
         右键 dock 栏应用图标
        :param application: 应用名
        """
        btn = APPS[application]["dock_btn"]
        self.send_link_to_dock(application)
        pylinuxauto.find_element_by_attr_path(btn, button=3).click()
        logger.debug(f"在任务栏右键 <{btn}> 按钮")
        sleep(2)

    @check_application_config
    def double_click_application_in_dock_by_attr(self, application: str):
        """
         双击 dock 栏应用图标
        :param application: 应用名
        """
        btn = APPS[application]["dock_btn"]
        self.send_link_to_dock(application)
        self.dog.element_double_click(btn)
        logger.debug(f"在任务栏双击 <{btn}> 按钮")
        sleep(2)

    @check_application_config
    @check_process_function
    def right_click_all_windows_in_dock_by_attr(self, application: str):
        """
         任务栏右键“所有窗口“
        :param application: 应用名
        :return:
        """
        self.send_link_to_dock(application)
        self.right_click_application_in_dock_by_attr(application)
        pylinuxauto.reverse_select_menu(4)
        sleep(0.5)

    @check_application_config
    def right_click_move_in_dock_by_attr(self, application: str):
        """
         任务栏右键“移除驻留”
        :param application: 应用名
        :return:
        """
        self.send_link_to_dock(application)
        package = APPS[application]["package"]
        if application == "dde-file-manager":
            status = Cmd.monitor_process(package)
        else:
            status = Cmd.get_process_status(package)
        self.right_click_application_in_dock_by_attr(application)
        pylinuxauto.reverse_select_menu(3 if status else 1)
        sleep(0.5)

    @check_application_config
    @check_process_function
    def right_forced_close_in_dock_by_attr(self, application: str):
        """
         任务栏右键“强制退出”
        :param application: 应用名
        :return:
        """
        self.send_link_to_dock(application)
        self.right_click_application_in_dock_by_attr(application)
        pylinuxauto.reverse_select_menu(2)
        sleep(0.5)

    @check_application_config
    @check_process_function
    def right_click_close_all_in_dock_by_attr(self, application: str):
        """
         任务栏右键“关闭所有”
        :param application: 应用名
        :return:
        """
        self.send_link_to_dock(application)
        self.right_click_application_in_dock_by_attr(application)
        pylinuxauto.reverse_select_menu(1)
        sleep(0.5)

    @check_application_config
    @check_process_close
    def right_click_open_in_dock_by_attr(self, application: str):
        """
         任务栏右键“打开”
        :param application: 应用名
        :return:
        """
        self.send_link_to_dock(application)
        self.right_click_application_in_dock_by_attr(application)
        pylinuxauto.reverse_select_menu(2)
        sleep(0.5)

    @check_application_config
    @check_process_function
    def right_click_open_new_windows_in_dock_by_attr(self, application):
        """
         任务栏右键“新建窗口“
        :param application: 应用名
        :return:
        """
        self.send_link_to_dock(application)
        self.right_click_application_in_dock_by_attr(application)
        pylinuxauto.select_menu(2)
        logger.info("任务栏右键“新建窗口“")
        sleep(0.5)

    def right_click_element_in_dock_by_attr(self, btn):
        """在dock上右键某个元素"""
        pylinuxauto.find_element_by_attr_path(btn, button=3).click()

    def click_element_in_dock_by_attr(self, btn):
        """在dock上右键某个元素"""
        pylinuxauto.find_element_by_attr_path(btn).click()


@log
class DdeDockPublicMethod(BaseMethod):
    """文管对应的dock栏操作"""

    def send_defender_to_dock_by_cmd(self):
        """
         发送安全中心到任务栏
        :return:
        """
        self.send_link_to_dock("安全中心")

    def click_defender_btn_in_dock_by_attr(self):
        """
         点击任务栏图标启动看图
        :return:
        """
        self.click_application_in_dock_by_attr("安全中心")

    # =============================dock栏 看图操作=======================================
    def open_image_viewer_in_dock_by_attr(self):
        """
         点击任务栏图标启动看图
        :return:
        """
        self.click_and_focus_application_in_dock_by_attr("看图")

    def send_image_viewer_to_dock_by_cmd(self):
        """
         发送看图到任务栏
        :return:
        """
        self.send_link_to_dock("看图")

    def click_image_viewer_btn_in_dock_by_attr(self):
        """
         点击任务栏图标启动看图
        :return:
        """
        self.click_application_in_dock_by_attr("看图")

    def right_click_image_viewer_btn_in_dock_by_attr(self):
        """
         右键点击任务栏图标启动看图
        :return:
        """
        self.right_click_application_in_dock_by_attr("看图")

    def close_image_viewer_by_cmd(self):
        """
         关闭看图并清理数据
        :return:
        """
        self.close_app("看图")
        sleep(0.5)

    def get_deepin_image_viewer_location(self):
        """
         返回dock栏的看图图标坐标
        :return:
        """
        # return self.find_system_desktop_image("deepin_image_viewer")
        return self.dog.element_center("Btn_看图")

    # =============================dock栏 桌面智能助手操作=======================================

    def click_ai_assistant_in_dock_by_attr(self):
        """
        点击任务栏图标启动桌面智能助手
        :return:
        """
        pylinuxauto.find_element_by_attr_path("Form_mainwindow").child(
            "Btn_mainpanelcontrol"
        ).child("Btn_aiassistant").click()
        sleep(1)

    def right_click_ai_assistant_in_dock_by_attr(self):
        """
        点击任务栏图标启动桌面智能助手
        :return:
        """
        pylinuxauto.find_element_by_attr_path("Form_mainwindow").child(
            "Btn_mainpanelcontrol"
        ).child("Btn_aiassistant").click(3)
        sleep(1)

    def click_ai_assistant_settings_in_dock_by_attr(self):
        """
        点击任务栏图标启动桌面智能助手
        :return:
        """
        self.right_click_ai_assistant_in_dock_by_attr()
        sleep(1)
        try:
            pylinuxauto.click(*pylinuxauto.find_element_by_ocr("助手设置").center())
        except TypeError:
            pass
        sleep(3)

    def close_ai_assistant_by_cmd(self):
        """
        关闭桌面智能助手并清理数据
        :return:
        """
        self.close_app("桌面智能助手")
        sleep(0.5)

    # =============================dock栏 磁盘管理器操作=======================================

    def open_diskmanager_in_dock_by_attr(self):
        """
         点击任务栏图标启动磁盘管理器
        :return:
        """

        self.click_and_focus_application_in_dock_by_attr("磁盘管理器")

    def right_click_open_diskmanager_in_dock_by_attr(self):
        """
         右键点击任务栏磁盘管理器图标启动
        :return:
        """

        # 如果任务栏没有文管，则将文管发送到任务栏
        self.right_click_application_in_dock_by_attr("磁盘管理器")
        try:
            pylinuxauto.click(*pylinuxauto.find_element_by_ocr("打开").center())
        except TypeError:
            pass

    def right_click_move_diskmanager_in_dock_by_attr(self):
        """
         任务栏右键磁盘管理器“移除驻留”
        :return:
        """
        self.right_click_move_in_dock_by_attr("磁盘管理器")

    def close_diskmanager_by_cmd(self):
        """
         关闭磁盘管理器并清理数据
        :return:
        """
        self.close_app("磁盘管理器")
        sleep(1)

    def enter_user_password(self):
        """
        打开磁盘管理器前，需验证用户信息，输入用户密码，并点击 "确认" 按钮
        :return:
        """

        # 输入密码前等待 1 秒，等待弹窗启动，增加容错
        sleep(1)

        try:
            # 判断是否出现输入用户密码弹窗
            if pylinuxauto.find_element_by_ocr("读取磁盘信息需要认证"):
                # 输入用户密码
                pylinuxauto.input_message(config.PASSWORD)
                sleep(1)
                # 点击"确认"按钮
                pylinuxauto.click(*pylinuxauto.find_element_by_ocr("确定").center())
                sleep(5)
        except TypeError:
            pass

    # =============================dock栏 下载器操作=======================================

    def click_downloader_in_dock_by_attr(self):
        """
         点击任务栏图标启动 下载器
        :return:
        """

        self.click_and_focus_application_in_dock_by_attr("下载器")
        sleep(1)

    def close_downloader_by_cmd(self):
        """
         关闭 下载器 并清理数据
        :return:
        """
        self.close_app("下载器")
        sleep(1)

    # =============================dock栏 文管操作=======================================
    def send_file_manager_to_dock_by_cmd(self):
        """
         发送文件管理器到任务栏
        :return:
        """
        self.send_link_to_dock("文件管理器")

    def open_file_manager_in_dock_by_attr(self):
        """
         点击任务栏图标启动文管
        :return:
        """
        self.click_and_focus_application_in_dock_by_attr("文件管理器")

    def click_file_manager_btn_in_dock_by_attr(self):
        """
         点击任务栏图标启动文管
        :return:
        """
        self.click_application_in_dock_by_attr("文件管理器")

    def right_click_open_new_window_in_file_manager_by_attr(self):
        """
         任务栏右键文件管理器“新建窗口“
        :return:
        """
        self.right_click_open_new_windows_in_dock_by_attr("文件管理器")

    def right_click_all_window_in_file_manager_by_attr(self):
        """
         任务栏右键文件管理器“所有窗口“
        :return:
        """
        self.right_click_all_windows_in_dock_by_attr("文件管理器")

    def right_click_file_manager_in_dock_by_attr(self):
        """
         在任务栏右键点击文管
        :return:
        """
        self.right_click_application_in_dock_by_attr("文件管理器")

    def right_click_forced_close_in_file_manager_by_attr(self):
        """
         右键dock栏上强制退出文管
        :return:
        """
        self.right_forced_close_in_dock_by_attr("文件管理器")

    def right_click_close_all_in_file_manager_by_attr(self):
        """
         右键dock栏上文件管理器 点击关闭所有
        :return:
        """
        self.right_click_close_all_in_dock_by_attr("文件管理器")

    def right_click_move_in_file_manager_by_attr(self):
        """
         任务栏右键文件管理器“移除驻留”
        :return:
        """
        self.right_click_move_in_dock_by_attr("文件管理器")

    def close_file_manager_by_cmd(self):
        """
         关闭文管并清理数据
        :return:
        """
        self.close_app("文件管理器")
        sleep(0.5)

    def close_control_center_by_cmd(self):
        """
         关闭控制中心并清理数据
        :return:
        """
        self.close_app("控制中心")
        sleep(1)

    def get_dde_file_manager_location(self):
        """
         返回dock栏文管文件坐标
        :return: 坐标
        """
        # return self.find_dock_image("dde_file_manager")
        return self.dog.element_center("Btn_文件管理器")

    # =============================dock栏 相册操作=======================================
    def double_click_album_in_dock_by_attr(self):
        """
         任务栏双击相册
        :return:
        """
        self.double_click_application_in_dock_by_attr("相册")

    def right_click_album_in_dock_by_attr(self):
        """
         任务栏右键点击相册
        :return:
        """
        self.right_click_application_in_dock_by_attr("相册")

    # =============================dock栏 影院操作=======================================
    def open_movie_in_dock_by_attr(self):
        """
         点击任务栏图标启动影院
        :return:
        """
        self.click_and_focus_application_in_dock_by_attr("影院")

    def send_file_deepin_movie_to_dock_by_cmd(self):
        """
         发送影院到任务栏
        :return:
        """
        self.send_link_to_dock("影院")

    def right_click_movie_in_dock_by_attr(self):
        """
         任务栏右键点击影院
        :return:
        """
        self.right_click_application_in_dock_by_attr("影院")

    def click_movie_btn_in_dock_by_attr(self):
        """
         点击任务栏图标启动影院
        :return:
        """
        self.click_application_in_dock_by_attr("影院")

    def close_movie_by_cmd(self):
        """
         关闭影院并清理数据
        :return:
        """
        self.close_app("影院")
        sleep(0.5)

    def get_deepin_movie_app_location(self) -> tuple:
        """
         返回dock栏的影院图标栏坐标
        :return:
        """
        # return self.find_system_desktop_image("deepin_movie")
        return self.dog.element_center("Btn_影院")

    # =============================dock栏 启动器操作=======================================
    def click_launcher_in_dock_by_attr(self, is_press_esc=True):
        """
         任务栏点击启动器
        :return:
        """
        if is_press_esc:
            pylinuxauto.esc()
        sleep(1)
        pylinuxauto.find_element_by_attr_path("Btn_launcheritem").click()
        sleep(2)
        # 启动器经常点击不响应，尝试再来一把
        try:
            DdeLauncherPublicMethod()
        except ApplicationStartError:
            pylinuxauto.find_element_by_attr_path("Btn_launcheritem").click()

    # =============================dock栏 右键菜单操作=======================================

    def right_click_launcher_in_dock_by_attr(self):
        """任务栏右键点击启动器,打开任务栏设置菜单
        :return:
        """
        pylinuxauto.find_element_by_attr_path("Btn_launcheritem", button=3).click()
        sleep(1)

    def select_dock_menu(self, number: int):
        """选择任务栏右键菜单中的选项（从上到下）
        :param number: 在菜单中的位置数
        :return:
        """
        self.right_click_launcher_in_dock_by_attr()
        for _ in range(number):
            pylinuxauto.press_key("down")
        sleep(0.5)
        logger.debug(f"选择右键菜单中的选项(从上到下)第{number}项")

    def reverse_select_dock_menu(self, number: int):
        """选择任务栏右键菜单中的选项（从下到上）
        :param number: 在菜单中的位置数
        :return:
        """
        self.right_click_launcher_in_dock_by_attr()
        for _ in range(number):
            pylinuxauto.press_key("up")
        sleep(0.5)
        logger.debug(f"选择右键菜单中的选项(从下到上)第{number}项")

    def select_right_menu_dock_mode(self):
        """任务栏选择右键菜单: 模式
        :return:
        """
        self.select_dock_menu(1)

    def select_right_menu_dock_location(self):
        """任务栏选择右键菜单: 位置
        :return:
        """
        self.select_dock_menu(2)

    def select_right_menu_dock_state(self):
        """任务栏选择右键菜单: 状态
        :return:
        """
        self.reverse_select_dock_menu(2)

    def click_right_menu_dock_set(self):
        """任务栏点击右键菜单: 任务栏设置
        :return:
        """
        self.reverse_select_dock_menu(1)
        pylinuxauto.enter()
        sleep(0.5)

    def click_right_submenu_dock_mode_efficient(self):
        """任务栏点击右键菜单: 模式 -> 高效模式
        :return:
        """
        self.select_right_menu_dock_mode()
        pylinuxauto.enter()
        pylinuxauto.select_submenu(2)
        sleep(0.5)

    def click_right_submenu_dock_mode_fashion(self):
        """任务栏点击右键菜单: 模式 -> 时尚模式
        :return:
        """
        self.select_right_menu_dock_mode()
        pylinuxauto.enter()
        pylinuxauto.select_submenu(1)
        sleep(0.5)

    def click_right_submenu_dock_location_up(self):
        """任务栏点击右键菜单: 位置 -> 上
        :return:
        """
        self.select_right_menu_dock_location()
        pylinuxauto.enter()
        pylinuxauto.select_submenu(1)
        sleep(1)

    def click_right_submenu_dock_location_down(self):
        """任务栏点击右键菜单: 位置 -> 下
        :return:
        """
        self.select_right_menu_dock_location()
        pylinuxauto.enter()
        pylinuxauto.select_submenu(2)
        sleep(1)

    def click_right_submenu_dock_location_left(self):
        """任务栏点击右键菜单: 位置 -> 左
        :return:
        """
        self.select_right_menu_dock_location()
        pylinuxauto.enter()
        pylinuxauto.reverse_select_menu(2)
        sleep(1)

    def click_right_submenu_dock_location_right(self):
        """任务栏点击右键菜单: 位置 -> 右
        :return:
        """
        self.select_right_menu_dock_location()
        pylinuxauto.enter()
        pylinuxauto.reverse_select_menu(1)
        sleep(1)

    def click_right_submenu_dock_state_show(self):
        """任务栏点击右键菜单: 状态 -> 一直显示
        :return:
        """
        self.select_right_menu_dock_state()
        pylinuxauto.enter()
        pylinuxauto.select_submenu(1)
        sleep(1)

    def click_right_submenu_dock_state_hide(self):
        """任务栏点击右键菜单: 状态 -> 一直隐藏
        :return:
        """
        self.select_right_menu_dock_state()
        pylinuxauto.enter()
        pylinuxauto.select_submenu(2)
        sleep(1)

    def click_right_submenu_dock_state_smart_hide(self):
        """任务栏点击右键菜单: 状态 -> 智能隐藏
        :return:
        """
        self.select_right_menu_dock_state()
        pylinuxauto.enter()
        pylinuxauto.reverse_select_menu(1)
        sleep(1)

    # =============================dock栏 显示桌面操作=======================================

    def click_show_desktop_in_dock_by_attr(self):
        """任务栏点击显示桌面
        :return:
        """
        pylinuxauto.find_element_by_attr_path("Btn_show-desktop").click()
        sleep(1)

    def click_show_desktop_area_in_dock_by_attr(self):
        """任务栏点击显示桌面区域
        :return:
        """
        pylinuxauto.find_element_by_attr_path("Form_showdesktoparea").click()
        sleep(1)

    # =============================dock栏 多任务视图操作=======================================

    def click_multitasking_in_dock_by_attr(self):
        """任务栏点击多任务视图
        :return:
        """
        pylinuxauto.find_element_by_attr_path("Btn_multitasking").click()
        sleep(1)

    # =============================dock栏 画板操作=======================================
    def close_draw_by_cmd(self):
        """
         关闭画板并清理数据
        :return:
        """
        self.close_app("画板")
        sleep(0.5)

    def open_draw_in_dock_by_attr(self):
        """
         点击任务栏图标启动画板
        :return:
        """
        self.click_and_focus_application_in_dock_by_attr("画板")

    def click_draw_btn_in_dock_by_attr(self):
        """
         点击dock栏的启动画板
        :return:
        """
        self.click_application_in_dock_by_attr("画板")

    def right_click_draw_btn_in_dock_by_attr(self):
        """
         右键点击dock栏的画板录屏
        :return:
        """
        self.right_click_application_in_dock_by_attr("画板")

    # =============================dock栏 回收站操作=======================================
    def open_trash_in_dock_by_attr(self):
        """
         打开dock栏的回收站
        :return:
        """
        pylinuxauto.find_element_by_attr_path("Btn_trash").click()
        sleep(0.5)

    def right_click_trash_in_dock_by_attr(self):
        """
         右键dock栏的回收站
        :return:
        """
        pylinuxauto.find_element_by_attr_path("Btn_trash", button=3).click()
        sleep(0.5)

    def drag_to_trash_in_dock_by_attr(self):
        """
         拖拽到dock栏右边插件区域的回收站
        :return:
        """
        pylinuxauto.drag_to(*self.dog.element_center("Btn_trash"))
        sleep(1)

    def clean_trash_in_dock_by_attr(self):
        """
         dock栏清空回收站
        :return:
        """
        self.right_click_trash_in_dock_by_attr()
        pylinuxauto.select_menu(2)
        sleep(0.5)

    # =============================dock栏 其他操作=======================================

    def right_click_disk_in_dock_by_attr(self):
        """
         在dock栏右键点击挂载设备按钮
        :return:
        """
        for i in pylinuxauto.find_element_by_attr_path(
            f"$//Btn_mainpanelcontrol//Form_tray-centralmethod"
        ).children:
            if i.name.startswith("Form_mount-item-key"):
                pylinuxauto.find_element_by_attr_path(
                    f"$//Btn_mainpanelcontrol//Form_tray-centralmethod/{i.name}"
                ).click(button=3)
        sleep(2)  # 响应比较慢

    def click_disk_in_dock_by_attr(self):
        """
         点击任务栏磁盘图标
        :return:
        """
        for i in pylinuxauto.find_element_by_attr_path(
            f"$//Btn_mainpanelcontrol//Form_tray-centralmethod"
        ).children:
            if i.name.startswith("Form_mount-item-key"):
                pylinuxauto.find_element_by_attr_path(
                    f"$//Btn_mainpanelcontrol//Form_tray-centralmethod/{i.name}"
                ).click()
        sleep(2)  # 响应比较慢

    def click_keyboard_btn_in_dock_by_attr(self):
        """
         点击托盘区域软键盘
        :return:
        """
        pylinuxauto.find_element_by_attr_path("Btn_onboard").click()

    def click_mount_ftp_icon_in_desktop_by_image(self):
        """
         点击右下角挂载ftp的图标
        :return:
        """
        try:
            _x, _y = self.find_dock_image("mount_ftp_icon_amd")
        except TemplateElementNotFound:
            _x, _y = self.find_dock_image("mount_ftp_icon_arm")
        pylinuxauto.click(_x, _y)

    def click_umount_icon_in_desktop_by_image(self):
        """
         点击右下角挂载ftp的图标
        :return:
        """
        try:
            _x, _y = self.find_dock_image("mount_ftp_icon_amd")
        except TemplateElementNotFound:
            _x, _y = self.find_dock_image("mount_ftp_icon_arm")
        pylinuxauto.click(_x + 243, _y - 3)

    def right_click_disk_usb_in_dock_by_image(self):
        """
         点击磁盘菜单中的U盘
        :return:
        """
        pylinuxauto.right_click(*self.find_dock_image("disk_usb", rate=0.8))

    def point_dock_main_window_by_attr(self):
        """
         鼠标移动到任务栏中心坐标
        :return:
        """
        pylinuxauto.move_to(*self.dog.element_center("Form_mainwindow"))

    def click_notifications_in_dock_by_attr(self):
        """
         点击任务栏最右侧通知中心按钮
        :return:
        """
        pylinuxauto.find_element_by_attr_path("Btn_notifications").click()

    # =============================文本编辑器=============================
    def open_editor_in_dock_by_attr(self):
        """
         dock栏点击启动文本编辑器
        :return:
        """
        self.click_and_focus_application_in_dock_by_attr("文本编辑器")

    def close_editor_by_cmd(self):
        """
         关闭文本编辑器并清理数据
        :return:
        """
        self.close_app("文本编辑器")

    # =============================dock栏 音乐操作=============================
    def open_music_in_dock_by_attr(self):
        """
         点击任务栏图标启动音乐
        :return:
        """
        if self.get_process_status("deepin-music"):
            self.kill_process("deepin-music")
            sleep(2)
        self.click_and_focus_application_in_dock_by_attr("音乐")

    def right_click_music_btn_in_dock_by_attr(self):
        """
         右键点击音乐
        :return:
        """
        self.right_click_application_in_dock_by_attr("音乐")

    def right_click_music_btn_in_dock_trayarea_by_attr(self):
        """
         右键点击托盘区域音乐图标
        :return:
        """
        pylinuxauto.find_element_by_attr_path("Btn_mainpanelcontrol").child(
            "Form_trayarea"
        ).child("Form_normalcontainer").child("Btn_deepin-music").click(3)

    def click_music_btn_in_dock_trayarea_by_attr(self):
        """
         点击托盘区域音乐图标
        :return:
        """
        pylinuxauto.find_element_by_attr_path("Btn_mainpanelcontrol").child(
            "Form_trayarea"
        ).child("Form_normalcontainer").child("Btn_deepin-music").click()

    # def get_deepin_music_location(self) -> tuple:
    #     """
    #      返回dock栏的音乐图标坐标
    #     :return:
    #     """
    #     return self.find_system_desktop_image("deepin_music")

    # =============================dock栏 相机操作=============================
    def open_camera_in_dock_by_attr(self):
        """
         点击任务栏图标启动相机
        :return:
        """
        self.click_and_focus_application_in_dock_by_attr("相机")

    def click_camera_btn_in_dock_by_attr(self):
        """
         点击任务栏图标启动相机
        :return:
        """
        self.click_application_in_dock_by_attr("相机")

    # =============================dock栏 控制中心操作=============================
    def click_control_center_in_dock_by_attr(self):
        """
         点击dock栏的启动控制中心
        :return:
        """
        self.click_and_focus_application_in_dock_by_attr("控制中心")

    # =============================dock栏 应用商城操作=============================
    def click_app_store_in_dock_by_attr(self):
        """
         点击dock栏的启动应用商店
        :return:
        """
        self.click_and_focus_application_in_dock_by_attr("应用商店")

    # =============================dock栏 日历操作=============================
    def click_calendar_in_dock_by_attr(self):
        """
         点击dock栏的启动日历
        :return:
        """
        self.click_and_focus_application_in_dock_by_attr("日历")

    def close_calendar_in_dock_by_cmd(self):
        """
         关闭日历
        :return:
        """
        self.close_app("日历")

    # =============================dock栏 浏览器操作=============================
    def click_browser_in_dock_by_attr(self):
        """
         点击dock栏的浏览器
        :return:
        """
        self.click_and_focus_application_in_dock_by_attr("浏览器")

    @classmethod
    def close_browser_in_dock_by_cmd(cls):
        """
         点击dock栏的浏览器
        :return:
        """
        cls.kill_process("browser")

    # =============================dock栏 截图录屏===============================
    def send_screen_recorder_to_dock_by_cmd(self):
        """
         发送截图录屏到任务栏
        :return:
        """
        self.send_link_to_dock("截图录屏")

    def click_screen_recorder_in_dock_by_attr(self):
        """
         鼠标左键点击dock栏的启动截图录屏
        :return:
        """
        self.click_application_in_dock_by_attr("截图录屏")

    def right_click_screen_recorder_in_dock_by_attr(self):
        """
         鼠标右键点击dock栏的启动截图录屏
        :return:
        """
        self.right_click_application_in_dock_by_attr("截图录屏")

    def right_click_move_in_screen_recorder_by_attr(self):
        """
         任务栏右键截图录屏“移除驻留”
        :return:
        """
        self.right_click_move_in_dock_by_attr("截图录屏")

    def click_stop_recorder_in_dock_by_attr(self):
        """
         点击任务栏停止录制按钮
        :return:
        """
        _x, _y, _w, _h = pylinuxauto.find_element_by_attr_path(
            "$//Form_pluginarea/Btn_deepin-screen-recorder-plugin"
        ).extents
        # x, y, w, h = pylinuxauto.find_element_by_attr_path(
        # "Form_pluginarea").children("Btn_deepin-screen-recorder-plugin").extents
        pylinuxauto.click(_x + _w / 4, _y + _h / 2)

    # =============================dock栏 相册=======================================
    def open_album_in_dock_by_attr(self):
        """
         dock栏启动相册
        :return:
        """
        self.click_and_focus_application_in_dock_by_attr("相册")

    def click_album_btn_in_dock_by_attr(self):
        """
         点击dock栏的启动相册
        :return:
        """
        self.click_application_in_dock_by_attr("相册")

    # =============================dock栏 全局搜索操作=======================================
    def right_click_grand_search_in_dock_by_attr(self):
        """
         右键点击dock栏的全局搜索图标
        :return:
        """
        pylinuxauto.find_element_by_attr_path("Btn_grand-search", button=3).click()
        sleep(0.5)

    def click_grand_search_in_dock_by_attr(self):
        """
         左键点击dock栏的全局搜索图标
        :return:
        """
        pylinuxauto.find_element_by_attr_path("Btn_grand-search").click()
        sleep(0.5)

    def click_set_button_by_attr(self):
        """
         单击全局搜索-搜索设置按钮
        :return:
        """
        pylinuxauto.find_element_by_attr_path("Btn_grand-search", button=3).click()
        pylinuxauto.select_menu(1)
        sleep(0.5)

    def move_to_grand_search_icon_by_attr(self):
        """
         挪动鼠标到dock栏全局搜索图标
        :return:
        """
        _x, _y = pylinuxauto.find_element_by_attr_path("Btn_grand-search").center()
        pylinuxauto.move_to(_x, _y)

    def change_dock_on_desktop_lef(self):
        """
         将任务栏设置在屏幕左侧显示
        :return:
        """
        self.point_dock_main_window_by_attr()
        pylinuxauto.right_click()
        pylinuxauto.select_menu(2)
        sleep(1)
        pylinuxauto.select_menu(2)

    @classmethod
    def change_dock_on_desktop_down(cls):
        """
         将任务栏设置在屏幕下方显示
        :return:
        """
        pylinuxauto.move_to_and_right_click("0", "600")  # 防止点击到应用图标
        pylinuxauto.select_menu(2)
        sleep(1)
        pylinuxauto.select_menu(1)

    @classmethod
    def recovery_dock_default_position_by_cmd(cls):
        """
         恢复dock栏默认下方显示
        :return:
        """
        Cmd.run("gsettings set com.deepin.dde.dock position bottom")

    # =============================dock栏 日志收集工具操作=======================================
    def open_log_in_dock_by_attr(self):
        """
         dock栏启动日志收集工具
        :return:
        """
        self.click_and_focus_application_in_dock_by_attr("日志收集工具")

    def close_log_by_cmd(self):
        """
         关闭日志收集工具
        :return:
        """
        self.close_app("日志收集工具")
        sleep(0.5)

    # =============================dock栏 帮助手册操作=======================================
    def open_manual_in_dock_by_attr(self):
        """
         dock栏启动帮助手册
        :return:
        """
        self.click_and_focus_application_in_dock_by_attr("帮助手册")

    def close_manual_by_cmd(self):
        """
         关闭帮助手册
        :return:
        """
        self.kill_process("dman")
        sleep(0.5)

    # =============================dock栏 字体管理器操作=======================================
    def open_font_manager_in_dock_by_attr(self):
        """
         dock栏启动字体管理器
        :return:
        """
        self.click_and_focus_application_in_dock_by_attr("字体管理器")

    def close_font_manager_by_cmd(self):
        """
         关闭字体管理器
        :return:
        """
        self.close_app("字体管理器")
        sleep(0.5)

    # =============================dock栏 归档管理器操作=======================================
    def open_compressor_in_dock_by_attr(self):
        """
         dock栏启动归档管理器
        :return:
        """
        self.click_and_focus_application_in_dock_by_attr("归档管理器")

    def close_compressor_by_cmd(self):
        """
         关闭归档管理器
        :return:
        """
        self.close_app("归档管理器")
        sleep(0.5)

    # =============================dock栏 文档查看器操作=======================================
    def open_reader_in_dock_by_attr(self):
        """
         dock栏启动文档查看器
        :return:
        """
        self.click_and_focus_application_in_dock_by_attr("文档查看器")

    def close_reader_by_cmd(self):
        """
         关闭文档查看器
        :return:
        """
        self.close_app("文档查看器")
        sleep(0.5)

    # =============================dock栏 系统监视器操作=======================================
    def open_system_monitor_in_dock_by_attr(self):
        """
         dock栏启动系统监视器
        :return:
        """
        self.click_and_focus_application_in_dock_by_attr("系统监视器")

    def close_system_monitor_by_cmd(self):
        """
         关闭系统监视器
        :return:
        """
        self.close_app("系统监视器")
        sleep(0.5)

    # =============================dock栏 终端操作=======================================
    def open_terminal_in_dock_by_attr(self):
        """
         dock栏启动终端
        :return:
        """
        self.click_and_focus_application_in_dock_by_attr("终端")

    def close_terminal_by_cmd(self):
        """
         关闭终端
        :return:
        """
        self.close_app("终端")
        sleep(0.5)

    # =============================dock栏 计算器操作=======================================
    def open_calculator_in_dock_by_attr(self):
        """
         dock栏启动日志收集工具
        :return:
        """
        self.click_and_focus_application_in_dock_by_attr("计算器")

    def close_calculator_by_cmd(self):
        """
         关闭计算器
        :return:
        """
        self.close_app("计算器")
        sleep(0.5)

    # =============================dock栏 启动盘制作工具操作=======================================
    def open_boot_maker_in_dock_by_attr(self):
        """
         dock栏启动 启动盘制作工具
        :return:
        """
        self.click_and_focus_application_in_dock_by_attr("启动盘制作工具")

    def close_boot_maker_by_cmd(self):
        """
         关闭 启动盘制作工具
        :return:
        """
        self.close_app("启动盘制作工具")
        sleep(0.5)

    # =============================dock栏 软件包安装器操作=======================================
    def open_deb_installer_in_dock_by_attr(self):
        """
         dock栏启动软件包安装器
        :return:
        """
        self.click_and_focus_application_in_dock_by_attr("软件包安装器")

    def close_deb_installer_by_cmd(self):
        """
         关闭软件包安装器
        :return:
        """
        self.close_app("软件包安装器")
        sleep(0.5)

    # =============================dock栏 语音记事本操作=======================================
    def open_voice_note_in_dock_by_attr(self):
        """
         dock栏启动语音记事本
        :return:
        """
        self.click_and_focus_application_in_dock_by_attr("语音记事本")

    def close_voice_note_by_cmd(self):
        """
         关闭软件语音记事本
        :return:
        """
        self.close_app("语音记事本")
        sleep(0.5)

    # =============================dock栏 设备管理器操作=======================================
    def open_devicemanager_in_dock_by_attr(self):
        """
         dock栏启动设备管理器
        :return:
        """
        self.click_and_focus_application_in_dock_by_attr("设备管理器")

    def close_devicemanager_by_cmd(self):
        """
         关闭软件设备管理器
        :return:
        """
        self.close_app("设备管理器")
        sleep(0.5)

    # =============================dock栏 安全中心操作=======================================
    def open_defender_in_dock_by_attr(self):
        """
         dock栏启动安全中心
        :return:
        """
        self.click_and_focus_application_in_dock_by_attr("安全中心")

    def close_defender_by_cmd(self):
        """
         关闭软件安全中心
        :return:
        """
        self.close_app("安全中心")
        sleep(0.5)

    # =============================dock栏 服务与支持操作=======================================
    def open_service_support_in_dock_by_attr(self):
        """
         dock栏启动服务与支持
        :return:
        """
        self.click_and_focus_application_in_dock_by_attr("服务与支持")

    def close_service_support_by_cmd(self):
        """
         关闭软件服务与支持
        :return:
        """
        self.close_app("服务与支持")
        sleep(0.5)

    # =============================dock栏 连连看操作=======================================
    def open_lianliankan_in_dock_by_attr(self):
        """
         dock栏启动连连看
        :return:
        """
        self.click_and_focus_application_in_dock_by_attr("连连看")

    def close_lianliankan_by_cmd(self):
        """
         关闭软件连连看
        :return:
        """
        self.close_app("连连看")
        sleep(0.5)

    # =============================dock栏 五子棋操作=======================================
    def open_gomoku_in_dock_by_attr(self):
        """
         dock栏启动五子棋
        :return:
        """
        self.click_and_focus_application_in_dock_by_attr("五子棋")

    def close_gomoku_by_cmd(self):
        """
         关闭软件五子棋
        :return:
        """
        self.close_app("五子棋")
        sleep(0.5)

    # =============================dock栏 托盘区域操作=======================================
    def click_popupindicator_in_dock_tray_area_by_attr(self):
        """
        点击任务栏托盘区域的：向上箭头
        :return:
        """

        pylinuxauto.find_element_by_attr_path("dde-dock").child(
            "Form_mainwindow"
        ).child("Form_appoverflowarea_3").child("Btn_tray").child(
            "Form_popupindicator"
        ).click()
        sleep(1)

    def click_quick_panel_in_dock_tray_area_by_attr(self):
        """
        点击任务栏托盘区域的：快捷面板
        :return:
        """

        pylinuxauto.find_element_by_attr_path("dde-dock").child(
            "Form_mainwindow"
        ).child("Form_appoverflowarea_3").child("Btn_dde-quick-panel").click()
        sleep(1)

    def click_datetime_in_dock_tray_area_by_attr(self):
        """
        点击任务栏托盘区域的：时间
        :return:
        """

        pylinuxauto.find_element_by_attr_path("dde-dock").child(
            "Form_mainwindow"
        ).child("Form_appoverflowarea_4").child("Btn_datetime").click()
        sleep(1)

    def click_icon_deployment_but_in_dock_by_attr(self):
        """
        点击托盘区域icon展开/收起按钮
        """
        pylinuxauto.find_element_by_attr_path("Form_iconbutton_2").click()

    @classmethod
    def dde_launcher_menu_retraction(cls):
        """
        启动器菜单从全屏化收起
        """
        pylinuxauto.find_element_by_attr_path(
            "/dde-launcher/Btn_btn-togglemode"
        ).click()


if __name__ == "__main__":
    DdeDockPublicMethod().click_ai_assistant_in_dock_by_attr()
    DdeDockPublicMethod().close_ai_assistant_by_cmd()
    DdeDockPublicMethod().click_icon_deployment_but_in_dock_by_attr()
