#!/usr/bin/env python3
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
from youqu3.gui import pylinuxauto
from youqu3 import setting
from youqu3 import logger
from youqu3 import log
from youqu3 import sleep
import os

from youqu3.dbus import Dbus
from youqu3 import sleep
from youqu3.exceptions import TemplateElementNotFound
from youqu3.exceptions import ElementNotFound


class _DdeControlCenterPublicMethod:
    """
    系统控制中心基类
    """

    APP_NAME = "dde-control-center"
    DESC = "/usr/bin/dde-control-center"

    def __init__(self, check_start=True):
        kwargs = {}
        kwargs["name"] = self.APP_NAME
        kwargs["description"] = self.DESC
        kwargs["check_start"] = check_start
        kwargs["config_path"] = config.UI_INI_PATH

    def click_and_input_search_in_control_center_by_attr(self, text, press_enter=True):
        """
         在控制中心中点击搜索，输入，然后搜索
        :param text: 输入的文本
        :param press_enter: 输入内容后是否按下 Enter
        :return:
        """
        pylinuxauto.find_element_by_attr_path("DMainWindow").child(
            "Editable_searchmodulelineedit"
        ).click()
        sleep(1)
        pylinuxauto.input_message(text)
        sleep(1)
        if press_enter:
            pylinuxauto.enter()
            sleep(1)

    @classmethod
    def find_control_center_image(cls, *elements, rate=0.9):
        """
         通过图片查找元素坐标
        :param elements:
        :return:
        """
        element = tuple(map(lambda x: f"{config.PIC_RES_PATH}/{x}", elements))
        return pylinuxauto.find_element_by_image(*element, rate=rate).center().center()


@log
class DdeControlCenterPublicMethod(_DdeControlCenterPublicMethod):
    """
    控制中心业务层方法
    """

    # ============================= 控制中心 顶部操作 =============================

    def click_settings_in_control_center_by_attr(self):
        """
         点击控制中心右上角设置按钮
        :return:
        """
        pylinuxauto.find_element_by_attr_path("DMainWindow").child(
            "Btn_dtitlebardwindowoptionbutton"
        ).click()
        sleep(0.5)

    def click_settings_help_in_control_center_by_attr(self):
        """
         点击控制中心右上角设置-帮助按钮
        :return:
        """
        self.click_settings_in_control_center_by_attr()
        pylinuxauto.click(*pylinuxauto.find_element_by_ocr("帮助").center())
        sleep(2)

    # ============================= 控制中心 键盘和语言->输入法操作 =============================

    def search_and_click_keyboards_and_languages_in_control_center_by_attr(self):
        """
         在控制中心中进入键盘和语言
        :return:
        """
        self.click_and_input_search_in_control_center_by_attr("键盘和语言")

    def click_input_method_in_control_center_by_attr(self):
        """
         在控制中心中点击输入法
        :return:
        """
        self.search_and_click_keyboards_and_languages_in_control_center_by_attr()
        pylinuxauto.find_element_by_attr_path("DMainWindow").child("输入法").click()
        sleep(1)

    @classmethod
    def set_screen_orientation_to_standard_by_dbus(cls):
        """
        设置屏幕方向为：标准
        """

        dbus_object = Dbus(
            "com.deepin.daemon.Display",
            "/com/deepin/daemon/Display",
            "com.deepin.daemon.Display",
        )
        monitor_path = dbus_object.get_session_properties_value("Monitors")
        os.system(
            f"dbus-send --session --print-reply --dest=com.deepin.daemon.Display {monitor_path[0]} com.deepin"
            f".daemon.Display.Monitor.SetRotation uint16:1"
        )
        os.system(
            "dbus-send --session --print-reply --dest=com.deepin.daemon.Display /com/deepin/daemon/Display "
            "com.deepin.daemon.Display.ApplyChanges"
        )
        sleep(5)

    @classmethod
    def set_standard_font(cls):
        """
        设置标准字体为：思源黑体
        """
        #
        os.system(
            "dbus-send --session --type=method_call --print-reply --dest=com.deepin.daemon.Appearance /com/deepin/daemon/Appearance com.deepin.daemon.Appearance.Set string:standardfont string:'Source Han Sans SC'"
        )
        sleep(3)

    @classmethod
    def init_environment(cls):
        """
        此方法主要用于执行用例前进行环境初始化
        且当前方法只适用于接口设置，不适用于UI设置
        """
        # 设置标准字体为：思源黑体
        cls.set_standard_font()
        # 设置屏幕方向为：标准
        cls.set_screen_orientation_to_standard_by_dbus()


if __name__ == "__main__":
    DdeControlCenterPublicMethod().click_input_method_in_control_center_by_attr()
