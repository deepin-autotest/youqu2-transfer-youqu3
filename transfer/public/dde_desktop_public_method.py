#!/usr/bin/env python3 # pylint: disable=too-many-lines
# _*_ coding:utf-8 _*_
# SPDX-FileCopyrightText: 2023 UnionTech Software Technology Co., Ltd.
# SPDX-License-Identifier: GPL-2.0-only
from youqu3.cmd import Cmd
from config import config
from youqu3 import setting
from youqu3 import logger
from youqu3 import log
from youqu3 import sleep
from youqu3.gui import pylinuxauto
import os
import re
import shutil

import dbus
from youqu3 import log
from youqu3 import logger
from youqu3 import setting
from youqu3 import sleep
from youqu3.exceptions import ApplicationStartError
from youqu3.exceptions import GetWindowInformation
from youqu3.exceptions import NoIconOfThisSize
from youqu3.exceptions import TemplateElementNotFound, ElementNotFound
from youqu3.gui import pylinuxauto
from youqu3.gui.pylinuxauto.ui.wayland_windowinfo import WaylandWindowInfo

from right_menu_public_method import RightMenuPublicMethod


@log
class _DdeDesktopPublicBaseMethod(RightMenuPublicMethod):
    """
    系统桌面操作层封装
    """

    APP_NAME = "dde-desktop"
    DESC = "/usr/bin/dde-desktop"

    def __init__(self, file_box=True, number=-1, pause: int = 1):
        self.file_box = file_box
        self.number = number
        self.pause = pause
        kwargs = {}
        kwargs["name"] = self.APP_NAME
        kwargs["description"] = self.DESC
        kwargs["check_start"] = True
        kwargs["config_path"] = config.UI_INI_PATH

        setattr(self.ui, "window_info", self.window_info)
        if setting.IS_WAYLAND:
            self.retry = 1
            self.wwininfo = WaylandWindowInfo()

    def window_info(self):
        """
         重写底层 window_info
        :return: 窗口信息
        """
        if setting.IS_X11:
            try:
                # Get window_operate ID based on package name
                app_id = Cmd.run(
                    f"xdotool search --classname --onlyvisible {self.APP_NAME}",
                    interrupt=False,
                    print_log=False,
                    command_log=False,
                ).split("\n")
                app_id_list = [int(_id) for _id in app_id if _id]  # to int
                app_id_list.sort()
                logger.debug(f"app_id_list: {app_id_list}")
                # Obtain the information of the window_operate according to the ID
                actual_id = app_id_list[-1]
                if len(app_id_list) > 1:
                    # 获取所有id的长度
                    _win_size = [[x, self.__window_size(x)[0]] for x in app_id_list]
                    # 从小到大排序
                    _win_size = sorted(
                        [x for x in _win_size if x[1] > 720], key=lambda x: x[1]
                    )
                    if self.file_box:
                        # 取最小的
                        actual_id = _win_size[0][0]
                    else:
                        # 取最大的
                        actual_id = _win_size[-1][0]
                return Cmd.run(
                    f"xwininfo -id {actual_id}",
                    interrupt=False,
                    print_log=False,
                    command_log=False,
                )
            except ElementNotFound as exc:
                raise ApplicationStartError(f"{self.APP_NAME, exc}") from exc
        elif setting.IS_WAYLAND:
            if hasattr(self.wwininfo.library, "GetAllWindowStatesList"):
                for _ in range(self.retry + 1):
                    info = self.wwininfo.window_info().get(self.APP_NAME)
                    if info is None:
                        sleep(1)
                    else:
                        break
                else:
                    raise ApplicationStartError(self.APP_NAME)
                if isinstance(info, dict):
                    return info
                elif isinstance(info, list):
                    return info[self.number]
            else:
                proxy_object = dbus.SessionBus().get_object("org.kde.KWin", "/dde")
                dbus.Interface(proxy_object, "org.kde.KWin").WindowMove()
                sleep(self.pause)
                pylinuxauto.esc()
                return self.wwininfo._window_info()
        return None

    @classmethod
    def __window_size(cls, window_id):
        """
         获取窗口大小
        :param window_id: 窗口ID
        :return: 窗口大小
        """
        try:
            app_window_info = Cmd.run(
                f"xwininfo -id {window_id}",
                interrupt=False,
                print_log=False,
                command_log=False,
            )
            window_width = re.findall(r"Width.*:\s(\d+)", app_window_info)[0]
            window_height = re.findall(r"Height.*:\s(\d+)", app_window_info)[0]
            logger.debug(f"获取窗口大小 {window_width}*{window_height}")
            return int(window_width), int(window_height)
        except (IndexError, KeyError) as exc:
            raise GetWindowInformation(f"获取窗口大小错误 {exc}") from exc

    @staticmethod
    def get_file_or_dir_axes_by_config(name):
        """
         根据桌面配置文件获取文件或者文件夹坐标
        :param name: 文件名称
        :return: 坐标
        """
        from youqu3.desktop import get_desktop_file_location_by_config

        return get_desktop_file_location_by_config(name)

    def click_file_in_desktop_by_config(self, file_name):
        """
         通过配置文件点击桌面文件
        :param file_name: 文件名称
        :return:
        """
        pylinuxauto.click(*self.get_file_or_dir_axes_by_config(file_name))

    def double_click_file_in_desktop_by_config(self, file_name):
        """
         通过配置文件双击桌面文件
        :param file_name: 文件名称
        :return:
        """
        pylinuxauto.double_click(*self.get_file_or_dir_axes_by_config(file_name))
        sleep(2)

    def right_click_file_in_desktop_by_config(self, file_name):
        """
         通过配置文件右键点击桌面文件
        :param file_name: 文件名称
        :return:
        """
        pylinuxauto.right_click(*self.get_file_or_dir_axes_by_config(file_name))

    @staticmethod
    def desktop_dbus():
        """
         桌面的dbus对象
        :return: 桌面 dbus 对象
        """
        return Dbus(
            "com.deepin.daemon.Appearance",
            "/com/deepin/daemon/Appearance",
            "com.deepin.daemon.Appearance",
        )

    @staticmethod
    def display_dbus():
        """
         显示器的dbus对象
        :return:
        """
        return Dbus(
            "com.deepin.daemon.Display",
            "/com/deepin/daemon/Display",
            "com.deepin.daemon.Display",
        )

    @classmethod
    def find_system_desktop_image(cls, *elements):
        """
         通过图片查找桌面元素坐标
        :param elements:
        :return:
        """
        element = tuple(map(lambda x: f"{config.PIC_RES_PATH}/{x}", elements))
        return pylinuxauto.find_element_by_image(*element).center().center()

    def double_click_file_in_right_view_by_attr(self, file_name):
        """
         双击打开文管右侧文件
        :param file_name: 文件名称
        :return:
        """
        pylinuxauto.find_element_by_attr_path(f"$//file_view/{file_name}").point()
        # pylinuxauto.find_element_by_attr_path("right_view").child(file_name).point()   # 多个computer_window定位失败的问题
        pylinuxauto.double_click()

    def click_element_in_desktop_by_image(self, *pic):
        """
         点击桌面元素
        :param pic: 图片路径
        :return:
        """
        pylinuxauto.click(*self.find_system_desktop_image(*pic))

    def double_click_element_in_desktop_by_image(self, *pic):
        """
         双击桌面元素
        :param pic: 图片路径
        :return:
        """
        pylinuxauto.double_click(*self.find_system_desktop_image(*pic))
        sleep(2)

    def right_click_element_in_desktop_by_image(self, *pic):
        """
         右键桌面元素
        :param pic: 图片路径
        :return:
        """
        pylinuxauto.right_click(*self.find_system_desktop_image(*pic))

    def move_to_element_in_desktop_by_image(self, *pic):
        """
         移动到桌面元素
        :param pic: 图片路径
        :return:
        """
        pylinuxauto.move_to(*self.find_system_desktop_image(*pic))

    def click_dir_in_desktop_plugs_by_ui(self, dir_name, flag, offset_y=None):
        """
         调用文管插件，点击指定文件夹
        :param dir_name:  文件名
        :param flag: import 导入窗口， export 导出窗口
        :return:
        """

        if flag in ("import", "export"):
            _x, _y = pylinuxauto.find_element_by_ui(
                dir_name, offset_y=offset_y, appname="", config_path=""
            ).center()
            if flag != "import":
                _y = _y - 38
            else:
                tmp_ = pylinuxauto.find_element_by_ocr("最近使用").center()
                if tmp_ is False:
                    _y = _y - 40
            pylinuxauto.move_to_and_click(_x, _y)
        else:
            logger.error("flag Error")

    def click_file_in_desktop_plugs_by_attr(self, filename):
        """
         调用文管插件，点击指定文件
        :param filename: 文件名称
        :return:
        """
        pylinuxauto.find_element_by_attr_path(f"$//file_view/{filename}").point()
        # pylinuxauto.find_element_by_attr_path('file_view').child(filename).point()
        pylinuxauto.click()

    def double_click_file_in_desktop_plugs_by_attr(self, filename):
        """
         调用文管插件，双击指定文件
        :param filename: 文件名称
        :return:
        """
        pylinuxauto.find_element_by_attr_path(f"$//file_view/{filename}").point()
        pylinuxauto.double_click()

    def right_click_file_in_desktop_plugs_by_attr(self, filename):
        """
         调用文管插件，右键点击指定文件
        :param filename: 文件名称
        :return:
        """
        pylinuxauto.find_element_by_attr_path(f"$//file_view/{filename}").point()
        # pylinuxauto.find_element_by_attr_path('file_view').child(filename).point()
        pylinuxauto.right_click()


class DdeDesktopPublicMethod(_DdeDesktopPublicBaseMethod):
    """
    系统桌面业务层
    包含多媒体应用调用文管的文管小窗口
    """

    # ============== 文件选择框 ===========================

    def click_open_btn_in_desktop_plugs_by_ui(self):
        """
         调用文管插件，点击右下角“打开“
        :return:
        """
        pylinuxauto.click(
            *pylinuxauto.find_element_by_ui("打开", appname="", config_path="").center()
        )

    def click_cancel_btn_in_desktop_plugs_save_by_ui(self):
        """
         调用文管插件，点击右下角“取消“
        :return:
        """
        pylinuxauto.click(
            *pylinuxauto.find_element_by_ui(
                "取消保存", appname="", config_path=""
            ).center()
        )

    def click_cancel_btn_in_desktop_plugs_import_by_ui(self):
        """
         调用文管插件，点击右下角“取消“
        :return:
        """
        pylinuxauto.click(
            *pylinuxauto.find_element_by_ui(
                "取消打开", appname="", config_path=""
            ).center()
        )

    def click_ok_btn_in_pop_up_window_by_ui(self):
        """
         点击小弹窗“确定”按钮
        :return:
        """
        pylinuxauto.click(
            *pylinuxauto.find_element_by_ui(
                "关闭弹窗-确定", appname="", config_path=""
            ).center()
        )

    def click_ok_btn_in_open_mode_window_by_attr(self):
        """
         点击打开方式小弹窗“确定”按钮
        :return:
        """
        # pylinuxauto.click(*pylinuxauto.find_element_by_ui("打开方式-确定", appname="", config_path="").center())
        pylinuxauto.find_element_by_attr_path("确 定").click()

    def click_cancel_btn_in_open_mode_window_by_ui(self):
        """
         点击打开方式小弹窗“取消”按钮
        :return:
        """
        # pylinuxauto.click(*pylinuxauto.find_element_by_ui("打开方式-取消", appname="", config_path="").center())
        pylinuxauto.find_element_by_attr_path("取 消").click()

    def click_close_btn_in_open_mode_window_by_attr(self):
        """
         点击打开方式小弹窗“关闭”按钮
        :return:
        """
        pylinuxauto.find_element_by_attr_path(
            "$//DTitlebarButtonArea//DTitlebarDWindowCloseButton"
        ).click()

    def click_cancel_btn_in_pop_up_window_by_ui(self):
        """
         点击小弹窗的“取消”按钮
        :return:
        """
        pylinuxauto.click(
            *pylinuxauto.find_element_by_ui(
                "关闭弹窗-取消", appname="", config_path=""
            ).center()
        )

    def click_formate_box_in_desktop_plugs_by_ui(self, flag="import"):
        """
         调用文管插件，点击右下角“格式框“
        :param flag: import 导入插件框，其他，导出插件框
        :return:
        """
        _x, _y = pylinuxauto.find_element_by_ui(
            "格式框", appname="", config_path=""
        ).center()
        if flag != "import":
            _y = _y - 40
        pylinuxauto.click(_x, _y)

    def click_recent_dir_in_desktop_plugs_by_ui(self, flag="import"):
        """
         调用文管插件，点击右下角“最近使用“
        :param flag: import 导入插件框，export，导出插件框
        :return:
        """
        if flag in ("import", "export"):
            _x, _y = pylinuxauto.find_element_by_ui(
                "最近使用", appname="", config_path=""
            ).center()
            if flag != "import":
                _x, _y = 0, 0
            pylinuxauto.click(_x, _y)
        else:
            logger.error("flag Error")

    def click_home_dir_in_desktop_plugs_by_ui(self, flag="import"):
        """
         调用文管插件，点击右下角“主目录“
        :param flag: import 导入插件框，其他，导出插件框
        :return:
        """
        self.click_dir_in_desktop_plugs_by_ui("主目录", flag)

    def click_desktop_dir_in_desktop_plugs_by_ui(self, flag="import"):
        """
         调用文管插件，点击右下角“桌面“
        :param flag: import 导入插件框，其他，导出插件框
        :return:
        """
        self.click_dir_in_desktop_plugs_by_ui("桌面", flag)

    def click_videos_dir_in_desktop_plugs_by_ui(self, flag="import"):
        """
         调用文管插件，点击右下角“视频“
        :param flag: import 导入插件框，其他，导出插件框
        :return:
        """
        offset_y = None
        for _ in range(4):
            x, y, w, h = self.ui.window_location_and_sizes()
            if w == 0 and h == 0:
                sleep(1)
            else:
                break
        pic_path = self.save_temporary_picture(x, y, w, h)
        if pylinuxauto.find_element_by_ocr(
            "最近使用", picture_abspath=pic_path + ".png"
        ):
            offset_y = 38
        self.click_dir_in_desktop_plugs_by_ui("视频", flag, offset_y=offset_y)

    def click_music_dir_in_desktop_plugs_by_ui(self, flag="import"):
        """
         调用文管插件，点击右下角“音乐“
        :param flag: import 导入插件框，其他，导出插件框
        :return:
        """
        self.click_dir_in_desktop_plugs_by_ui("音乐", flag)

    def click_pictures_dir_in_desktop_plugs_by_ui(self, flag="import", offset_y=None):
        """
         调用文管插件，点击右下角“图片“
        :param flag: import 导入插件框，其他，导出插件框
        :return:
        """
        self.click_dir_in_desktop_plugs_by_ui("图片", flag, offset_y=offset_y)

    def click_documents_dir_in_desktop_plugs_by_ui(self, flag="import"):
        """
         调用文管插件，点击右下角“文档“
        :param flag: import 导入插件框，其他，导出插件框
        :return:
        """
        self.click_dir_in_desktop_plugs_by_ui("文档", flag)

    def click_downloads_dir_in_desktop_plugs_by_ui(self, flag="import"):
        """
         调用文管插件，点击右下角“下载“
        :param flag: import 导入插件框，其他，导出插件框
        :return:
        """
        self.click_dir_in_desktop_plugs_by_ui("下载", flag)

    def click_computer_dir_in_desktop_plugs_by_ui(self, flag="import"):
        """
         调用文管插件，点击右下角“计算机“
        :param flag: import 导入插件框，其他，导出插件框
        :return:
        """
        self.click_dir_in_desktop_plugs_by_ui("计算机", flag)

    def click_save_btn_in_desktop_plugs_by_ui(self):
        """
         调用文管插件，点击右下角“保存“（左右布局）
        :return:
        """
        pylinuxauto.click(
            *pylinuxauto.find_element_by_ui("保存", appname="", config_path="").center()
        )

    def click_blank_space_in_desktop_plugs_by_ui(self):
        """
         点击文管插件空白处
        :return:
        """
        pylinuxauto.click(*pylinuxauto.find_element_by_ui("空白处"), _type="xdotool")

    def click_icon_view_btn_in_desktop_plugs_by_ui(self):
        """
         调用文管插件，点击右下角“图标视图“
        :return:
        """
        pylinuxauto.click(
            *pylinuxauto.find_element_by_ui(
                "图标视图", appname="", config_path=""
            ).center()
        )

    def click_list_view_btn_in_desktop_plugs_by_ui(self):
        """
         调用文管插件，点击右下角“列表视图“
        :return:
        """
        pylinuxauto.click(
            *pylinuxauto.find_element_by_ui(
                "列表视图", appname="", config_path=""
            ).center()
        )

    def click_first_file_in_desktop_plugs_by_ui(self):
        """
         调用文管插件，点击“列表视图下第一个文件“
        :return:
        """
        pylinuxauto.click(
            *pylinuxauto.find_element_by_ui(
                "列表视图下第一个文件", appname="", config_path=""
            ).center()
        )

    def double_click_first_file_in_desktop_plugs_by_ui(self):
        """
         调用文管插件，双击“列表视图下第一个文件“
        :return:
        """
        pylinuxauto.double_click(
            *pylinuxauto.find_element_by_ui(
                "列表视图下第一个文件", appname="", config_path=""
            ).center()
        )

    def click_second_file_in_desktop_plugs_by_ui(self):
        """
         调用文管插件，点击右下角“列表视图下第二个文件“
        :return:
        """
        pylinuxauto.click(
            *pylinuxauto.find_element_by_ui(
                "列表视图下第二个文件", appname="", config_path=""
            ).center()
        )

    def double_click_second_file_in_desktop_plugs_by_ui(self):
        """
         调用文管插件，双击右下角“列表视图下第二个文件“
        :return:
        """
        pylinuxauto.click(
            *pylinuxauto.find_element_by_ui(
                "列表视图下第二个文件", appname="", config_path=""
            ).center()
        )

    def double_click_third_file_in_desktop_plugs_by_ui(self):
        """
         调用文管插件，双击“列表视图下第三个文件“
        :return:
        """
        pylinuxauto.double_click(
            *pylinuxauto.find_element_by_ui(
                "列表视图下第三个文件", appname="", config_path=""
            ).center()
        )

    def click_third_file_in_desktop_plugs_by_ui(self):
        """
         调用文管插件，点击右下角“列表视图下第三个文件“
        :return:
        """
        pylinuxauto.click(
            *pylinuxauto.find_element_by_ui(
                "列表视图下第三个文件", appname="", config_path=""
            ).center()
        )

    # ============================= 系统桌面 ====================================

    def right_click_new_folder_in_desktop_by_image(self):
        """
         右键点击新建文件夹
        :return:
        """
        pylinuxauto.right_click(*self.find_system_desktop_image("folder"))

    def click_new_folder_in_desktop_by_image(self):
        """
         点击新建文件夹
        :return:
        """
        pylinuxauto.click(*self.find_system_desktop_image("folder"))

    def right_click_center_in_desktop_by_attr(self):
        """
         在桌面中心点点击右键
        :return:
        """
        try:
            pylinuxauto.find_element_by_attr_path(
                "screen_canvas_view", button=3
            ).click()
        except ElementNotFound:
            pylinuxauto.right_click(960, 540)

    def click_center_in_desktop_by_attr(self):
        """
         在桌面中心点点击左键
        :return:
        """
        try:
            pylinuxauto.find_element_by_attr_path("screen_canvas_view").click()
        except ElementNotFound:
            pylinuxauto.click(960, 540)

    def right_click_left_in_desktop_by_attr(self):
        """
         在桌面的左侧1/8处点击右键
        :return:
        """
        try:
            desktop_x, desktop_y = pylinuxauto.find_element_by_attr_path(
                "screen_canvas_view"
            ).center()
        except ElementNotFound:
            desktop_x, desktop_y = 960, 520
        pylinuxauto.right_click(desktop_x / 4, desktop_y / 4)

    def click_left_in_desktop_by_attr(self):
        """
         在桌面的左侧1/8处点击
        :return:
        """
        try:
            desktop_x, desktop_y = pylinuxauto.find_element_by_attr_path(
                "screen_canvas_view"
            ).center()
        except ElementNotFound:
            desktop_x, desktop_y = 960, 520
        pylinuxauto.click(desktop_x / 4, desktop_y / 4)

    def click_zero_in_desktop_by_attr(self):
        """
         在桌面的0,0区域点击
        :return:
        """
        pylinuxauto.click(10, 10)

    def move_mouse_to_center_and_drag_to_zero(self):
        """
         从桌面中心拖动鼠标到右上角
        :return:
        """
        # 获取中心坐标
        try:
            start_x, start_y = pylinuxauto.find_element_by_attr_path(
                "screen_canvas_view"
            ).center()
        except ElementNotFound:
            start_x, start_y = 960, 520
        pylinuxauto.move_on_and_drag_to((start_x, start_y), (0, 0))

    def move_to_desktop_center(self):
        """
         移动鼠标到桌面中心
        :return:
        """
        try:
            pylinuxauto.move_to(*self.dog.element_center("screen_canvas_view"))
        except ElementNotFound:
            pylinuxauto.move_to(960, 520)

    def locate_left_in_desktop_by_attr(self):
        """
         在桌面左边定位
        :return:
        """
        try:
            desktop_x, desktop_y = pylinuxauto.find_element_by_attr_path(
                "screen_canvas_view"
            ).center()
        except ElementNotFound:
            desktop_x, desktop_y = 960, 520
        return desktop_x / 2, desktop_y / 2

    def select_two_file_in_desktop_by_attr(self):
        """
         拖动框选两个文件
        :return:
        """
        start_x, start_y = self.locate_left_in_desktop_by_attr()
        rel_x, rel_y = 150, 335
        pylinuxauto.draw_line(start_x - 30, start_y - 30, rel_x, rel_y)

    def create_two_dir_and_select_by_image(self):
        """
         拖动框选两个文件夹并框选他们
        :return:
        """
        self.new_dir_in_desktop_by_cmd("新建文件夹")
        start_x, start_y = self.get_dir_location()
        self.new_dir_in_desktop_by_cmd("新建文件夹1")
        rel_x, rel_y = 150, 335
        pylinuxauto.draw_line(start_x - 30, start_y - 30, rel_x, rel_y)

    def build_new_folder_in_desktop_by_right_menu(self):
        """
         桌面新建名为“新建文件夹”的目录
        :return:
        """
        self.right_click_left_in_desktop_by_attr()
        self.click_new_folder_in_right_menu_by_image()

    def build_new_word_in_desktop_by_right_menu(self):
        """
         右键桌面新建一个word文档
        :return:
        """
        self.right_click_left_in_desktop_by_attr()
        self.click_new_document_in_right_menu_by_image()
        self.click_word_in_right_menu_by_image()

    def build_new_excel_in_desktop_by_right_menu(self):
        """
         右键桌面新建一个excel文档
        :return:
        """
        self.right_click_left_in_desktop_by_attr()
        self.click_new_document_in_right_menu_by_image()
        self.click_excel_in_right_menu_by_image()

    def build_new_ppt_in_desktop_by_right_menu(self):
        """
         右键桌面新建一个ppt文档
        :return:
        """
        self.right_click_left_in_desktop_by_attr()
        self.click_new_document_in_right_menu_by_image()
        self.click_ppt_in_right_menu_by_image()

    def build_new_txt_in_desktop_by_right_menu(self):
        """
         右键桌面新建一个txt文档
        :return:
        """
        self.right_click_left_in_desktop_by_attr()
        self.click_new_document_in_right_menu_by_image()
        self.click_txt_in_right_menu_by_image()

    def build_hidden_txt_in_desktop_by_cmd(self):
        """
         命令行创建一个隐藏的文本文档 <.hidden.txt>
        :return:
        """
        self.new_file_in_desktop_by_cmd(".hidden.txt")

    def sort_by_name_in_desktop_by_right_menu(self):
        """
         右键点击以“名称”排序
        :return:
        """
        self.right_click_left_in_desktop_by_attr()
        self.click_sort_method_in_right_menu_by_image()
        self.click_name_in_right_menu_by_image()

    def sort_by_time_in_desktop_by_right_menu(self):
        """
         右键点击以“修改时间”排序
        :return:
        """
        self.right_click_left_in_desktop_by_attr()
        self.click_sort_method_in_right_menu_by_image()
        self.click_change_time_in_right_menu_by_image()

    def sort_by_size_in_desktop_by_right_menu(self):
        """
         右键点击以“大小”排序
        :return:
        """
        self.right_click_left_in_desktop_by_attr()
        self.click_sort_method_in_right_menu_by_image()
        self.click_size_in_right_menu_by_image()

    def sort_by_type_in_desktop_by_right_menu(self):
        """
         右键点击以“类型”排序
        :return:
        """
        self.right_click_left_in_desktop_by_attr()
        self.click_sort_method_in_right_menu_by_image()
        self.click_type_in_right_menu_by_image()

    # ======图标大小========
    def icon_minimum_in_desktop_by_right_menu(self):
        """
         "右键点击选择图标“极小”
        :return:
        """
        self.right_click_left_in_desktop_by_attr()
        self.click_icon_size_in_right_menu_by_image()
        self.click_minist_in_right_menu_by_image()

    def icon_small_in_desktop_by_right_menu(self):
        """
         右键点击选择图标“小”
        :return:
        """
        self.right_click_left_in_desktop_by_attr()
        self.click_icon_size_in_right_menu_by_image()
        self.click_mini_in_right_menu_by_image()

    def icon_middle_in_desktop_by_right_menu(self):
        """
         右键点击选择图标“中”
        :return:
        """
        self.right_click_left_in_desktop_by_attr()
        self.click_icon_size_in_right_menu_by_image()
        self.click_middle_in_right_menu_by_image()

    def icon_big_in_desktop_by_right_menu(self):
        """
         右键点击选择图标“大”
        :return:
        """
        self.right_click_left_in_desktop_by_attr()
        self.click_icon_size_in_right_menu_by_image()
        self.click_big_in_right_menu_by_image()

    def icon_maximum_in_desktop_by_right_menu(self):
        """
         右键点击选择图标“极大”
        :return:
        """
        self.right_click_left_in_desktop_by_attr()
        self.click_icon_size_in_right_menu_by_image()
        self.click_bigist_in_right_menu_by_image()

    def select_icon_size_in_desktop_by_right_menu(self, size):
        """
         右键菜单设置桌面图标大小
        :param size:
        :return:
        """
        size_dict = {
            "极小": self.icon_minimum_in_desktop_by_right_menu,
            "小": self.icon_small_in_desktop_by_right_menu,
            "中": self.icon_middle_in_desktop_by_right_menu,
            "大": self.icon_big_in_desktop_by_right_menu,
            "极大": self.icon_maximum_in_desktop_by_right_menu,
        }
        options = size_dict.get(size)
        if options:
            options()
        else:
            raise NoIconOfThisSize(size)

    def select_auto_sort_in_desktop_by_right_menu(self):
        """
         右键点击“自动排列”
        :return:
        """
        self.right_click_left_in_desktop_by_attr()
        self.click_auto_sort_in_right_menu_by_image()

    def select_paste_in_desktop_by_right_menu(self):
        """
         桌面右键点击“粘贴”
        :return:
        """
        self.right_click_left_in_desktop_by_attr()
        self.click_paste_in_right_menu_by_image()

    def select_all_in_desktop_by_right_menu(self):
        """
         桌面右键点击“所有”
        :return:
        """
        self.right_click_left_in_desktop_by_attr()
        self.click_select_all_in_right_menu_by_image()

    def select_terminal_in_desktop_by_right_menu(self):
        """
         桌面右键点击“在终端中打开”
        :return:
        """
        self.right_click_left_in_desktop_by_attr()
        self.click_terminal_in_right_menu_by_image()

    def select_setting_display_in_desktop_by_right_menu(self):
        """
         桌面右键点击“显示设置”
        :return:
        """
        self.right_click_left_in_desktop_by_attr()
        self.click_display_setting_in_right_menu_by_image()

    def select_wallpaper_in_desktop_by_right_menu(self):
        """
         桌面右键点击“壁纸与屏保”
        :return:
        """
        self.right_click_left_in_desktop_by_attr()
        self.click_wallpaper_in_right_menu_by_image()

    def click_file_name_edit_in_desktop_plugs_by_ui(self):
        """
         点击文件名修改框
        :return:
        """
        pylinuxauto.click(
            *pylinuxauto.find_element_by_ui(
                "文件名称编辑框", appname="", config_path=""
            ).center()
        )

    def double_click_computer_in_desktop_by_image(self):
        """
         双击桌面<计算机>图标
        :return:
        """
        self.double_click_file_in_desktop_by_config("dde-computer.desktop")

    def double_click_diskmanager_in_desktop_by_image(self):
        """
         双击桌面<磁盘管理器>图标
        :return:
        """
        self.double_click_element_in_desktop_by_image("deepin_diskmanager")

    def double_click_downloader_in_desktop_by_image(self):
        """
         双击桌面<下载器>图标
        :return:
        """
        self.double_click_element_in_desktop_by_image("deepin_downloader")

    def double_click_boot_maker_in_desktop_by_image(self):
        """
         双击桌面<启动盘制作工具>图标
        :return:
        """
        self.double_click_element_in_desktop_by_image("deepin_boot_maker")

    def click_computer_in_desktop_by_image(self):
        """
         点击桌面<计算机>图标
        :return:
        """
        self.click_file_in_desktop_by_config("dde-computer.desktop")

    def right_click_computer_in_desktop_by_image(self):
        """
         右键点击计算机桌面图标
        :return:
        """
        try:
            self.right_click_element_in_desktop_by_image("deepin_computer")
        except TemplateElementNotFound:
            self.icon_small_in_desktop_by_right_menu()
            self.right_click_element_in_desktop_by_image("deepin_computer")

    def click_open_computer_in_desktop_by_image(self):
        """
         右键计算机点击打开
        :return:
        """
        self.right_click_file_in_desktop_by_config("dde-computer.desktop")
        pylinuxauto.select_menu(1)

    def click_create_link_computer_in_desktop_by_image(self):
        """
         右键计算机点击创建链接
        :return:
        """
        self.right_click_file_in_desktop_by_config("dde-computer.desktop")
        pylinuxauto.click(*pylinuxauto.find_element_by_ocr("发送到").center())
        self.click_create_link_in_right_menu_by_image()

    def click_attribute_computer_in_desktop_by_image(self):
        """
         右键计算机点击属性
        :return:
        """
        self.right_click_file_in_desktop_by_config("dde-computer.desktop")
        pylinuxauto.reverse_select_menu(1)

    def drag_computer_down_in_desktop_by_image(self):
        """
         拖动计算机图标
        :return:
        """
        locate = self.find_system_desktop_image("deepin_computer")
        pylinuxauto.move_on_and_drag_to(locate, (0, 340))

    def drag_computer_up_in_desktop_by_image(self):
        """
         拖动计算机图标
        :return:
        """
        locate = self.find_system_desktop_image("deepin_computer")
        pylinuxauto.move_on_and_drag_to(locate, (0, -340))

    def close_computer_attribute_in_desktop_by_image(self):
        """
         关闭计算机属性小窗口
        :return:
        """
        pylinuxauto.click(957, 500)
        pylinuxauto.esc()

    def double_click_trash_in_desktop_by_image(self):
        """
         双击桌面<回收站>图标
        :return:
        """
        try:
            self.double_click_element_in_desktop_by_image("recycle", "recycle_file")
        # 如果找不到，尝试恢复大小后再找
        except TemplateElementNotFound:
            self.icon_small_in_desktop_by_right_menu()
            self.double_click_element_in_desktop_by_image("recycle", "recycle_file")

    def close_trash_attribute_in_desktop_by_image(self):
        """
         关闭回收站属性小窗口
        :return:
        """
        _x, _y = self.find_system_desktop_image("recycle_attribute")
        pylinuxauto.click(_x + 134, _y - 122)

    def click_empty_btn_in_dialog_by_attr(self):
        """
         点击确认窗口中的“清空”
        :return:
        """
        pylinuxauto.find_element_by_attr_path("清空").click()

    def right_click_trash_in_desktop_by_image(self):
        """
         右键点击回收站
        :return:
        """
        pylinuxauto.right_click(*self.gettrash_location_by_image())

    def click_trash_in_desktop_by_image(self):
        """
         单机点击回收站
        :return:
        """
        pylinuxauto.click(*self.gettrash_location_by_image())

    def drag_txt_to_trash_on_desktop_by_image(self):
        """
         拖拽txt文件到回收站
        :return:
        """
        self.move_to_txt_on_desktop_by_image()
        self.drag_to_trash_on_desktop_by_image()

    def drag_to_trash_on_desktop_by_image(self):
        """
         拖拽文件到回收站
        :return:
        """
        pylinuxauto.drag_to(*self.gettrash_location_by_image())

    def gettrash_location_by_image(self):
        """
         桌面回收站图标的坐标
        :return:
        """
        return self.find_system_desktop_image("recycle", "recycle_file")

    def get_location_on_desktop_computer_by_image(self):
        """
         桌面计算机图标的坐标
        :return:
        """
        return self.get_file_or_dir_axes_by_config("dde-computer.desktop")

    def right_click_deepin_album_icon_in_desktop_by_image(self):
        """
         在桌面右键相册图标
        :return:
        """
        pylinuxauto.right_click(*self.find_system_desktop_image("deepin_album"))

    def double_click_deepin_album_icon_in_desktop_by_image(self):
        """
         在桌面双击相册图标
        :return:
        """
        pylinuxauto.double_click(*self.find_system_desktop_image("deepin_album"))
        sleep(2)

    def click_open_trash_in_desktop_by_image(self):
        """
         右键回收站点击打开
        :return:
        """
        self.right_click_trash_in_desktop_by_image()
        pylinuxauto.select_menu(1)

    def click_create_link_trash_in_desktop_by_image(self):
        """
         右键回收站点击创建链接
        :return:
        """
        self.right_click_trash_in_desktop_by_image()
        pylinuxauto.reverse_select_menu(2)

    def click_attribute_trash_in_desktop_by_image(self):
        """
         右键回收站点击属性
        :return:
        """
        self.right_click_trash_in_desktop_by_image()
        pylinuxauto.reverse_select_menu(1)

    def drag_trash_down_in_desktop_by_image(self):
        """
         拖动回收站图标
        :return:
        """
        locate = self.gettrash_location_by_image()
        pylinuxauto.move_on_and_drag_to(locate, (0, 340))
        logger.info(f"拖动回收站图标从{locate}至(0, 340)")

    @classmethod
    def create_recursion_dir_by_cmd(cls, path="Desktop", num=4):
        """
         递归生成多个文件夹
        :param path: 路径
        :param num: 生成的文件数
        :return:
        """
        if num == 1:
            os.system(f"mkdir -p ~/{path}/test{num + 1}")
        if num >= 2:
            cmd = "mkdir -p ~/Desktop/test1"
            for i in range(2, num + 1):
                cmd = cmd + f"/test{i}"
            os.system(cmd)

    @classmethod
    def create_long_name_dir_in_desktop_by_cmd(cls):
        """
         在桌面生成超常名字文件夹
        :return:
        """
        os.system(f"mkdir -p ~/Desktop/{'超常名称' * 11}/test")

    @classmethod
    def create_long_name_file_in_desktop_by_cmd(cls):
        """
         在桌面生成超常名字文件
        :return:
        """
        os.system(f"touch  ~/Desktop/{'超常名称' * 11}.txt")

    @classmethod
    def new_files_by_cmd(cls, path="Desktop", num=1):
        """
         生成多个个文件
        :param path: 路径
        :param num: 文件数
        :return:
        """
        for i in range(0, num):
            os.system(f"touch ~/{path}/test{i + 1}.txt")

    @classmethod
    def chmod_dir_in_desktop_by_cmd(cls, permission, dir_name):
        """
         修改桌面文件夹权限
        :param permission: 权限值 例如555,777
        :param dir_name: 文件夹名
        :return:
        """
        os.system(f"chmod -R {permission} ~/Desktop/{dir_name}/")

    @classmethod
    def chmod_file_in_desktop_by_cmd(cls, permission, file_name):
        """
         修改桌面文件权限
        :param permission: 权限值 例如555,777
        :param file_name: 文件名
        :return:
        """
        os.system(f"chmod {permission} ~/Desktop/{file_name}")

    def paste_file_in_desktop_by_right_menu(self):
        """
         在桌面粘贴文件
        :return:
        """
        DdeDesktopPublicMethod.winleft_d()
        sleep(1)
        DdeDesktopPublicMethod.right_click(100, 300)
        self.click_paste_in_right_menu_by_image()

    @classmethod
    def new_dir_in_desktop_by_cmd(cls, *names):
        """
         在桌面上新建文件夹
        :param names: 文件夹名列表
        :return:
        """
        if names:
            for name in names:
                os.system(f"mkdir ~/Desktop/{name} | true")
        pylinuxauto.f5()
        sleep(1)

    @classmethod
    def new_file_in_desktop_by_cmd(cls, *names):
        """
         在桌面上新建txt
        :param names: 文件名列表
        :return:
        """
        if names:
            for name in names:
                os.system(f"touch ~/Desktop/{name}")
        pylinuxauto.f5()
        sleep(1)

    def colleagues_create_different_types_of_files(self):
        """
         在桌面上右键新建ppt,execl,doc,txt文件
        :return:
        """
        self.click_zero_in_desktop_by_attr()
        pylinuxauto.right_click()
        self.click_new_document_in_right_menu_by_image()
        self.click_word_in_right_menu_by_image()
        self.click_zero_in_desktop_by_attr()
        pylinuxauto.right_click()
        self.click_new_document_in_right_menu_by_image()
        self.click_ppt_in_right_menu_by_image()
        self.click_zero_in_desktop_by_attr()
        pylinuxauto.right_click()
        self.click_new_document_in_right_menu_by_image()
        self.click_excel_in_right_menu_by_image()
        self.click_zero_in_desktop_by_attr()
        pylinuxauto.right_click()
        self.click_new_document_in_right_menu_by_image()
        self.click_txt_in_right_menu_by_image()
        pylinuxauto.f5()

    @staticmethod
    def copy_music_and_rename_to_desktop_by_cmd(rename):
        """
         复制一首音乐到桌面，并重命名
        :param rename:
        :return:
        """
        shutil.copyfile(
            "/usr/share/music/bensound-sunny.mp3",
            f"/home/{config.USERNAME}/Desktop/{rename}.mp3",
        )

    @staticmethod
    def copy_movie_to_desktop_by_cmd():
        """
         复制一部视频到桌面
        :return:
        """
        shutil.copyfile(
            "/usr/share/dde-introduction/demo.mp4",
            f"/home/{config.USERNAME}/Desktop/demo.mp4",
        )

    @staticmethod
    def copy_jpg_and_rename_to_desktop_by_cmd(rename):
        """
         复制一张jpg的图片到桌面，并重命名
        :param rename: 新名字
        :return:
        """
        shutil.copyfile(
            "/usr/share/wallpapers/deepin/abc-123.jpg",
            f"/home/{config.USERNAME}/Desktop/{rename}.jpg",
        )

    @classmethod
    def desktop_wallpapers_de1_custom_picture(cls):
        """
         删除自定义壁纸目录的图片
         地址：.config/deepin/dde-daemon/appearance/custom-wallpapers
        :return:
        """
        os.system("rm -rf  ~/.config/deepin/dde-daemon/appearance/custom-wallpapers")

    @staticmethod
    def write_txt_in_desktop_by_cmd(text="统信成都测试部", name="测试文档"):
        """
         桌面新建txt并写入文本
        :param text: 文件内容
        :param name: 文件名
        :return:
        """
        with open(
            f"/home/{config.USERNAME}/Desktop/{name}.txt", "w", encoding="utf-8"
        ) as file:
            file.write(text)

    @staticmethod
    def write_txt_in_desktop_folder_by_cmd(text="统信成都测试部", name="测试文档"):
        """
         桌面新建文件夹内新建txt并写入
        :param text: 文件内容
        :param name: 文件名
        :return:
        """
        _path = os.path.expanduser("~/Desktop/新建文件夹")
        if not os.path.exists(_path):
            os.makedirs(_path)

        if "." not in name:
            _file_path = f"{_path}/{name}.txt"
        else:
            _file_path = f"{_path}/{name}"
        with open(_file_path, "w+", encoding="utf-8") as file:
            file.write(text)

    def right_click_txt_on_desktop_by_image(self):
        """
         右键桌面txt文件
        :return:
        """
        pylinuxauto.right_click(*self.find_system_desktop_image("txt"))
        sleep(1)

    @classmethod
    def get_file_from_ftp(cls, file_name, path="Desktop"):
        """
         从ftp下载psd格式图片
        :param file_name:
        :param path:
        :return:
        """
        os.system(
            f"wget -P  /home/{config.USERNAME}/{path} "
            f"ftp://{config.FTP_IP}/uploads/dde-file-manager/"
            f"automated_test_material/desktop/{file_name} > /dev/null 2&>1"
        )

    def click_txt_on_desktop_by_image(self):
        """
         左键桌面txt文件
        :return:
        """
        self.click_element_in_desktop_by_image("txt")

    def double_click_txt_on_desktop_by_image(self):
        """
         双击桌面txt文件
        :return:
        """
        self.double_click_element_in_desktop_by_image("txt")

    def move_to_txt_on_desktop_by_image(self):
        """
         左移动到桌面txt文件
        :return:
        """
        self.move_to_element_in_desktop_by_image("txt")

    def right_click_folder_in_desktop_by_image(self):
        """
         右键点击文件夹
        :return:
        """
        self.right_click_element_in_desktop_by_image("folder")

    def move_to_folder_in_desktop_by_image(self):
        """
         移动到文件夹
        :return:
        """
        self.move_to_element_in_desktop_by_image("folder")

    def click_folder_in_desktop_by_image(self):
        """
         左键点击文件夹
        :return:
        """
        self.click_element_in_desktop_by_image("folder")

    def double_click_folder_in_desktop_by_image(self):
        """
         双击点击文件夹
        :return:
        """
        self.double_click_element_in_desktop_by_image("folder")

    def double_click_dde_file_manager_icon_in_desktop_by_image(self):
        """
         在桌面双击文管图标
        :return:
        """
        pylinuxauto.double_click(*self.get_dde_file_manager_location_by_image())
        sleep(2)

    def right_click_zip_file_in_desktop_by_image(self):
        """
         右键点击桌面zip压缩包文件
        :return:
        """
        self.right_click_element_in_desktop_by_image("zip")

    def click_only_set_wallpaper_to_desktop_by_image(self):
        """
         点击屏保页面<仅设置桌面>
        :return:
        """
        self.click_element_in_desktop_by_image("only_set_wallpaper_to_desktop")

    def click_display_in_dialog_by_attr(self):
        """
         点击 弹窗中的 “显示“
        :return:
        """
        pylinuxauto.find_element_by_attr_path("$//显示").click()

    def double_click_zip_on_desktop_by_image(self):
        """
         双击打开zip文件
        :return:
        """
        self.double_click_element_in_desktop_by_image("zip")

    @classmethod
    def drag_txt_to_desktop_zip_by_image(cls):
        """
         拖拽txt到zip文件中
        :return:
        """
        folder_position = DdeDesktopPublicMethod.find_system_desktop_image("txt")
        zip_position = DdeDesktopPublicMethod.find_system_desktop_image("zip")
        pylinuxauto.click(*folder_position)
        sleep(1)
        pylinuxauto.drag_to(*zip_position)

    def double_click_no_read_pic_in_desktop_by_img(self):
        """
         桌面双击无读写权限的文件
        :return:
        """
        self.double_click_element_in_desktop_by_image("no_read_pic")

    @classmethod
    def send_icon_to_desktop_by_cmd(cls, app):
        """
         发送图标到桌面
        :param app:
        :return:
        """
        os.system(f"cp /usr/share/applications/{app}.desktop ~/Desktop/")

    def focus_desktop(self):
        """
         聚焦桌面
        :return:
        """
        self.ui.focus_windows("dde-desktop")

    def get_dir_location(self):
        """
         返回桌面文件夹坐标
        :return:
        """
        return self.find_system_desktop_image("folder")

    def get_screensaver_location(self):
        """
         返回屏保界面的屏保按钮坐标
        :return:
        """
        return self.find_system_desktop_image("screensaver")

    def get_setscreensaver_location(self):
        """
         返回屏保界面的设置屏保按钮坐标
        :return:
        """
        return self.find_system_desktop_image("set_screensaver")

    def get_execl_location(self):
        """
         返回桌面execl文件坐标
        :return:
        """
        return self.find_system_desktop_image("execl")

    def get_doc_location(self):
        """
         返回桌面doc文件坐标
        :return:
        """
        return self.find_system_desktop_image("doc")

    def get_ppt_location(self):
        """
         返回桌面ppt文件坐标
        :return:
        """
        return self.find_system_desktop_image("ppt")

    def get_txt_location(self):
        """
         返回桌面txt文件坐标
        :return:
        """
        return self.find_system_desktop_image("txt")

    def get_dde_file_manager_location_by_image(self):
        """
         返回桌面文管文件坐标
        :return:
        """
        return self.find_system_desktop_image("dde_file_manager")

    def get_movie_file_location(self):
        """
         返回桌面视频文件栏坐标
        :return:
        """
        return self.find_system_desktop_image("movie_file")

    # def set_default_workspace(self):
    #     """
    #      在桌面恢复默认工作区
    #     此方法不在提供，请在子项目中重写此方法
    #     :return:
    #     """
    #     # 找寻桌面窗口ID
    #     desktop_id = self.ui.get_windows_id("dde-desktop")
    #     # 聚焦桌面
    #     cmd_f = f"xdotool windowactivate {desktop_id[0]}"
    #     # 使用快捷键切换工作区
    #     cmd_k = "xdotool key super+Right"
    #     bus = DbusCommonMethod()
    #     # 获取总数工作区
    #     workspace_count = bus.get_workspace_count()
    #     # 获取当前工作区
    #     current_workspace = bus.get_current_workspace()
    #     sleep(2)
    #     # 执行聚焦桌面
    #     Cmd.run(cmd_f, interrupt=False, print_log=False, command_log=False)
    #     for _ in range(0, int(workspace_count - current_workspace + 1)):
    #         sleep(1)
    #         # 执行快捷键切换工作区
    #         Cmd.run(
    #             cmd_k, interrupt=False, print_log=False, command_log=False
    #         )

    def double_click_deepin_music_icon_on_desktop_by_image(self):
        """
         桌面双击音乐图标
        :return:
        """
        self.double_click_element_in_desktop_by_image("deepin_music")

    def right_click_deepin_music_on_desktop_by_image(self):
        """
         右键点击音乐图标
        :return:
        """
        self.right_click_element_in_desktop_by_image("deepin_music")

    def double_click_camera_on_desktop_by_image(self):
        """
         桌面双击相机图标
        :return:
        """
        self.double_click_element_in_desktop_by_image("deepin_camera")

    def double_click_deepin_movie_on_desktop_by_image(self):
        """
         桌面双击相机图标
        :return:
        """
        self.double_click_element_in_desktop_by_image("deepin_movie")

    def double_click_deepin_screen_recorder_on_desktop_by_image(self):
        """
         桌面双击截图录屏图标
        :return:
        """
        self.double_click_element_in_desktop_by_image("deepin_screen_recorder")

    def right_click_deepin_screen_recorder_on_desktop_by_image(self):
        """
         桌面右键截图录屏图标
        :return:
        """
        self.right_click_element_in_desktop_by_image("deepin_screen_recorder")

    def click_deepin_screen_recorder_on_desktop_by_image(self):
        """
         桌面单击截图录屏图标
        :return:
        """
        self.click_element_in_desktop_by_image("deepin_screen_recorder")

    def get_screen_name_by_dbus(self):
        """
         获取当前显示器的名字
        :return:
        """
        return self.display_dbus().get_session_properties_value("Primary")

    def setting_default_wallpaper_by_dbus(self):
        """
         设置壁纸为默认壁纸
        :return:
        """
        self.desktop_dbus().session_object_methods().SetMonitorBackground(
            str(self.get_screen_name_by_dbus()),
            (
                "/usr/share/wallpapers/deepin/desktop"
                f".{'bmp' if config.SYS_ARCH == config.ArchName.mips else 'jpg'}"
            ),
        )

    @classmethod
    def new_folder_in_desktop_by_cmd(cls, text=None):
        """
         shell在桌面新建文件夹
        :param text: 文件夹名
        :return:
        """
        os.system(
            f"mkdir /home/{config.USERNAME}/Desktop/{text if text else '新建文件夹'}"
        )

    @staticmethod
    def delete_computer_and_trash_icon_in_desktop_by_cmd():
        """
         删除桌面的计算机和回收站图标
        :return:
        """
        try:
            for i in ["dde-computer.desktop", "dde-trash.desktop"]:
                shutil.move(
                    f"/home/{config.USERNAME}/Desktop/{i}",
                    f"/home/{config.USERNAME}/Pictures/{i}",
                )
        except FileNotFoundError:
            pass

    @classmethod
    def recovery_computer_and_trash_icon_by_cmd(cls):
        """
         恢复桌面的计算机和回收站图标
        :return:
        """
        for i in ["dde-computer.desktop", "dde-trash.desktop"]:
            Cmd.run(
                f"cp /usr/share/applications/{i} /home/{config.USERNAME}/Desktop/",
                interrupt=False,
                print_log=False,
                command_log=False,
            )

    @classmethod
    def new_txt_in_desktop_by_cmd(cls, text=None):
        """
         shell在桌面新建txt
        :param text: 文件名
        :return:
        """
        os.system(
            f"touch /home/{config.USERNAME}/Desktop/{text if text else '新建文本'}.txt"
        )
        pylinuxauto.f5()

    @classmethod
    def new_doc_in_desktop_by_cmd(cls, text=None, size=1):
        """
         shell在桌面新建doc
        :param text: 文件名
        :param size: 文件大小
        :return:
        """
        os.system(
            f"dd if=/dev/zero of=/home/{config.USERNAME}/Desktop/"
            f"{text if text else '新建Word文档'}.doc bs={size}M count=1"
        )

    @classmethod
    def clean_trash_by_cmd(cls):
        """
         清空回收站
        :return:
        """
        os.system(f"rm -rf /home/{config.USERNAME}/.local/share/Trash/*")

    def double_click_file_in_desktop_plugs_right_view_by_attr(self, element):
        """
         双击桌面目录元素
        :param element: 文件名
        :return:
        """
        pylinuxauto.find_element_by_attr_path(f"$//file_view/{element}").double_click()

    def click_file_in_desktop_plugs_right_view_by_attr(self, element):
        """
         单击桌面目录元素
        :param element: 文件名
        :return:
        """
        pylinuxauto.find_element_by_attr_path(f"$//file_view/{element}").click()

    def click_delete_btn_in_dialog_by_attr(self):
        """点击确认窗口中的“确认删除”"""
        try:
            pylinuxauto.find_element_by_attr_path("删 除").click()
        except ElementNotFound:
            pylinuxauto.find_element_by_attr_path("删除").click()

    def click_replace_btn_in_dialog_by_attr(self):
        """点击确认窗口中的“替换”"""
        try:
            pylinuxauto.find_element_by_attr_path("替 换").click()
        except ElementNotFound:
            pylinuxauto.find_element_by_attr_path("替换").click()

    @classmethod
    def build_new_txt_in_desktop_by_cmd(cls, *names):
        """在桌面上新建一个txt"""
        if names:
            for name in names:
                Cmd.run(f"touch ~/Desktop/{name}.txt")
        sleep(0.5)

    @classmethod
    def create_zip_file_in_desktop_by_cmd(cls):
        """
        创建压缩文件
        :return:
        """
        for _i in range(0, 3):
            cls.build_new_txt_in_desktop_by_cmd(f"{_i + 1}.zip")
        Cmd.run(r"cd ~/Desktop &&zip auto.zip *.txt && rm *.txt")


if __name__ == "__main__":
    DdeDesktopPublicMethod().click_open_computer_in_desktop_by_image()
