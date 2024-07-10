import os
import re

from transfer.mk_method_names import mk_method_names


class Transfer:

    def __init__(self, project_name):
        self.project_name = project_name
        self.new_project_name = f"youqu3_{project_name}"

    def new_project(self):
        if os.path.exists(self.new_project_name):
            os.system(f"rm -rf {self.new_project_name}")
        os.system(f"cp -r {self.project_name} {self.new_project_name}")

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
                flag = False
                if not file.endswith(".py"):
                    continue

                with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                    lines = f.readlines()

                new_lines = []
                import_index = None
                for index, line in enumerate(lines):
                    if line.startswith(("from", "import")):
                        import_index = index

                        if not flag:
                            new_lines.insert(import_index, "from youqu3.gui import pylinuxauto\n")
                            new_lines.insert(import_index, "from youqu3 import sleep\n")
                            new_lines.insert(import_index, "from youqu3 import log\n")
                            new_lines.insert(import_index, "from youqu3 import logger\n")
                            new_lines.insert(import_index, "from youqu3 import setting\n")
                            flag = True

                    if line.startswith((
                            "from public",
                            "# pylint: disable",
                            "from src import Src",
                            "from src.button_center import ButtonCenter",
                            "from src.filectl import FileCtl",
                            "from setting.globalconfig import GlobalConfig",
                    )):
                        """丢掉"""
                    # elif line.endswith((
                    #         "DdeDesktopPublicWidget,\n",
                    #         "RightMenuPublicMethod,\n",
                    # )):
                    #     """丢掉"""
                    elif line in (
                        ")\n",
                    ):
                        ...
                    else:
                        line = line.replace(f"apps.{self.project_name}.", "")
                        line = self._replace(line)

                        if "Method(Src)" in line:
                            line = line.replace("Method(Src)", "Method(Cmd)")
                            new_lines.insert(import_index, "from youqu3.cmd import Cmd\n")


                        new_lines.append(line)

                with open(os.path.join(root, file), "w", encoding="utf-8") as f:
                    f.writelines(new_lines)

    def _replace(self, line):
        line = line.replace("widget", "method")
        line = line.replace("Widget", "Method")
        line = line.replace("from src", "from youqu3")
        line = line.replace("from youqu3.depends.dogtail", "from pylinuxauto.attr.dogtail")
        line = line.replace("from youqu3 import ElementNotFound", "from youqu3.exceptions import ElementNotFound")
        line = line.replace("from youqu3 import TemplateElementNotFound", "from youqu3.exceptions import TemplateElementNotFound")
        line = line.replace("from youqu3.cmdctl import CmdCtl", "from youqu3.cmd import Cmd")
        line = line.replace("run_cmd(", "run(")
        line = line.replace("out_debug_flag=False", "print_log=False")
        line = line.replace("CmdCtl.kill_process(", "Cmd.kill_process(")
        line = line.replace("CmdCtl.run(", "Cmd.run(")
        line = line.replace("from youqu3 import AssertCommon", "from youqu3.assertx import Assert")
        line = line.replace("AssertCommon", "Assert")
        line = line.replace("Src, ", "")
        line = line.replace("Src", "")
        line = line.replace("DdeDesktopPublicMethod,", "")
        line = line.replace("RightMenuPublicMethod,", "")
        line = line.replace("from youqu3.custom_exception", "from youqu3.exceptions")
        line = line.replace("GlobalConfig.", "setting.")
        line = line.replace("Config = _Config()", "config = _Config()")
        line = line.replace("Config.", "config.")
        line = line.replace("from config import Config", "from config import config")

        # ocr
        if re.findall(r'(= .*?\.ocr\()', line) and not line.endswith(".center()\n"):
            line = re.sub(r'= .*?\.ocr\(', "= pylinuxauto.find_element_by_ocr(", line)
            line = line.replace("\n", ".center()\n")
        if re.findall(r'(\*.*?\.ocr\()', line) and not line.endswith(".center()\n"):
            line = re.sub(r'\*.*?\.ocr\(', "*pylinuxauto.find_element_by_ocr(", line)
            line = line.replace(")\n", ".center())\n")
        # dog
        if re.findall(r'= .*?\.dog\.element_center\(', line):
            line = re.sub(r'= .*?\.dog\.element_center\(', "= pylinuxauto.find_element_by_attr_path(", line)
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

        # image
        if re.findall(r"return pylinuxauto.find_element_by_image", line):
            line = line.replace("\n", ".center()\n")

        return line

    def transfer(self):
        self.new_project()
        self.rename_dir_file()
        self.transfer_code()
        # os.system(f"ruff format {self.new_project_name}")


if __name__ == "__main__":
    Transfer(
        project_name="autotest_dde_file_manager",
    ).transfer()
