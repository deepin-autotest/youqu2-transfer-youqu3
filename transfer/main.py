import os
import re

from transfer.mk_method_names import mk_method_names


class Transfer:

    def __init__(self, project_path):
        self.project_path = project_path
        self.project_name = project_path.split('/')[-1]
        self.new_project_name = f"youqu3_{self.project_name}"

    def new_project(self):
        if os.path.exists(self.new_project_name):
            os.system(f"rm -rf {self.new_project_name}")
        os.system(f"cp -r {self.project_path} {self.new_project_name}")
        os.system(f"cp -r public {self.new_project_name}/widget/public")
        os.system(f"cp --force tpl/* {self.new_project_name}/")
        os.system(f"cp --force tpl/.env {self.new_project_name}/.env")
        os.system(f"rm -rf {self.new_project_name}/.git")
        print(f"######### {self.new_project_name} ##########")

    def rename_dir_file(self):
        for root, dirs, files in os.walk(self.new_project_name):
            for dir in dirs:
                if "widget" in dir:
                    new_dir = dir.replace("widget", "method")
                    os.rename(os.path.join(root, dir), os.path.join(root, new_dir))
        for root, dirs, files in os.walk(self.new_project_name):
            for file in files:
                if "widget" in file:
                    new_file = file.replace("widget", "method")
                    os.rename(os.path.join(root, file), os.path.join(root, new_file))

    def transfer_code(self):
        for root, dirs, files in os.walk(self.new_project_name):
            for file in files:
                if not file.endswith(".py"):
                    continue

                print(os.path.join(root, file))
                flag = False
                with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                    lines = f.readlines()

                new_lines = []
                import_index = None
                for index, line in enumerate(lines):
                    if line.startswith(("from", "import")):
                        import_index = index

                        if not flag:
                            new_lines.insert(import_index, "from method.public.dde_desktop_public_method import DdeDesktopPublicMethod\n")
                            new_lines.insert(import_index, "from method.public.dde_dock_public_method import DdeDockPublicMethod\n")
                            new_lines.insert(import_index, "from method.public.right_menu_public_method import RightMenuPublicMethod\n")
                            new_lines.insert(import_index, "from method.public.dde_launcher_public_method import DdeLauncherPublicMethod\n")
                            new_lines.insert(import_index, "from method.public.dde_control_center_public_method import DdeControlCenterPublicMethod\n")
                            new_lines.insert(import_index, "from youqu3.cmd import Cmd\n")
                            new_lines.insert(import_index, "from youqu3.gui import pylinuxauto\n")
                            new_lines.insert(import_index, "from youqu3 import sleep\n")
                            new_lines.insert(import_index, "from youqu3 import log\n")
                            new_lines.insert(import_index, "from youqu3 import logger\n")
                            new_lines.insert(import_index, "from youqu3 import setting\n")
                            if file != "config.py":
                                new_lines.insert(import_index, "from config import config\n")
                            flag = True

                    if line.startswith((
                            "from public",
                            "# pylint: disable",
                            "from src import Src",
                            "from src.button_center import ButtonCenter",
                            "from src.dogtail_utils import DogtailUtils",
                            "from src import OCR",
                            "from setting.globalconfig import GlobalConfig",
                            "from src.mouse_key import MouseKey",
                            "from setting.globalconfig import GetCfg",
                            "    DdeControlCenterPublicMethod,",
                    )):
                        ...
                    elif line in (
                            ")\n",
                    ):
                        ...
                    else:
                        line = self._replace(line)
                        new_lines.append(line)

                with open(os.path.join(root, file), "w", encoding="utf-8") as f:
                    f.writelines(new_lines)

    def _replace(self, line):
        line = line.replace(f"apps.{self.project_name}.", "")
        line = line.replace("widget", "method")
        line = line.replace("Widget", "Method")
        line = line.replace("Method(Src)", "Method(Cmd)")
        line = line.replace("from src", "from youqu3")
        line = line.replace("from youqu3.depends.dogtail", "from pylinuxauto.attr.dogtail")
        line = line.replace("from youqu3 import ElementNotFound", "from youqu3.exceptions import ElementNotFound")
        line = line.replace("from youqu3 import TemplateElementNotFound", "from youqu3.exceptions import TemplateElementNotFound")
        line = line.replace("from youqu3.cmdctl import CmdCtl", "from youqu3.cmd import Cmd")
        line = line.replace("CmdCtl", "Cmd")
        line = line.replace("from src.filectl import FileCtl", "from youqu3.file import FileCtl")
        line = line.replace("FileCtl", "File")
        line = line.replace("filectl", "file")
        line = line.replace("from setting.globalconfig import _GlobalConfig", "from youqu3._setting._setting import _Setting")
        line = line.replace("_GlobalConfig", "_Setting")
        line = line.replace("from youqu3.dbus_utils import DbusUtils", "from youqu3.dbus import Dbus")
        line = line.replace("Src.run_cmd(", "Cmd.run(")
        line = line.replace("run_cmd(", "run(")
        line = line.replace("self.run(", "Cmd.run(")
        line = line.replace("cls.run(", "Cmd.run(")
        line = line.replace("out_debug_flag=False", "print_log=False")
        line = line.replace("from youqu3 import AssertCommon", "from youqu3.assertx import Assert")
        line = line.replace("from youqu3.assert_common import AssertCommon", "from youqu3.assertx import Assert")
        line = line.replace("AssertCommon", "Assert")
        line = line.replace("DbusUtils", "Dbus")
        line = line.replace("from youqu3 import Dbus", "from youqu3.dbus import Dbus")
        line = line.replace("Src.__init__(self, **kwargs)", "")
        line = line.replace("Src, ", "")
        line = line.replace("Src", "")
        line = line.replace(", ShortCut", "")
        line = line.replace("DdeDesktopPublicMethod,", "")
        line = line.replace("RightMenuPublicMethod,", "")
        line = line.replace("from youqu3.custom_exception", "from youqu3.exceptions")
        line = line.replace("GlobalConfig.", "setting.")
        line = line.replace("Config = _Config()", "config = _Config()")
        line = line.replace("Config.", "config.")
        line = line.replace("from config import Config", "from config import config")
        line = line.replace(").doubleClick()", ").double_click()")
        line = line.replace("self.assert_process_status(True,", "self.assert_process_exist(")
        line = line.replace("self.assert_process_status(False,", "self.assert_process_not_exist(")

        # ocr
        if re.findall(r'(= .*?\.ocr\()', line) and not line.endswith(".center()\n"):
            line = re.sub(r'= .*?\.ocr\(', "= pylinuxauto.find_element_by_ocr(", line)
            line = line.replace("\n", ".center()\n")
        if re.findall(r'(\*.*?\.ocr\()', line) and not line.endswith(".center()\n"):
            line = re.sub(r'\*.*?\.ocr\(', "*pylinuxauto.find_element_by_ocr(", line)
            line = line.replace(")\n", ".center())\n")
        if re.findall(r"return pylinuxauto.find_element_by_ocr", line):
            line = line.replace("\n", ".center()\n")
        if re.findall(r"[a-zA-Z]+\.ocr\(", line):
            line = re.sub("[a-zA-Z]+\.ocr\(", "pylinuxauto.find_element_by_ocr(", line)
            if line.endswith(":"):
                line = line.replace("):", ").result:")
        # dog
        if re.findall(r'= .*?\.dog\.element_center\(', line):
            line = re.sub(r'= .*?\.dog\.element_center\(', "= pylinuxauto.find_element_by_attr_path(", line)
            line = line.replace("\n", ".center()\n")
        if re.findall(r'self\.dog\.element_click\(', line):
            line = re.sub(r'self\.dog\.element_click\(', "pylinuxauto.find_element_by_attr_path(", line)
            line = line.replace("\n", ".click()\n")
        if re.findall(r'self\.dog\.element_center\(', line):
            line = re.sub(r'self\.dog\.element_center\(', "pylinuxauto.find_element_by_attr_path(", line)
            line = line.replace("\n", ".center()\n")

        # ui
        if re.findall(r'= .*?\.ui\.btn_center\(', line):
            line = re.sub(r'= .*?\.ui\.btn_center\(', "= pylinuxauto.find_element_by_ui(", line)
            line = line.replace(")\n", ', appname="", config_path="").center()\n')
        if re.findall(r'\*.*?\.ui\.btn_center\(', line):
            line = re.sub(r'\*.*?\.ui\.btn_center\(', "*pylinuxauto.find_element_by_ui(", line)
            line = line.replace("))\n", ', appname="", config_path="").center())\n')

        for obj in ["cls", "self", "ShortCut", "MouseKey"]:
            for method_name in mk_method_names:
                line = line.replace(f"{obj}.{method_name}(", f"pylinuxauto.{method_name}(")
                line = re.sub(rf'\s[1].*?\.{method_name}\(', f"{(line.count(' ')) * ' '}pylinuxauto.{method_name}(", line)

            line = line.replace(f"{obj}.find_image(", "pylinuxauto.find_element_by_image(")
            line = line.replace(f"{obj}.ocr(", "pylinuxauto.find_element_by_ocr(")
            line = line.replace(f"{obj}.dog.find_element_by_attr(", "pylinuxauto.find_element_by_attr_path(")
            line = line.replace(f"{obj}.dog.app_element(", "pylinuxauto.find_element_by_attr_path(")
            line = line.replace(f"{obj}.get_process_status(", "Cmd.get_process_status(")
            line = line.replace(f"{obj}.kill_process(", "Cmd.kill_process(")

        for method_name in mk_method_names:
            if re.findall(rf"[a-zA-Z]+\.{method_name}", line):
                line = re.sub(rf'[a-zA-Z]+\.{method_name}\(', f"pylinuxauto.{method_name}(",line)

        # image
        if re.findall(r"return pylinuxauto.find_element_by_image", line):
            line = line.replace("\n", ".center()\n")

        return line

    def ruff_format(self):
        os.system(f"cd {self.new_project_name}/ && ruff format .")

    def transfer(self):
        self.new_project()
        self.rename_dir_file()
        self.transfer_code()
        self.ruff_format()


if __name__ == "__main__":
    Transfer(
        project_path="~/github/youqu/apps/autotest_dde_file_manager",
    ).transfer()
