#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#

import sys
from TouchStyle import *
import time
import os
from _thread import start_new_thread
import zipfile
import urllib.request
import json
import semantic_version
from pathlib import Path

update_log = "/tmp/update_log.log"
update_exit = "/tmp/update_exit"
release_api_url = "https://api.github.com/repos/ftCommunity/ftcommunity-TXT/releases"


class UpdateCheckThread(QThread):

    new_line = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, parent):
        super(UpdateCheckThread, self).__init__(parent)
        self.lines = []

    def run(self):
        time.sleep(1)
        while True:
            if os.path.isfile(update_exit):
                with open(update_exit) as f:
                    self.error.emit(f.read().replace("\n", "").strip())
                    break

            with open(update_log) as f:
                new_lines = f.readlines()
            if len(new_lines) > len(self.lines):
                i = len(self.lines)
                while i <= len(new_lines) - 1:
                    self.new_line.emit(new_lines[i].replace("\n", "").strip())
                    i += 1
                self.lines = new_lines

            time.sleep(0.1)


def updateStarter(ver):
    print("Start")
    if os.path.isfile(update_log):
        os.remove(update_log)
    if os.path.isfile(update_exit):
        os.remove(update_exit)
    os.system("sudo system-update " + ver + " > " + update_log + " 2>&1 ; echo $? > " + update_exit)


class EntryWidget(QWidget):
    pressed = pyqtSignal()

    def __init__(self, title, parent=None):
        QWidget.__init__(self, parent)

        self.layout = QVBoxLayout()
        self.layout.setSpacing(0)
        self.title = QLabel(title)
        self.layout.addWidget(self.title)
        self.value = QLabel("")
        self.value.setObjectName("smalllabel")
        self.value.setWordWrap(True)
        self.layout.addWidget(self.value)
        self.setLayout(self.layout)

    def setText(self, str):
        self.value.setText(str)

    def mousePressEvent(self, event):
        self.pressed.emit()


class PlainDialog(QDialog):

    def __init__(self):
        QDialog.__init__(self)
        if platform.machine() == "armv7l":
            size = QApplication.desktop().screenGeometry()
            self.setFixedSize(size.width(), size.height())
        else:
            self.setFixedSize(WIN_WIDTH, WIN_HEIGHT)

        self.setObjectName("centralwidget")

    def exec_(self):
        QDialog.showFullScreen(self)
        QDialog.exec_(self)


class ErrorDialog(TouchDialog):

    def __init__(self, parent, err):
        if err != "0":
            print("Error: " + err)
            err_codes = {"20": "Download validation failed!",
                         "30": "Backup failed!",
                         "40": "Installation failed!"}
            if err in err_codes:
                error = err_codes[err]
            else:
                error = "Unknown Error"
            error = error + "\nCode " + err
            title = "Error"
            self.reboot = False
        else:
            error = "TXT will reboot soon!"
            title = "Finished"
            self.reboot = True

        TouchDialog.__init__(self, title, parent)

        lbl = QLabel(error)
        lbl.setWordWrap(True)
        lbl.setAlignment(Qt.AlignCenter)
        vbox = QVBoxLayout()
        vbox.addStretch()
        vbox.addWidget(lbl)
        vbox.addStretch()
        self.centralWidget.setLayout(vbox)
        QTimer.singleShot(1, self.do_reboot)

    def do_reboot(self):
        if self.reboot:
            os.system("sudo reboot")


class ProgressDialog(PlainDialog):

    def __init__(self, parent, ver):
        PlainDialog.__init__(self)
        self.ver = ver
        self.parent = parent
        self.state = ""
        self.zip_sizes = {}

        self.thread = UpdateCheckThread(self)
        self.thread.new_line.connect(self.new_line)
        self.thread.error.connect(self.error)

        self.vbox = QVBoxLayout()
        title = QLabel("Progress")
        title.setAlignment(Qt.AlignCenter)
        self.vbox.addWidget(title)
        self.init_label = QLabel("Initializing Update")
        self.init_label.setAlignment(Qt.AlignCenter)
        self.vbox.addWidget(self.init_label)
        self.setLayout(self.vbox)
        QTimer.singleShot(2, self.start)
        self.check_timer = QTimer()
        self.check_timer.timeout.connect(self.checker)

    def start(self):
        self.size = int(os.popen("wget -qO- https://api.github.com/repos/ftCommunity/ftcommunity-TXT/releases/tags/v" + self.ver + " | get_size_json.py").read())
        print("Size: " + str(self.size))
        start_new_thread(updateStarter, (self.ver,))
        self.thread.start()
        self.buildUI()
        self.check_timer.start(100)

    def new_line(self, line):
        print("LINE: " + line)
        if line == "fetching archive from github...":
            self.state = "download"
        elif line == "validating update...":
            self.state = "validation"
        elif line == "backing up current system...":
            self.state = "backup"
        elif line == "installing update...":
            self.state = "install"
        print("State: " + self.state)

    def buildUI(self):
        self.init_label.setParent(None)
        self.preparation_widget = EntryWidget("Preparation")
        self.preparation_widget.setText("Pending")
        self.vbox.addWidget(self.preparation_widget)
        self.download_widget = EntryWidget("Download")
        self.download_widget.setText("Pending")
        self.vbox.addWidget(self.download_widget)
        self.backup_widget = EntryWidget("Backup")
        self.backup_widget.setText("Pending")
        self.vbox.addWidget(self.backup_widget)
        self.extract_widget = EntryWidget("Install")
        self.extract_widget.setText("Pending")
        self.vbox.addWidget(self.extract_widget)

    def checker(self):
        if self.state == "download":
            self.preparation_widget.setText("OK")
            try:
                current_size = os.stat("/tmp/update-" + self.ver + "/ftcommunity-txt-" + self.ver + ".zip").st_size
            except:
                current_size = 0
            percentage = (current_size / self.size) * 100
            self.download_widget.setText(str("{0:.1f}".format(percentage) + "%"))

        elif self.state == "validation":
            self.preparation_widget.setText("OK")
            self.download_widget.setText("Validating...")

        elif self.state == "backup":
            self.preparation_widget.setText("OK")
            self.download_widget.setText("OK")
            count = 0
            base = "/media/sdcard/boot/"
            if not os.path.isfile(base + "am335x-kno_txt.dtb"):
                count += 1
            if not os.path.isfile(base + "rootfs.img"):
                count += 1
            if not os.path.isfile(base + "uImage"):
                count += 1
            self.backup_widget.setText({0: "0%", 1: "33%", 2: "67%", 3: "100%"}[count])

        elif self.state == "install":
            self.preparation_widget.setText("OK")
            self.download_widget.setText("OK")
            self.backup_widget.setText("OK")
            if self.zip_sizes == {}:
                zip_file = zipfile.ZipFile("/tmp/update-" + self.ver + "/ftcommunity-txt-" + self.ver + ".zip")
                for c_file in zip_file.infolist():
                    sub_dict = {"target": c_file.file_size}
                    self.zip_sizes[c_file.filename] = sub_dict
            base = "/media/sdcard/boot/"
            for name, t_size in self.zip_sizes.items():
                try:
                    current_size = os.stat(base + name).st_size
                except:
                    current_size = 0
                self.zip_sizes[name]["percentage"] = current_size / self.zip_sizes[name]["target"]

            percentage = 0
            target_sum = 0
            for perc in self.zip_sizes.values():
                percentage += perc["percentage"] * perc["target"]
                target_sum += perc["target"]

            percentage = percentage / target_sum * 100
            self.backup_widget.setText(str("{0:.1f}".format(percentage) + "%"))

    def error(self, err):
        dialog = ErrorDialog(self.parent, err)
        dialog.exec_()
        self.close()


class UpdateListWidget(QListWidget):
    update = pyqtSignal(str)

    def __init__(self, releases, parent=None):
        super(UpdateListWidget, self).__init__(parent)

        id_list = []
        for r in releases:
            id_list.append(r["id"])

        id_list = reversed(sorted(id_list))

        for ID in id_list:
            release = self.getReleaseByID(id_list, releases, ID)
            if release["prerelease"]:
                item = QListWidgetItem(QIcon(os.path.join(os.path.dirname(os.path.realpath(__file__)),"prerelease.png")),release["tag_name"])
            else:
                item= QListWidgetItem(QIcon(os.path.join(os.path.dirname(os.path.realpath(__file__)),"stable.png")),release["tag_name"])
            item.setData(Qt.UserRole, (release))
            self.addItem(item)
        self.itemClicked.connect(self.onItemClicked)

    def onItemClicked(self, item):
        release = item.data(Qt.UserRole)
        self.update.emit(release["tag_name"])

    def getReleaseByID(self, id_list, releases, ID):
        for r in releases:
            if ID == r["id"]:
                return(r)
        return(None)

class TouchGuiApplication(TouchApplication):

    def __init__(self, args):
        TouchApplication.__init__(self, args)

        # create the empty main window
        self.w = TouchWindow("Update")
        self.dialog = None
        self.update_version = ""

        self.vbox = QVBoxLayout()
        self.lbl = QLabel("Searching for updates")
        self.lbl.setWordWrap(True)
        self.vbox.addWidget(self.lbl)
        self.but = QPushButton("Update")
        self.but.pressed.connect(self.start)
        self.but.setDisabled(True)
        self.vbox.addWidget(self.but)
        self.w.centralWidget.setLayout(self.vbox)
        self.w.show()
        QTimer.singleShot(0, self.checkUpdate)
        self.exec_()

    def start(self, ver=None):
        if self.dialog == None:
            if ver == None:
                ver = self.update_version
            ver = ver.replace('v', '')
            print("updating to :" + ver)
            self.dialog = ProgressDialog(self.w, ver)
            self.dialog.exec_()
            self.w.close()

    def getLatestRelease(self):
        try:
            raw_data = urllib.request.urlopen(release_api_url).read().decode()
            all_releases = json.loads(raw_data)
            i = 0
            while i <= len(all_releases) - 1:
                if all_releases[i]["prerelease"] == False:
                    return(all_releases[i])
                i += 1
        except:
            pass
        return(None)

    def to_str(self, ver):
        return(str(ver.major) + "." + str(ver.minor) + "." + str(ver.patch))

    def checkUpdate(self):
        lcl_ver = semantic_version.Version(Path('x/etc/fw-ver.txt').read_text().replace('v', ''))
        if len(lcl_ver.build) > 0:
            if "snapshot" in lcl_ver.build[0]:
                self.lbl.setParent(None)
                self.but.setParent(None)
                raw_data = urllib.request.urlopen(release_api_url).read().decode()
                all_releases = json.loads(raw_data)
                self.update_list = UpdateListWidget(all_releases)
                self.update_list.update.connect(self.start)
                self.vbox.addWidget(self.update_list)
                return
        release = self.getLatestRelease()
        if release == None:
            self.lbl.setText('Error while checking for updates!\nPlease try again later!\nYou are currently using ' + self.to_str(lcl_ver))
            return
        release_ver = semantic_version.Version(release['tag_name'].replace('v', ''))

        if lcl_ver < release_ver:
            self.update_version = self.to_str(release_ver)
            self.lbl.setText('An update to ' + self.update_version + ' is avaible. To Installl press "Update".\nYou are currently using ' + self.to_str(lcl_ver))
            self.but.setDisabled(False)
        else:
            self.lbl.setText("No new verion found!\nYou are currently using " + self.to_str(lcl_ver))


if __name__ == "__main__":
    TouchGuiApplication(sys.argv)
