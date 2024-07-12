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
from youqu3 import log
from youqu3.exceptions import TemplateElementNotFound
from youqu3.exceptions import ElementNotFound


@log
class DdeLauncherPublicMethod:
    """启动器的方法类"""

    APP_NAME = "dde-launcher"
    DESC = "/usr/bin/dde-launcher"

    def __init__(self):
        kwargs = {}
        kwargs["name"] = self.APP_NAME
        kwargs["description"] = self.DESC
        kwargs["check_start"] = True
        kwargs["config_path"] = config.UI_INI_PATH

    def click_and_input_search_edit_in_launcher_by_attr(self, text):
        """
         在启动器中点击搜索，然后输入
        :param text: 输入的文本
        :return:
        """
        try:
            pylinuxauto.find_element_by_attr_path("Form_windowedsearcheredit").click()
        except ElementNotFound:
            pylinuxauto.find_element_by_attr_path("Form_searcheredit").click()
        sleep(0.5)
        pylinuxauto.input_message(text)
        sleep(0.5)

    def click_search_edit_on_launcher_by_attr(self):
        """
         移动到启动器上
        :return:
        """
        try:
            pylinuxauto.find_element_by_attr_path("Form_windowedsearcheredit").click()
        except ElementNotFound:
            pylinuxauto.find_element_by_attr_path("Form_searcheredit").click()

    def click_app_in_lancher_by_attr(self, app_name):
        """
         在启动器中点击应用
        :param app_name: 应用名
        :return:
        """
        pylinuxauto.find_element_by_attr_path(f"{app_name}").click()

    def double_click_app_in_lancher_by_attr(self, app_name):
        """
         在启动器中双击应用
        :param app_name: 应用名
        :return:
        """
        pylinuxauto.find_element_by_attr_path(f"{app_name}").double_click()

    def right_click_app_in_lancher_by_attr(self, app_name):
        """
         在启动器中右键点击应用
        :param app_name: 应用名
        :return:
        """
        pylinuxauto.find_element_by_attr_path(f"{app_name}").click(3)

    def select_music_right_menu_in_launcher(self, num):
        """
         在启动器中选择音乐的右键菜单
        :param num: 菜单的第几项
        :return:
        """
        self.click_and_input_search_edit_in_launcher_by_attr("音乐")
        sleep(1)
        self.right_click_app_in_lancher_by_attr("音乐")
        pylinuxauto.select_menu(num)
        sleep(1)

    def click_music_in_launcher_by_attr(self):
        """
         在启动器中点击音乐
        :return:
        """
        self.click_app_in_lancher_by_attr("音乐")

    def click_open_file_manager_in_launcher_by_attr(self):
        """
         在启动器中点击文管
        :return:
        """
        self.click_and_input_search_edit_in_launcher_by_attr("文件管理器")
        self.click_app_in_lancher_by_attr("文件管理器")

    def click_screen_recorder_in_launcher_by_attr(self):
        """
         在启动器中点击截图录屏
        :return:
        """
        self.click_and_input_search_edit_in_launcher_by_attr("截图录屏")
        self.click_app_in_lancher_by_attr("截图录屏")

    def send_file_manager_to_desktop_in_launcher_by_attr(self):
        """
         在launcher中发送到桌面
        :return:
        """
        self.click_and_input_search_edit_in_launcher_by_attr("文件管理器")
        self.right_click_app_in_lancher_by_attr("文件管理器")
        pylinuxauto.select_menu(2)
        sleep(1)

    def open_file_manager_in_launcher_by_right_menu(self):
        """
         在启动器中右键打开应用
        :return:
        """
        self.click_and_input_search_edit_in_launcher_by_attr("文件管理器")
        self.right_click_app_in_lancher_by_attr("文件管理器")
        pylinuxauto.select_menu(1)
        sleep(1)

    # =============================磁盘管理器 操作=======================================
    def open_diskmanager_in_launcher_by_attr(self):
        """
         在启动器中打开 磁盘管理器
        :return:
        """

        DISKMANAGER = "磁盘管理器"
        self.click_and_input_search_edit_in_launcher_by_attr(DISKMANAGER)
        self.click_app_in_lancher_by_attr(DISKMANAGER)
        sleep(1)
        self.enter_user_password()

    def send_diskmanager_to_dock_in_launcher_by_attr(self):
        """
         在启动器中右键发送 磁盘管理器 到任务栏
        :return:
        """

        DISKMANAGER = "磁盘管理器"
        self.click_and_input_search_edit_in_launcher_by_attr(DISKMANAGER)
        self.right_click_app_in_lancher_by_attr(DISKMANAGER)
        try:
            pylinuxauto.click(*pylinuxauto.find_element_by_ocr("发送到任务栏").center())
        except TypeError:
            # 如果没有"发送到任务栏"，大概率是已经发送到任务栏了，关闭启动器
            pylinuxauto.esc()

    def send_diskmanager_to_desktop_in_launcher_by_attr(self):
        """
         在启动器中右键发送 磁盘管理器 到桌面
        :return:
        """

        DISKMANAGER = "磁盘管理器"
        self.click_and_input_search_edit_in_launcher_by_attr(DISKMANAGER)
        self.right_click_app_in_lancher_by_attr(DISKMANAGER)
        try:
            pylinuxauto.click(*pylinuxauto.find_element_by_ocr("发送到桌面").center())
        except TypeError:
            # 如果没有"发送到任务栏"，大概率是已经发送到任务栏了，退出启动器
            pylinuxauto.esc()

    def right_click_from_desktop_move_diskmanager_in_launcher_by_attr(self):
        """
         在启动器中右键从桌面移除 磁盘管理器
        :return:
        """

        DISKMANAGER = "磁盘管理器"
        self.click_and_input_search_edit_in_launcher_by_attr(DISKMANAGER)
        self.right_click_app_in_lancher_by_attr(DISKMANAGER)
        sleep(0.5)
        try:
            pylinuxauto.click(*pylinuxauto.find_element_by_ocr("从桌面上移除").center())
        except TypeError:
            # 如果没有"从桌面上移除"，大概率是已经移除了
            pass

    def right_click_open_diskmanager_in_launcher_by_right_menu(self):
        """
         在启动器中右键打开 磁盘管理器
        :return:
        """

        DISKMANAGER = "磁盘管理器"
        self.click_and_input_search_edit_in_launcher_by_attr(DISKMANAGER)
        self.right_click_app_in_lancher_by_attr(DISKMANAGER)
        pylinuxauto.select_menu(1)
        sleep(1)
        self.enter_user_password()

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

    # =============================下载器 操作=======================================

    def click_downloader_in_launcher_by_attr(self):
        """
         在启动器中左键单击打开 下载器
        :return:
        """

        downloader = "下载器"
        self.click_and_input_search_edit_in_launcher_by_attr(downloader)
        self.click_app_in_lancher_by_attr(downloader)
        sleep(1)

    def send_downloader_to_dock_in_launcher_by_attr(self):
        """
         在启动器中右键发送 下载器 到任务栏
        :return:
        """

        downloader = "下载器"
        self.click_and_input_search_edit_in_launcher_by_attr(downloader)
        self.right_click_app_in_lancher_by_attr(downloader)
        try:
            pylinuxauto.click(*pylinuxauto.find_element_by_ocr("发送到任务栏").center())
        except TypeError:
            # 如果没有"发送到任务栏"，大概率是已经发送到任务栏了，关闭启动器
            pylinuxauto.esc()
        sleep(1)

    def send_downloader_to_desktop_in_launcher_by_attr(self):
        """
         在启动器中右键发送 下载器 到桌面
        :return:
        """

        downloader = "下载器"
        self.click_and_input_search_edit_in_launcher_by_attr(downloader)
        self.right_click_app_in_lancher_by_attr(downloader)
        try:
            pylinuxauto.click(*pylinuxauto.find_element_by_ocr("发送到桌面").center())
        except TypeError:
            # 如果没有"发送到任务栏"，大概率是已经发送到任务栏了，退出启动器
            pylinuxauto.esc()
        sleep(1)

    def right_click_from_desktop_move_downloader_in_launcher_by_attr(self):
        """
         在启动器中右键从桌面移除 下载器
        :return:
        """

        downloader = "下载器"
        self.click_and_input_search_edit_in_launcher_by_attr(downloader)
        self.right_click_app_in_lancher_by_attr(downloader)
        sleep(0.5)
        try:
            pylinuxauto.click(*pylinuxauto.find_element_by_ocr("从桌面上移除").center())
        except TypeError:
            # 如果没有"从桌面上移除"，大概率是已经移除了
            pass

    def right_click_open_downloader_in_launcher_by_right_menu(self):
        """
         在启动器中右键打开 下载器
        :return:
        """

        downloader = "下载器"
        self.click_and_input_search_edit_in_launcher_by_attr(downloader)
        self.right_click_app_in_lancher_by_attr(downloader)
        pylinuxauto.select_menu(1)
        sleep(1)

    def enter_open_downloader_in_launcher_by_right_menu(self):
        """
         在启动器中回车打开 下载器
        :return:
        """

        downloader = "下载器"
        self.click_and_input_search_edit_in_launcher_by_attr(downloader)
        pylinuxauto.enter()
        sleep(1)

    # =============================启动盘制作工具 操作=======================================

    def click_boot_maker_in_launcher_by_attr(self):
        """
         在启动器中左键单击打开 启动盘制作工具
        :return:
        """

        downloader = "启动盘制作工具"
        self.click_and_input_search_edit_in_launcher_by_attr(downloader)
        self.click_app_in_lancher_by_attr(downloader)
        sleep(1)

    def send_boot_maker_to_desktop_in_launcher_by_attr(self):
        """
         在启动器中右键发送 启动盘制作工具 到桌面
        :return:
        """

        downloader = "启动盘制作工具"
        self.click_and_input_search_edit_in_launcher_by_attr(downloader)
        self.right_click_app_in_lancher_by_attr(downloader)
        try:
            pylinuxauto.click(*pylinuxauto.find_element_by_ocr("发送到桌面").center())
        except TypeError:
            # 如果没有"发送到任务栏"，大概率是已经发送到任务栏了，退出启动器
            pylinuxauto.esc()
        sleep(1)

    # =============================控制中心 操作=======================================

    def click_control_center_in_launcher_by_attr(self):
        """
         在启动器中左键单击打开 控制中心
        :return:
        """

        downloader = "控制中心"
        self.click_and_input_search_edit_in_launcher_by_attr(downloader)
        self.click_app_in_lancher_by_attr(downloader)
        sleep(1)


if __name__ == "__main__":
    # DdeLauncherPublicMethod().open_downloader_in_launcher_by_attr()
    DdeLauncherPublicMethod().click_open_file_manager_in_launcher_by_attr()
