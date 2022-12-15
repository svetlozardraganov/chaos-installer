
import logging  # used for the loggin window in PyQt
import os
import shutil
import subprocess
import sys


from PyQt5.Qt import QDesktopServices, QUrl
from PyQt5.QtCore import (QSettings, QSize, Qt, QThreadPool, QTimer)
from PyQt5.QtGui import QColor, QFont, QIcon, QPalette, QPixmap
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox,
                             QFileDialog, QFormLayout, QFrame,
                             QGridLayout, QGroupBox, QHBoxLayout, QHeaderView,
                             QLabel, QLineEdit, QMainWindow,
                             QProgressBar, QPushButton, QRadioButton,
                             QSplashScreen, QStatusBar,
                             QTableWidget, QTableWidgetItem, QTabWidget,
                             QTextEdit, QVBoxLayout, QWidget)



logging.basicConfig(level=logging.INFO)
# logging.basicConfig(level=logging.DEBUG)

import platform
import tempfile


#PROJECT MODULES IMPORT
import CG_License
import CG_Nightlies
import CG_Uninstall
import CG_Utilities
import CG_ZIP_Installer

if platform.system() == 'Windows':
    import CG_Registry
    



#HANDLE COMMAND LINE ARGUMENTS:
try:
    killApp = False
    args = sys.argv
    args.pop(0)
    print('Argument List:', str(args))
    # logging.info(args)

    for item in args:
        print(item)
        if '-install=' in item or item.endswith('.exe'):

            if '-install=' in item:
                build_full_path = item[len('-install='):]
            else:
                build_full_path = item

            index = build_full_path.rfind('\\') + 1
            build_name = build_full_path[index:]
            build_path = build_full_path[:index]
            print('Build Name = {}'.format(build_name))
            print('Build Path = {}'.format(build_path))

            data = CG_ZIP_Installer.instance.getZipVersionsFromString(input_string=build_name)
            
            CG_Utilities.instance.install(download_path=build_path, 
                                build_file= build_name,
                                productName=data['productName'], 
                                productVersion= data['productVersion'], 
                                platformName=data['platformName'],
                                platformVersion=data['platformVersion'])
            killApp = True

except:
    pass

if killApp == True:
    exit()



#RESOURCES:
#MULTITHREADING/DOWNLAOD FREEZE ISSUE: https://www.learnpyqt.com/courses/concurrent-execution/multithreading-pyqt-applications-qthreadpool/

#MULTITHREADING TUTORIAL TO RESOLVE FREEZES: https://www.learnpyqt.com/courses/concurrent-execution/multithreading-pyqt-applications-qthreadpool/


class ChaosGroup(QMainWindow): #THIS IS THE MAIN WINDOW, THE ONE THAT EVERYTHING IS BUILD ON

    download_path = os.path.realpath(tempfile.gettempdir()) + "/Chaos-Installer/"
    mounted_volumes = []

    # SETTINGS
    #Computer\HKEY_USERS\S-1-5-21-2633894342-2101855249-4104172794-1001\Software\svetlozar.draganov\Chaos Group Installer
    #(MACOS) /Users/support/Library/Preferences/com.svetlozar-draganov.Chaos-Installer
    settings_global = QSettings('svetlozar.draganov', 'Chaos-Installer')


    def __init__(self):
        super().__init__()

        #MENUBAR
        self.bar = self.menuBar()
        # self.file = self.bar.addMenu("File")
        # self.file.addAction("Sample Menu 1")

        #MAIN WINDOW PROPERTIES
        self.setMinimumSize(QSize(650,425))
        self.setWindowTitle("Chaos Installer")
        self.setWindowIcon(QIcon('images/logo.png'))

        #HIDE TITLEBAR
        #https://www.geeksforgeeks.org/pyqt5-how-to-hide-the-title-bar-of-window/
        # self.setWindowFlag(Qt.FramelessWindowHint) 

        #STATUSBAR
        self.statusBar = StatusBar()
        self.setStatusBar(self.statusBar)


        # LOAD WINDOW SETTINGS
        try:
            self.resize(ChaosGroup.settings_global.value('window size'))
            self.move(ChaosGroup.settings_global.value('window position'))
            ChaosGroup.download_path = ChaosGroup.settings_global.value('install folder')
        except:
            logging.info('Cannot Load Settings!')
            pass

        #CREATE DOWNLOAD FOLDER IF NOT EXIST
        if not os.path.exists(ChaosGroup.download_path):
            os.makedirs(ChaosGroup.download_path)



        #TRY LOADING SUDO PASSWORD FROM SETTINGS
        if platform.system() != 'Windows':
            
            try:
                ChaosGroup.sudo_password = ChaosGroup.settings_global.value('sudo_password')
                
                #CHECK IF PASSWORD IS RIGHT, IF NOT THROWN AN ERROR AND EXECUTE THE EXCEPT BLOCK
                subprocess.check_output('sudo -k -S echo success', shell=True, input=ChaosGroup.sudo_password)

                logging.info('Sudo-password successfully loaded')

                #IF LOGIN IS SUCCESSFULL CREATE TABS
                self.tab_MAIN = Tab_MAIN(self)
                self.setCentralWidget(self.tab_MAIN)
                
            #IF PASSWORD IS INCORRECT BUILD THE GUI FOR THE SUDO-INPUT-WINDOW
            except:
                logging.info('Cannot load sudo-password')
                
                self.sudo_login = Sudo_Login()
                self.setCentralWidget(self.sudo_login)

                self.tab_MAIN = Tab_MAIN(self)
                self.tab_MAIN.hide()

        #IF SYSTEM IS WINDOWS, JUST CREATE TABS
        else:
            self.tab_MAIN = Tab_MAIN(self)
            self.setCentralWidget(self.tab_MAIN)
        


    def closeEvent(self, *args, **kwargs):

        # STORE SETTINGS
        CG.tab_MAIN.tab_Settings.storeSettings()




class StatusBar(QStatusBar):

    def __init__(self):

        super().__init__()

        # self.statusBar = QStatusBar()

        self.platformName = QLabel("Host App:")
        self.platformName.setStyleSheet("QLabel{font-weight: bold;color: grey}")
        self.addPermanentWidget(self.platformName)

        self.platormPath = QLabel("host-app-path")
        self.addPermanentWidget(self.platormPath)

        self.productName = QLabel("product-name:")
        self.productName.setStyleSheet("QLabel{font-weight: bold;color: grey}")
        self.addPermanentWidget(self.productName)

        self.version = QLabel("xx.xx.xx")
        self.addPermanentWidget(self.version)

        self.productName2 = QLabel("V-Ray:")
        self.productName2.setStyleSheet("QLabel{font-weight: bold;color: grey}")
        self.productName2.hide()
        self.addPermanentWidget(self.productName2)

        self.version2 = QLabel("xx.xx.xx")
        self.version2.hide()
        self.addPermanentWidget(self.version2)

        # self.statusBar.showMessage("Sample Message Status Bar:")

    def update_visibility(self, productName = '', platformName =''):
        
        CG.statusBar.productName.show()
        CG.statusBar.version.show()
        CG.statusBar.platformName.show()
        CG.statusBar.platormPath.show()
        CG.statusBar.productName2.show()
        CG.statusBar.version2.show()
        CG.statusBar.platformName.show()
        CG.statusBar.platormPath.show()

        # HIDE/SHOW STATUS BAR TEXTS:
        if productName in ['Lavina', 'Chaos Vantage', 'License Server', 'PDPlayer', 'V-Ray AppSDK']:
            CG.statusBar.platformName.hide()
            CG.statusBar.platormPath.hide()
            CG.statusBar.productName2.hide()
            CG.statusBar.version2.hide()

            if platform.system() != 'Windows' and productName == 'PDPlayer':
                CG.statusBar.productName.hide()
                CG.statusBar.version.hide()

        elif productName == 'V-Ray' and platformName != 'Standalone':
            CG.statusBar.productName2.hide()
            CG.statusBar.version2.hide()

        elif (productName == 'V-Ray' and platformName == 'Standalone') or (productName == 'V-Ray Swarm'):
            CG.statusBar.platformName.hide()
            CG.statusBar.platormPath.hide()
            CG.statusBar.productName2.hide()
            CG.statusBar.version2.hide()

        #HIDE ALL THE STATUSBAR ITEMS
        elif productName == 'V-Ray Benchmark':
            CG.statusBar.productName.hide()
            CG.statusBar.version.hide()
            CG.statusBar.platformName.hide()
            CG.statusBar.platormPath.hide()
            CG.statusBar.productName2.hide()
            CG.statusBar.version2.hide()
            CG.statusBar.platformName.hide()
            CG.statusBar.platormPath.hide()

        # elif productName == 'Phoenix FD':
        #     pass

    def update_versions(self, productName='', productVersion = '', platformName='', platformVersion=''):
        
        self.update_visibility(productName=productName, platformName=platformName)

        #reg = CG_Registry.Registry()

        # UPDATE CG-VERSION
        CG.statusBar.productName.setText(productName)

        if platform.system() == 'Windows':
            cg_version = CG_Registry.Registry().getCGproductVer(productName, platformName, platformVersion)

        elif platform.system() == 'Darwin':
            cg_version = CG_Uninstall.CG_Uninstall().getChaosProductVersion(productName=productName, platformName=platformName, platformVersion=platformVersion)
        
        elif platform.system() == 'Linux':
            cg_version = CG_Uninstall.CG_Uninstall().getChaosProductVersion(productName=productName, platformName=platformName, platformVersion=platformVersion)

        CG.statusBar.version.setText(cg_version)

        if cg_version == 'Not Installed':
            CG.statusBar.version.setStyleSheet("QLabel{color: red}")
        else:
            CG.statusBar.version.setStyleSheet("")

        # UPDATE PLATFORM PATH
        if platform.system() == 'Windows':
            platform_path = CG_Registry.registry.getHostAppPath(platformName=platformName, platformVersion=platformVersion,
                                             productVersion=productVersion)
        
        elif platform.system() == 'Linux':
            platform_path = CG_Utilities.instance.linux_get_host_app_path(platformName=platformName, platformVersion=platformVersion)

        elif platform.system() == 'Darwin':

            platform_path = CG_Utilities.instance.mac_get_host_app_path(platformName=platformName, platformVersion=platformVersion)

            #REMOVE THE STRING DATA AFTER THE .APP
            if '.app' in platform_path:
                split_index = platform_path.find('.app') + len('.app')
                platform_path = platform_path[:split_index]

        CG.statusBar.platormPath.setText(platform_path)

        if platform_path == 'Not Installed':
            CG.statusBar.platormPath.setStyleSheet("QLabel{color: red}")
        else:
            CG.statusBar.platormPath.setStyleSheet("")

        # UPDATE CG-VERSION2 WHEN PHOENIXFD IS THE PRODUCT NAME

        if platform.system() != 'Darwin':

            if platform.system() == 'Windows':
                cg_version2 = CG_Registry.Registry().getCGproductVer('V-Ray', platformName, platformVersion)

            elif platform.system() == 'Linux':
                cg_version2 = CG_Uninstall.CG_Uninstall().getChaosProductVersion(productName='V-Ray', platformName=platformName, platformVersion=platformVersion)


            #cg_version2 = 'Not Installed'
            CG.statusBar.version2.setText(cg_version2)

            if cg_version2 == 'Not Installed':
                CG.statusBar.version2.setStyleSheet("QLabel{color: red}")
            else:
                CG.statusBar.version2.setStyleSheet("")


class Tab_MAIN(QWidget): #HERE THE WINDOW IS SPLIT ON MULTIPLE TABS, AND INFO IS ADDED INTO EACH TAB

    def __init__(self, parent):
        super(QWidget, self).__init__(parent)
        self.mainLayout = QVBoxLayout()

        #CREATE TABS
        self.tab_Widget = QTabWidget(self)
        self.tab_Install = Tab_Installer()
        self.tab_Uninstall = Tab_Uninstaller()
        self.tab_License = Tab_License()
        # self.tab_Logging = Tab_Logging()
        self.tab_Settings = Tab_Settings()
        
        #ADD TABS TO TAB-WIDGET
        self.tab_Widget.addTab(self.tab_Install, "Installer")
        self.tab_Widget.addTab(self.tab_Uninstall, "Uninstaller")
        self.tab_Widget.addTab(self.tab_License, "License Listener")
        self.tab_Widget.addTab(self.tab_Settings, 'Settings')

        #ADD PROGRESS BAR
        self.progress_bar = QProgressBar()
        # self.progress_bar.setAlignment(Qt.AlignCenter)
        self.progress_bar.setMaximumHeight(5)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.hide()

        #ADD WIDGETS TO LAYOUT
        self.mainLayout.addWidget(self.tab_Widget)
        self.mainLayout.addWidget(self.progress_bar)
        self.setLayout(self.mainLayout)


    def progress_bar_update(self, data):
        self.progress_done = data['progress_done']
        self.downloaded_mb = data['downloaded_mb']
        self.total_mb = data['total_mb']

        if self.progress_done != 100:
            CG.tab_MAIN.progress_bar.show()
            CG.tab_MAIN.progress_bar.setValue(self.progress_done)
            CG.statusBar.showMessage("Downloading " + str(self.progress_done) + "%  " + str(self.downloaded_mb) + "MB/" + str(self.total_mb) + "MB")


        else:
            CG.tab_MAIN.progress_bar.hide()
            CG.statusBar.clearMessage()
        

class Tab_Installer(QWidget): #THIS WIDGET IS SPLIT INTO SEPARATE GROUPS, EACH GROUP HAS IT'S OWN SET OF FUCTIONALITY

    def __init__(self):
        super().__init__()
        
        #CREATE LAYOUT
        self.mainLayout = QVBoxLayout()
        self.bottomLayout = QHBoxLayout()
        self.bottomLayout.setAlignment(Qt.AlignLeft)

        self.tab_installer_ref = self #REFERENCE TO THIS TAB_INSTALLER IS NEEDED IN ORDER TO LATER ADD OFFICIAL WIDGET AFTER LOGIN
       
        self.group_login = Group_LogIn(self.tab_installer_ref)
        # self.group_official = Group_Official()  #OFFICIAL-DOWNLOAD WIDGET WILL BE ADDED IN THE LOGIN TAB
        self.group_nightly = Group_Nightly()
        self.group_zip = Group_ZIP()

        self.rbtn_install_silent = QRadioButton("Silent Install")
        self.rbtn_install_silent.setChecked(True)
        self.rbtn_install_gui = QRadioButton("GUI Install")
        self.chbox_start_host_app_after_install = QCheckBox('Start Host-App')
        self.qcheck_quit_after_installation = QCheckBox('Quit after install')


        #ADD WIDGETS TO LAYOUT
        self.mainLayout.addWidget(self.group_login.groupBox_Login)
        # self.mainLayout.addWidget(self.group_official.groupBox_Official) #OFFICIAL-DOWNLOAD WIDGET WILL BE ADDED IN THE LOGIN TAB
        self.mainLayout.addWidget(self.group_nightly.groupBox_Nightly)
        self.mainLayout.addWidget(self.group_zip.groupBox_ZIP_Installer)

        self.bottomLayout.addWidget(self.rbtn_install_silent)
        self.bottomLayout.addWidget(self.rbtn_install_gui)
        self.bottomLayout.addWidget(self.chbox_start_host_app_after_install)
        self.bottomLayout.addWidget(self.qcheck_quit_after_installation)

        self.mainLayout.addLayout(self.bottomLayout)

        #mainLayout.addStretch(1)
        self.setLayout(self.mainLayout)

        #VARIABLE TO STORE BUILD ID VALUE NEEDED FOR THE DOWNLOAD FUNCTION OF CG_OFFICIAL FILE
        self.build_id_list = []
        self.buildFile_list = []




class Group_LogIn(QWidget):
    #THIS CLASS PROVIDES USER-LOGIN FUNCTIONALITY WITH CHAOS-ACCOUNT
    #IF LOGIN IS NOT SUCCESFULL THE REST OF THE UI REMAINS HIDDEN FOR THE USER

    def __init__(self, tab_installer_ref):
        super().__init__()

        self.groupBox_Login = QGroupBox("www.chaosgroup.com")
        mainLayout = QHBoxLayout()  

        self.tab_installer_ref = tab_installer_ref

        #CHAOSGROUP.COM LOGIN
        try:
            ChaosGroup.username = ChaosGroup.settings_global.value('username')
            ChaosGroup.password = ChaosGroup.settings_global.value('password')
        except:
             logging.info('Cannot load log-in credentials')

        #CHECK IF USERNAME AND PASSWORD ARE CORRECT BY LOGGING TO CHAOSGROUP.COM
        self.log_in_chaosgroup = CG_Official.GetBuildsList(username=ChaosGroup.username, password=ChaosGroup.password)

        #SHOW LOGON SCREEN IF LOGIN IS NOT SUCCESSFULL
        if self.log_in_chaosgroup.status_code != 200:

            #ADD WIDGETS
            self.qlabel_username = QLabel('Username:')
            self.qline_username = QLineEdit()

            self.qlabel_password = QLabel('Password')
            self.qline_password = QLineEdit()
            self.qline_password.setEchoMode(QLineEdit.Password)

            self.qcheckbox_remember_credentials = QCheckBox('Remember Credentials')
            self.btn_log_in = QPushButton('Log In')
            self.btn_log_in.clicked.connect(lambda: self.LogInButtonPress(username=self.qline_username.text(),
                                                                        password=self.qline_password.text()))

            mainLayout.addWidget(self.qlabel_username)
            mainLayout.addWidget(self.qline_username)
            mainLayout.addWidget(self.qlabel_password)
            mainLayout.addWidget(self.qline_password)
            mainLayout.addWidget(self.qcheckbox_remember_credentials)
            mainLayout.addWidget(self.btn_log_in)

            self.groupBox_Login.setLayout(mainLayout)


        else:
            #IF LOGGIN IS SUCCESSFULL PASS THE BUILDS LIST TO OFFICIAL-GROUP, ADD OFFICIAL GROUP TO TAB-WIDGET, AND HIDE LOGGIN GROUP
            self.group_official = Group_Official(builds_list = self.log_in_chaosgroup)
            self.tab_installer_ref.mainLayout.addWidget(self.group_official.groupBox_Official)
            self.groupBox_Login.hide()

              #SET V-RAY AS DEFAULT PRODUCT FOR OFFICIAL AND NIGHTLY GROUP

                    

    def LogInButtonPress(self, username, password):

        self.log_in_chaosgroup = CG_Official.GetBuildsList(username=username, password=password)

        #IF LOGIN IS SUCCESFULL PROCEED WITH ADDING THE REST OF THE UI-MENUS
        if self.log_in_chaosgroup.status_code == 200:
            logging.info('Succesfull login')

            #STORE USERNAME/PASSWORD IN SETTINGS
            if self.qcheckbox_remember_credentials.isChecked() == True:
                ChaosGroup.settings_global.setValue('username', self.qline_username.text())
                ChaosGroup.settings_global.setValue('password', self.qline_password.text())

            #STORE USERNAME/PASSWORD IN GENERAL VARIABLES, CAUSE THOSE ARE USED IN OFFICIAL-SECTION,
            #AND SINCE THEY ARE ONLY LOADED IN THE BEGINING OF THE SCTIPT THEY WILL NOT BE UPDATED WHEN LOGIN SCREEN APPEARS
            ChaosGroup.username = self.qline_username.text()
            ChaosGroup.password = self.qline_password.text()
            
   
            #INNITIALIZE OFFICIAL INSTALLER AFTER SUCCESSFULL LOGIN
            self.group_official = Group_Official(builds_list = self.log_in_chaosgroup)
            self.tab_installer_ref.group_login.groupBox_Login.hide()
            self.tab_installer_ref.mainLayout.insertWidget(0, self.group_official.groupBox_Official)

            #SET V-RAY AS A CURRENT PRODUCT FOR THE OFFICIAL INSTALLER
            vray_index = self.group_official.cbox_official_productName.findText('V-Ray')
            self.group_official.cbox_official_productName.setCurrentIndex(vray_index)

        else:

            error_msg = 'Cannot not log-in, are you using the correct username and password'
            more_information = 'Try to log-in https://download.chaosgroup.com/ in a web-browser.'
            CG_Utilities.instance.PyQTerrorMSG(error_msg=error_msg, more_information=more_information, App=CG)


class Group_Official(QWidget):

    def __init__(self, builds_list):
        super().__init__()

        self.groupBox_Official = QGroupBox("Official Installer (download.chaos.com)")

        self.topLayout = QHBoxLayout()
        self.bottonLayout = QHBoxLayout()

        self.mainLayout = QVBoxLayout()

        # SELECT PRODUCT COMBOBOX
        self.cbox_official_productName = QComboBox()
        #CREATE A SET OF PRODUCTS IN ORDER TO REMOVE DUPLICATES
        self.official_cg_product_set = set()

        #GET BUILDS LIST FROM WEBSITE
        self.get_builds_list =  builds_list #CG_Official.GetBuildsList(username=ChaosGroup.username,password=ChaosGroup.password)

        for item in self.get_builds_list.builds_list:
            self.official_cg_product_set.add(item['productName'])
        self.official_cg_product_set = sorted(self.official_cg_product_set)

        #ADD PRODUCT SET TO COMBOBOX
        for item in self.official_cg_product_set:
            self.cbox_official_productName.addItem(item)
        self.cbox_official_productName.currentTextChanged.connect(self.cbox_official_productName_function) #RUN A FUNCTION WHEN COMBOX OPTION IS CHANGED


        # SELECT HOST APPLICATION COMBOBOX
        self.cbox_official_platformName = QComboBox()
        self.cbox_official_platformName.addItem("-")
        self.cbox_official_platformName.currentTextChanged.connect(self.cbox_official_platformName_function) #RUN A FUNCTION WHEN COMBOX OPTION IS CHANGED

        #SELECT HOST APP VERSION COMBOBOX
        self.cbox_official_platformVersion = QComboBox()
        self.cbox_official_platformVersion.addItem("-")
        self.cbox_official_platformVersion.currentTextChanged.connect(self.cbox_official_platformVersion_function) #RUN A FUNCTION WHEN COMBOX OPTION IS CHANGED

        # SELECT VRAY VERSION COMBOBOX
        self.cbox_official_version = QComboBox()
        self.cbox_official_version.addItem("-")
        self.cbox_official_version.currentTextChanged.connect(self.cbox_official_version_function)

        #INSTALL BUTTON
        self.official_install = QPushButton('Install', self)
        self.official_install.clicked.connect(self.click_btn_official_install)


        #ADD WIDGETS TO LAYOUT
        self.topLayout.addWidget(self.cbox_official_productName)
        self.topLayout.addWidget(self.cbox_official_platformName)
        self.topLayout.addWidget(self.cbox_official_platformVersion)
        self.topLayout.addWidget(self.cbox_official_version)
        self.bottonLayout.addWidget(self.official_install)


        self.mainLayout.addLayout(self.topLayout)
        self.mainLayout.addLayout(self.bottonLayout)
        self.groupBox_Official.setLayout(self.mainLayout)

        # self.setLayout(self.mainLayout)


    # OFFICIAL INSTALL - CONNECT BUTTON/MENUS FUNCTIONS
    def cbox_official_productName_function(self):
        logging.info('ProductName = %s', self.cbox_official_productName.currentText())

        # REMOVE EXISTING ITEMS FROM VARIABLES, NEEDED IN ORDER TO ADD NEW ONES
        self.build_id_list = []
        self.buildFile_list = []

        #IF PRODUCT == V-RAY, PHOENIXFD ADD HOST HOST PLATFORMS TO HOST-APP COMBOBOX
        if self.cbox_official_productName.currentText() == "V-Ray" or \
                self.cbox_official_productName.currentText() == "Phoenix FD":
            
           
            #CLEAR OTHER COMBOBOXES
            self.cbox_official_platformName.clear()
            self.cbox_official_platformName.show()
            self.cbox_official_platformVersion.clear()
            self.cbox_official_platformVersion.show()
            self.cbox_official_version.clear()

            #ADD PLATFORM TO COMBOBOX
            platformName_set = set()
            for item in self.get_builds_list.builds_list:
                if item['productName'] == self.cbox_official_productName.currentText():
                    platformName_set.add(item['platformName'])
                    #print(item['platformName'])

            #SORT HOST APP SET BEFORE ADDING ITEMS TO MENU
            platformName_set = sorted(platformName_set)
            for item in platformName_set:
                self.cbox_official_platformName.addItem(item)



        #IF PRODUCT == PDPLAYER, V-Ray AppSDK, License Server, Lvina
        if self.cbox_official_productName.currentText() == "PDPlayer" or \
                self.cbox_official_productName.currentText() == "V-Ray AppSDK" or \
                self.cbox_official_productName.currentText() == "License Server" or \
                self.cbox_official_productName.currentText() == "Chaos Vantage" or \
                self.cbox_official_productName.currentText() == "V-Ray Benchmark" or\
                self.cbox_official_productName.currentText() == "V-Ray Swarm" or\
                self.cbox_official_productName.currentText() == "Enterprise License Server" or\
                self.cbox_official_productName.currentText() == "Cosmos Browser":

            #CLEAR/HIDE OTHER COMBOBOXES
            self.cbox_official_platformName.hide()
            self.cbox_official_platformName.clear()

            self.cbox_official_platformVersion.hide()
            self.cbox_official_platformVersion.clear()

            self.cbox_official_version.clear()

            #ADD VERSIONS TO VERSION-COMBOBOX
            for item in self.get_builds_list.builds_list:
                if item['productName'] == self.cbox_official_productName.currentText():
                    self.cbox_official_version.addItem(item['version'])
                    self.build_id_list.append(item['id'])
                    self.buildFile_list.append(item['buildFile'])

            


    #SET HOST APP TYPE FUCNTION
    def cbox_official_platformName_function(self):

        #IF PLATFORMNAME COMBOBOX IS NOT EMPTY
        if self.cbox_official_platformName.currentText() != '':
            logging.debug(self.cbox_official_platformName.currentText())

            # REMOVE EXISTING ITEMS FROM VARIABLES, NEEDED IN ORDER TO ADD NEW ONES
            self.build_id_list = []
            self.buildFile_list = []

            self.cbox_official_platformVersion.clear()
            self.cbox_official_platformVersion.show()


            if self.cbox_official_platformName.currentText() == 'Modo' or \
                    self.cbox_official_platformName.currentText() == 'Revit'or \
                    self.cbox_official_platformName.currentText() == 'SketchUp'or \
                    self.cbox_official_platformName.currentText() == 'Standalone'or \
                    self.cbox_official_platformName.currentText() == 'Unreal':
                self.cbox_official_platformVersion.hide()
                self.cbox_official_version.clear()

                for item in self.get_builds_list.builds_list:
                    if item['platformName'] == self.cbox_official_platformName.currentText() and \
                            item['productName'] == self.cbox_official_productName.currentText():
                        self.cbox_official_version.addItem(item['version'])
                        self.build_id_list.append(item['id'])
                        self.buildFile_list.append(item['buildFile'])



            if self.cbox_official_platformName.currentText() == '3ds Max' or \
                self.cbox_official_platformName.currentText() == 'Maya' or \
                    self.cbox_official_platformName.currentText() == 'Houdini' or \
                    self.cbox_official_platformName.currentText() == 'Nuke' or \
                    self.cbox_official_platformName.currentText() == 'Rhino' or \
                    self.cbox_official_platformName.currentText() == 'Cinema 4D'    :

                platformName_set = set()
                for item in self.get_builds_list.builds_list:
                    if item['platformName'] == self.cbox_official_platformName.currentText() and \
                            item['productName'] == self.cbox_official_productName.currentText():
                        platformName_set.add(item['platformVersion'])

                platformName_set = sorted(platformName_set, reverse=True)
                for item in platformName_set:
                    self.cbox_official_platformVersion.addItem(item)

                #3DSMAX VERSION 9.0 IS BY DEFAULT ON TOP, REMOVE IT FROM THE TOP AND ADD IT BACK TO THE BOTTOM
                if self.cbox_official_productName.currentText() == 'V-Ray' and self.cbox_official_platformName.currentText() == '3ds Max':
                    self.cbox_official_platformVersion.removeItem(0)
                    self.cbox_official_platformVersion.addItem(list(platformName_set)[0])



    #SET HOST APP VERSION FUNCTION
    def cbox_official_platformVersion_function(self):

        #IF PLATFORM VERSION COMBOBOX IS NOT EMPTY:
        if self.cbox_official_platformVersion.currentText() != '':
            logging.info('<OFFICIAL> Platform Version = %s',self.cbox_official_platformVersion.currentText())

            #REMOVE EXISTING ITEMS FROM VARIABLES, NEEDED IN ORDER TO ADD NEW ONES
            self.build_id_list = []
            self.buildFile_list = []

            #ADD VERSIONS TO COMBOBOX
            self.cbox_official_version.clear()
            logging.info('<OFFICIAL> Platform Name = %s', self.cbox_official_platformName.currentText())

            for item in self.get_builds_list.builds_list:
                if item['platformName'] == self.cbox_official_platformName.currentText() and \
                    item['platformVersion'] == self.cbox_official_platformVersion.currentText() and \
                    item['productName'] == self.cbox_official_productName.currentText():

                    if self.cbox_official_productName.currentText() == "V-Ray":
                           
                        self.cbox_official_version.addItem(item['version'])
                        self.build_id_list.append(item['id'])
                        self.buildFile_list.append(item['buildFile'])

                    if self.cbox_official_productName.currentText() == "Phoenix FD":
                        self.cbox_official_version.addItem(item['productNameExtended'][11:])
                        self.build_id_list.append(item['id'])
                        self.buildFile_list.append(item['buildFile'])

    def cbox_official_version_function(self):

        #IF VERSION COMBOBOX IS NOT EMPTY
        if self.cbox_official_version.currentText() != '':

            logging.info('<OFFICIAL> Product Version = %s', self.cbox_official_version.currentText())
            # print(self.cbox_official_version.currentText())

            #UPDATE STATUSBAR
            CG.statusBar.update_versions(productName=self.cbox_official_productName.currentText(),
                                        productVersion = self.cbox_official_version.currentText(),
                                        platformName=self.cbox_official_platformName.currentText(),
                                        platformVersion=self.cbox_official_platformVersion.currentText())


    #CLICK ON OFFICIAL INSTALL BUTTON
    def click_btn_official_install(self):

        #CHECK IF HOST APP IS AVAILABLE:
        platformName=self.cbox_official_platformName.currentText()
        platformVersion = self.cbox_official_platformVersion.currentText()
        productName = self.cbox_official_productName.currentText()
        host_app_is_installed = CG_Utilities.instance.check_host_app_is_installed(productName=productName, platformName=platformName, platformVersion=platformVersion, App=CG)
        
        if host_app_is_installed == True:

            self.build_id = self.build_id_list[self.cbox_official_version.currentIndex()]
            logging.debug('id = %s', self.build_id_list[self.cbox_official_version.currentIndex()])

            self.build_file = self.buildFile_list[self.cbox_official_version.currentIndex()]
            logging.info('buildFile = %s', self.buildFile_list[self.cbox_official_version.currentIndex()])

            #BUILD DOWNLOADING
            #NEEDED IN ORDER TO RUN DOWNLOAD PROCESS AS A SEPARATE THREAD
            self.threadpool = QThreadPool()
            logging.debug("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())

            #SESSION KEEPS THE COOKIES FROM THE DOWNLOAD PAGE, THOSE NEEDS TO BE PASSED TO DOWNLOAD FUNCTION AS WELL
            
            
            self.download_build = CG_Official.DownloadBuild(self.build_id, self.build_file, ChaosGroup.download_path, ChaosGroup.username, ChaosGroup.password)

            #SIGNALS NEEDED TO UPDATE PROGRESS BAR, TITLE BAR, AND DETERMINE DONWLOAD COMPLETION
            self.download_build.signals.finished.connect(self.run_installer)
            
            #UPDATE PROGRESS BAR
            self.download_build.signals.progress_data_signal.connect(CG.tab_MAIN.progress_bar_update)

            #START DOWNLOAD PROCESS ON A SEPARATE THREAD
            self.threadpool.start(self.download_build)

        else:
            logging.info('Installation canceled')

    def run_installer(self):


        #START INSTALLATION
        CG_Utilities.instance.install(download_path = ChaosGroup.download_path,
                            build_file = self.build_file,
                            productName = self.cbox_official_productName.currentText(), 
                            productVersion = self.cbox_official_version.currentText(), 
                            platformName = self.cbox_official_platformName.currentText(),
                            platformVersion = self.cbox_official_platformVersion.currentText(),
                            silent_install = CG.tab_MAIN.tab_Install.rbtn_install_silent.isChecked(),
                            start_host_app = CG.tab_MAIN.tab_Install.chbox_start_host_app_after_install.isChecked(),
                            remove_files_after_install = CG.tab_MAIN.tab_Settings.qcheck_remove_official_files.isChecked(),
                            quit_after_install= CG.tab_MAIN.tab_Install.qcheck_quit_after_installation.isChecked(),
                            App = CG)
        

        #UPDATE STATUS BAR
        CG.statusBar.update_versions(productName=self.cbox_official_productName.currentText(),
                                    productVersion = self.cbox_official_version.currentText(),
                                    platformName=self.cbox_official_platformName.currentText(),
                                    platformVersion=self.cbox_official_platformVersion.currentText())

        #UPDATE UNINSTALL TAB
        #CG.tab_MAIN.tab_Uninstall.add_update_table_items()




class Group_Nightly(QWidget):
    
    def __init__(self):
        super().__init__()

        self.groupBox_Nightly = QGroupBox("Nightly Installer (nightlies.chaos.com)")

        self.cg_nightlies = CG_Nightlies.Nightlies()

        #CHECK IF FTP IS ACCESSIBLE
        if self.cg_nightlies.ftp_status == False:
            self.mainLayout = QVBoxLayout()
            self.mainLayout.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            self.qlabel_ftp_not_accessible = QLabel('Chaos Nightlies FTP Server is not accessible! \n Make sure you are in the office network or use VPN!')
            boldFont = QFont()
            boldFont.setBold(True)
            self.qlabel_ftp_not_accessible.setFont(boldFont)
            self.mainLayout.addWidget(self.qlabel_ftp_not_accessible)
            self.groupBox_Nightly.setLayout(self.mainLayout)
        
        #IF FTP IS ACCESSIBLE PROCEED WITH THE REST OF THE WIDGETS
        else:
            self.topLayout = QHBoxLayout()
            self.middleLayout = QHBoxLayout()
            self.bottomLayout = QHBoxLayout()
            self.mainLayout = QVBoxLayout()
            self.Top_Layout()


    def Top_Layout(self):
        
        # SELECT PRODUCT
        self.cbox_nightly_productName = QComboBox()
        product_names = list(self.cg_nightlies.productsNames)


        #remove product names for macOs
        remove_items = []
        if platform.system() == 'Darwin':
            for item in product_names:
                if item == 'Chaos Vantage' or item == 'Phoenix FD':
                    remove_items.append(item)

        #remove product names for Linux
        elif platform.system() == 'Linux':
            for item in product_names:
                if item == 'Chaos Vantage':
                    remove_items.append(item)

        for item in remove_items:
            product_names.remove(item)

        self.cbox_nightly_productName.addItems(product_names)
        self.cbox_nightly_productName.setToolTip("cbox_nightly_productName")
        self.cbox_nightly_productName.currentTextChanged.connect(self.cbox_nightly_productName_function)
        
        
        #SELECT PLATFORM TYPE
        self.cbox_nightly_platformName = QComboBox()
        self.cbox_nightly_platformName.setToolTip("cbox_nightly_platformName")
        self.cbox_nightly_platformName.currentTextChanged.connect(self.cbox_nightly_platformName_function)


        # SELECT PRODUCT VERSION
        self.cbox_nightly_version = QComboBox()
        self.cbox_nightly_version.setToolTip("cbox_nightly_version")
        self.cbox_nightly_version.currentTextChanged.connect(self.cbox_nightly_version_function)

        #INSTALL TYPE - NORMAL/ZIP
        self.cbox_install_type = QComboBox()
        self.cbox_install_type.addItems(['Standard Install', 'ZIP Install'])					   
        self.cbox_install_type.currentTextChanged.connect(self.cbox_install_type_function)

        # OPEN PAGE BUTTON
        self.open_page = QPushButton('Open Web')
        self.open_page.setMaximumWidth(150)
        self.open_page.clicked.connect(self.open_nightly_website_function)


        # INSTALL BUTTON
        self.nightly_install = QPushButton('Install')
        #self.nightly_install.setMaximumWidth(150)
        self.nightly_install.clicked.connect(self.nightly_install_function)


        # ADD WIDGETS TO LAYOUT
        self.topLayout.addWidget(self.cbox_nightly_productName)
        self.topLayout.addWidget(self.cbox_nightly_platformName)
        self.topLayout.addWidget(self.cbox_nightly_version)
        self.topLayout.addWidget(self.cbox_install_type)
        self.topLayout.addWidget(self.open_page)

        self.bottomLayout.addWidget(self.nightly_install) 

        self.mainLayout.addLayout(self.topLayout)
        self.mainLayout.addLayout(self.middleLayout)
        self.mainLayout.addLayout(self.bottomLayout)

        self.groupBox_Nightly.setLayout(self.mainLayout)


    def Bottom_Layout(self, widget_id = 0, path=None): 

        self.ftp_path = path

        while True:
            
            try:
                self.cg_nightlies.ftp.cwd(path)
                items = self.cg_nightlies.ftp.nlst()

                #SORT NIGHTLY/STABLE/BETA/RELEASE
                items = sorted(items, reverse=True)

                def sort_function(input_value):
                    if input_value.startswith('n'):
                        return 0
                    elif input_value.startswith('s'):
                        return 1
                    else:
                        return 2

                if 'nightly' in items or 'stable' in items or 'alpha' in items or 'beta' in items or 'release' in items:
                    
                    items = sorted(items, key=sort_function )


                #REMOVE SOME OF THE ITEMS FROM MENUS DEPENDING ON THE OPERATING SYSTEM
                remove_items = []

                if platform.system() == 'Windows':
                    
                    #INSTALL TYPE = STANDARD
                    if self.cbox_install_type.currentText() == 'Standard Install':

                        for item in items:
                            if 'release_notes' in item or '.txt' in item or '.7z' in item or 'archive.zip' in item or 'mavericks' in item or \
                                    'centos' in item or 'linux' in item or '_zip.' in item or 'dmg' in item or 'json' in item or \
                                    'changelog' in item or 'mac' in item or 'scenes' in item or \
                                    ('houdini' in item and 'install' not in item) or \
                                    ('appsdk' in item and 'zip' in item) or \
                                    ('revit' in item and 'edge' in item):

                                remove_items.append(item)

                     #INSTALL TYPE = ZIP
                    else:
                        for item in items:
                            if 'release_notes' in item or '.txt' in item or 'mavericks' in item or 'centos' in item or 'linux' in item \
                                or 'install.zip' in item or 'dmg' in item or 'json' in item or 'changelog' in item or '_install_windows.zip' in item \
                                or '_mac.zip' in item or 'mac_' in item or '.exe' in item:
                                remove_items.append(item)

                if platform.system() == 'Darwin':

                    #INSTALL TYPE = STANDARD
                    if self.cbox_install_type.currentText() == 'Standard Install':

                        for item in items:
                            if '.exe' in item or '.txt' in item:
                                remove_items.append(item)
                            
                            if '.zip' in item:
                                if 'mavericks' not in item and 'snow_leopard' not in item and  'mac' not in item:
                                    remove_items.append(item)

                                if 'mac' in item and 'install' not in item:
                                    remove_items.append(item)

                                if 'mavericks' in item and 'install' not in item:
                                    remove_items.append(item)

                    #INSTALL TYPE = ZIP
                    else:
                        for item in items:
                            
                            if 'release_notes' in item or '.txt' in item:
                                remove_items.append(item)

                            if 'maya' in item:
                                if not (('archive' in item) and ('mavericks' in item)):
                                    remove_items.append(item) 

                            if 'houdini' in item:
                                if 'install' in item or 'windows' in item or 'linux' in item:
                                    remove_items.append(item)



                if platform.system() == 'Linux':
                    
                    #INSTALL TYPE = STANDARD
                    if self.cbox_install_type.currentText() == 'Standard Install':

                        for item in items:
                            # if '.exe' in item or '.txt' in item or '_windows.zip' in item or '_mac.zip' in item or \
                            #     '_archive.zip' in item or 'mavericks' in item or 'notes' in item:

                            if 'notes' in item or '.txt' in item or 'changelog' in item:
                                remove_items.append(item)

                            if 'maya' in item:
                                if not (('linux' in item and 'install' in item) or ('centos' in item and 'install' in item)):
                                    remove_items.append(item)

                            elif 'houdini' in item:
                                if 'install_linux' not in item:
                                    remove_items.append(item)

                            elif 'vraystd' in item:
                                if not (('centos' in item and 'install' in item) or ('linux' in item and 'install' in item)) :
                                    remove_items.append(item)
                            
                            elif 'nuke' in item:
                                if not (('centos' in item and 'install' in item) or ('linux' in item and 'install' in item)):
                                    remove_items.append(item)
                            
                        #     if '.zip' in item:
                        #         if 'mavericks' not in item and 'snow_leopard' not in item and  'mac' not in item:
                        #             remove_items.append(item)

                        #         if 'mac' in item and 'install' not in item:
                        #             remove_items.append(item)

                        #         if 'mavericks' in item and 'install' not in item:
                        #             remove_items.append(item)

                    #INSTALL TYPE = ZIP
                    else:
                        for item in items:

                            if 'notes' in item or '.txt' in item or 'changelog' in item:
                                remove_items.append(item)

                            # if 'maya' in item:
                            #     if not ('linux' in item and 'archive' in item): #'install.zip' in item or '_x64_' in item:
                            #         remove_items.append(item)

                            if 'maya' in item:
                                if not (('centos' in item or 'linux' in item) and 'archive' in item): #'install.zip' in item or '_x64_' in item:
                                    remove_items.append(item)
                            
                            if 'houdini' in item:
                                if 'windows.zip' in item or '_mac.zip' in item or '_install_linux.zip' in item:
                                    remove_items.append(item)

                            if 'nuke' in item:
                                if not ('linux' in item and 'archive' in item) and not ('centos' in item and 'archive' in item) : #'install.zip' in item or '_x64_' in item:
                                    remove_items.append(item)

                            if 'vraystd' in item:
                                if 'install.zip' in item or '_x64_' in item:
                                    remove_items.append(item)
                    


                #REMOVE ITEMS
                for item in remove_items:
                    items.remove(item)

                    #PREVENT REMOVING ALL THE ITEMS BECAUSE THE LOGIC FOR BULDING THE BOTTOM MENU NEEDS ALL THE WIDGETS IN ORDER TO WORK CORRECTLY
                    #IF THE BUILDS WIDGET LENGHT BECOMES ZERO IT WILL BE REMOVED FROM THE INTERFACE AND IT WILL NO LONGER BE RESTORED
                    if len(items) == 0:
                        items.append('No available bulds!')


                path = items[0]
                self.ftp_path += path + '/'
                self.add_cbox = QComboBox()
                #LIMIT COMBOBOX ITEMS: https://stackoverflow.com/questions/11252299/pyqt-qcombobox-setting-number-of-visible-items-in-dropdown
                self.add_cbox.setStyleSheet("QComboBox { combobox-popup: 0; }")
                # self.add_cbox.setMaxVisibleItems(20)
                self.add_cbox.setObjectName("cbox{}".format(widget_id))
                self.add_cbox.addItems(items)
                self.add_cbox.currentTextChanged.connect(lambda: self.add_cbox_function())

                self.middleLayout.addWidget(self.add_cbox)

                # print(self.add_cbox.count())
                
                

            except:

                #THIS HAS TO BE REWORKED, CURRENTLY IT CRASHES WHEN MODO AND BLENDER ARE SELECTED AS NIGHTLY PRODUCT
                #PROBABLY DUE TO MISSING BUILDS IN THEIR DEFAULT FOLDERS, HENCE THE ITEMS VAR IS EMPTY
                try:
                    build_file = items[0]
                    platform_version = self.getPlatformVersion(platformName=self.cbox_nightly_platformName.currentText(),
                                                                build_file=build_file)

                    CG.statusBar.update_versions(productName=self.cbox_nightly_productName.currentText(),
                                                productVersion =self.cbox_nightly_version.currentText(),
                                                platformName=self.cbox_nightly_platformName.currentText(),
                                                platformVersion=platform_version)
                except:
                    pass

                break

            widget_id += 1  

        
    ###############################################################################
    #NIGHTLY BUILD GROUP FUNCTIONS
    ###############################################################################


    def cbox_nightly_productName_function(self):
        logging.debug("1-run cbox_nightly_productName_function")

        product_name = self.cbox_nightly_productName.currentText()

        
        #CLEAR/HIDE COMBOBOXES DEPENDING ON SELECTED PRODUCT
        self.cbox_nightly_platformName.clear()
        self.cbox_nightly_version.clear()        

        #ADD PLATFORM NAMES
        for key in self.cg_nightlies.productsNames[product_name]:

            #remove product names for OSX/LINUX
            if platform.system() == 'Windows':
                self.cbox_nightly_platformName.addItem(key)

            elif platform.system() == 'Darwin':
                if key == 'Maya' or key == 'Houdini' or key == 'Modo' or key == 'Cinema 4D' or key == 'Standalone' or key == 'SketchUp':
                    self.cbox_nightly_platformName.addItem(key)

            elif platform.system() == 'Linux':
                if key == 'Maya' or key == 'Houdini' or key == 'Standalone' or key == 'Nuke':
                    self.cbox_nightly_platformName.addItem(key)

        # print(self.cbox_nightly_productName.currentText())


    def cbox_nightly_platformName_function(self):
        logging.debug("2-run cbox_nightly_platformName_function")

        #CLEAR OTHER COMBOBOXES
        self.cbox_nightly_version.clear()
        
        try:
            product_name = self.cbox_nightly_productName.currentText()
            platform_name = self.cbox_nightly_platformName.currentText()
            versions = self.cg_nightlies.productsNames[product_name][platform_name]
            self.cbox_nightly_version.addItems(versions)
        except:
            pass


    def cbox_nightly_version_function(self):
            logging.debug('3-run cbox_nightly_version_function')
            product_name = self.cbox_nightly_productName.currentText()
            platform_name = self.cbox_nightly_platformName.currentText()

            #HIDE ZIP-INSTALLATIONS FOR PLATFORMS WHERE ZIP-INSTALL IS UNSUPPORTED   
            if product_name in ['V-Ray', 'Phoenix FD']:  
                if platform_name in ['3ds Max','SketchUp','Rhino','Revit','Modo','Unreal','Blender']:

                    self.cbox_install_type.setCurrentIndex(0)
                    self.cbox_install_type.hide()
                else:
                    
                    self.cbox_install_type.setCurrentIndex(0)
                    self.cbox_install_type.show()
            
            else:
                self.cbox_install_type.setCurrentIndex(0)
                self.cbox_install_type.hide()

            #TRIGGER INSTALL-TYPE FUNCTION IN ORDER TO ADD/UPDATE MIDDLE-ROW WIDGETS TO UI
            self.cbox_install_type_function()
            

    def cbox_install_type_function(self):
            
        product_name = self.cbox_nightly_productName.currentText()
        platform_name = self.cbox_nightly_platformName.currentText()
        nightly_version = self.cbox_nightly_version.currentText()

        
        #REMOVE PREVIOUSLY CREATED WIDGETS IN MIDDLE LAYOUT
        number_of_cboxes = self.middleLayout.count()
        for i in range(number_of_cboxes):
            item = self.middleLayout.itemAt(i).widget().deleteLater()
            # print(item)
            # item.setParent(None)
        


        if product_name and platform_name and nightly_version:
            self.ftp_root = self.cg_nightlies.productsNames[product_name][platform_name][nightly_version]


        logging.info('<NIGHTLY> Product Name = {0}'.format(product_name))
        logging.info('<NIGHTLY> Product Version = {0}'.format(nightly_version))
        logging.info('<NIGHTLY> Platform Name = {0}'.format(platform_name))
        logging.info('<NIGHTLY> FTP Path = {0}'.format(self.ftp_root))

        # self.cbox_nightly_build_type.addItems(ftp_roots)
        self.Bottom_Layout(widget_id = 0, path=self.ftp_root)

        # print('>'*15 ,self.groupBox_Nightly.children())   

    def add_cbox_function(self):
        
        #THIS FUNCTION OPERATES ON MULTIPLE COMBOBOXES. THE SENDER FUNCTIONALITY ALLOWS TO FIND OUT WHICH COMBOBOX EXECUTES THE FUNCTION
        sender = self.sender()
        # print(sender.currentText(), sender.objectName())

        # #GET PARRENT WIDGET
        # parent_obj = sender.parent()
        # childs = parent_obj.children()
        # # print(childs)

        # for child in childs:
        #     print(child.objectName())

        #     try:
        #         print(child.currentText())
        #     except:
        #         pass

        self.ftp_path = self.ftp_root
        sender_id = int(sender.objectName()[4:])
        parent_widgets = sender.parent().children()
        number_of_cbox_widgets = 0


        #DELETE CBOXES ON THE RIGHT SIDE OF THE SELECTED CBOX AND CALCULATE PATH TO IT
        for widget in parent_widgets:
            if 'cbox' in widget.objectName():
                number_of_cbox_widgets += 1
                widget_id = int(widget.objectName()[4:])

                #IF WIDGET-ID GREATER THAN SENDER-ID, I.E. IF WIDGET IS ON THE RIGHT SIDE OF THE SENDER-ID, DELETE IT
                if sender_id < widget_id:
                    # print(sender_id, widget_id)
                    widget.deleteLater()
                    widget_id -=1

                #IF WIDGET IS ON THE LEFT SIDE, ADD IT'S VALUE TO PATH
                else:
                    # print(widget.currentText())
                    self.ftp_path += widget.currentText() + '/'


        #IF CBOX HAS BEEN REMOVED, GENERATE ANOTHER ONE ON IT'S PLACE
        # print('sender_id={0}, number_of_cbox_widgets={1}'.format(sender_id,number_of_cbox_widgets))

        #GENERATE NEW CBOXES ONLY IF CURRENT CBOX IS NOT THE RIGHT MOST ONE, AND IF CURRENT CBOX IS NOT THE ONLY ONE
        if (sender_id != number_of_cbox_widgets - 1) or (sender_id == 0 and number_of_cbox_widgets -1 == 0):
            self.Bottom_Layout(widget_id = widget_id +1 , path= self.ftp_path)
        

        # print(sender_id, number_of_cbox_widgets)
        # print(self.ftp_path)

        #UPDATE STATUS BAR
        build_file = self.ftp_path.split('/')[-2]
        platform_version = self.getPlatformVersion(platformName=self.cbox_nightly_platformName.currentText(),
                                                    build_file=build_file)

        CG.statusBar.update_versions(productName=self.cbox_nightly_productName.currentText(),
                                    productVersion = self.cbox_nightly_version.currentText(),
                                    platformName=self.cbox_nightly_platformName.currentText(),
                                    platformVersion=platform_version)

        # sender.deleteLater()


    def nightly_install_function(self):

        logging.info('FTP Path = {0}'.format(self.ftp_path))
        product_name = self.cbox_nightly_productName.currentText()
        download_path = CG.download_path

        self.build_file = self.ftp_path.split('/')[-2]
        self.platform_version = self.getPlatformVersion(platformName=self.cbox_nightly_platformName.currentText(),
                                                        build_file=self.build_file)

        #CHECK IF HOST APP IS AVAILABLE:
        platformName=self.cbox_nightly_platformName.currentText()
        productName = self.cbox_nightly_productName.currentText()
        host_app_is_installed = CG_Utilities.instance.check_host_app_is_installed(productName=productName, platformName=platformName, platformVersion=self.platform_version, App=CG)
        

        if host_app_is_installed == True:
            # build = self.cbox_nightly_builds.currentText()

            #NEEDED IN ORDER TO RUN DOWNLOAD PROCESS AS A SEPARATE THREAD
            self.threadpool = QThreadPool()
            logging.debug("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())


            self.download_build = CG_Nightlies.NightlyDownload(CG.download_path, self.build_file, self.ftp_path)
            # CG_Nightlies.instance.download_file(CG.download_path, build_file)
            

            #SIGNALS NEEDED TO UPDATE PROGRESS BAR, TITLE BAR, AND DETERMINE DONWLOAD COMPLETION
            # self.download_build.signals.finished.connect(lambda: CG_Utilities.install(download_path=CG.download_path, build_file=self.build_file,
            #         productName=product_name, productVersion=product_version, platformName=platform_name, platformVersion=platform_version))

            self.download_build.signals.finished.connect(self.run_installer)

            # self.download_build.signals.progress_signal.connect(self.progress_update)
            # self.download_build.signals.total_mb_signal.connect(self.total_mb_update)
            # self.download_build.signals.downloaded_mb_signal.connect(self.downloaded_mb_update)

            # self.download_build.signals.progress_data.connect(self.progress_update)
            self.download_build.signals.progress_data_signal.connect(CG.tab_MAIN.progress_bar_update)

            self.threadpool.start(self.download_build)

        else:
            logging.info('Installation canceled')

    def run_installer(self):


        if self.cbox_install_type.currentText() == 'Standard Install':
            CG_Utilities.instance.install(download_path=CG.download_path,
                            build_file=self.build_file,
                            productName=self.cbox_nightly_productName.currentText(),
                            productVersion=self.cbox_nightly_version.currentText(),
                            platformName=self.cbox_nightly_platformName.currentText(),
                            platformVersion=self.platform_version,
                            silent_install=CG.tab_MAIN.tab_Install.rbtn_install_silent.isChecked(),
                            start_host_app= CG.tab_MAIN.tab_Install.chbox_start_host_app_after_install.isChecked(),
                            remove_files_after_install = CG.tab_MAIN.tab_Settings.qcheck_remove_nightly_files.isChecked(),
                            quit_after_install=CG.tab_MAIN.tab_Install.qcheck_quit_after_installation.isChecked(),
                            App = CG)
        else:
            CG_ZIP_Installer.instance.install(productName=self.cbox_nightly_productName.currentText(),
                                                productVersion=self.cbox_nightly_version.currentText(),
                                                platformName=self.cbox_nightly_platformName.currentText(),
                                                platformVersion=self.platform_version,
                                                download_path=CG.download_path,
                                                build_full_path= CG.download_path + self.build_file,
                                                build_name = self.build_file,
                                                remove_zip_files= CG.tab_MAIN.tab_Settings.qcheck_remove_zip_files.isChecked(),
                                                start_host_app=CG.tab_MAIN.tab_Install.chbox_start_host_app_after_install.isChecked(),
                                                App = CG)
                                                
        
    

    def getPlatformVersion(self, platformName='', build_file=''):
        if platformName == '3ds Max':
            start_idx = build_file.find('_max') + 4
            end_idx = build_file.find('_', start_idx)
            version = build_file[start_idx : end_idx]
            return version

        elif platformName == 'Maya':
            start_idx = build_file.find('_maya') + 5
            end_idx = build_file.find('_', start_idx)
            version = build_file[start_idx : end_idx]
            return version

        elif platformName == 'Houdini':
            start_idx = build_file.find('_houdini') + 8
            end_idx = build_file.find('_', start_idx)
            version = build_file[start_idx : end_idx]
            return version

        elif platformName == 'Nuke':
            start_idx = build_file.find('_nuke') + 5
            end_idx =  build_file.find('_', start_idx)
            version = build_file[start_idx : end_idx]
            return version

        elif platformName == 'Cinema 4D':
            start_idx = build_file.find('_c4d') + len('_c4d')
            end_idx =  build_file.find('_', start_idx)
            version = build_file[start_idx : end_idx].upper()
            return version
        
        return ''

    def open_nightly_website_function(self):
        logging.info('https://nightlies.chaosgroup.com/#' + self.ftp_path.rsplit('/',2)[0])

        url = QUrl('https://nightlies.chaosgroup.com/#' + self.ftp_path.rsplit('/',2)[0])
        QDesktopServices.openUrl(url)
    
                

class Group_ZIP(QWidget):


    def __init__(self):
        super().__init__()

        self.groupBox_ZIP_Installer = QGroupBox("Arbitrary Location Installer (zip/exe)")
        #self.groupBox_ZIP_Installer.setStyleSheet("QGroupBox { font-size: 9px; } ")

        mainLayout = QGridLayout()

        #ADD WIDGETS
        self.productName = QLabel("Chaos Product:")
        self.productName_value = QLineEdit()
        self.productName_value.setReadOnly(True)

        self.product_version = QLabel("Version:")
        self.product_version_value = QLineEdit()
        self.product_version_value.setReadOnly(True)

        self.platformName = QLabel("Host App:")
        self.platformName_value = QLineEdit()
        self.platformName_value.setReadOnly(True)

        self.platformVersion = QLabel("Version:")
        self.platformVersion_value = QLineEdit()
        self.platformVersion_value.setReadOnly(True)
        
        self.phoenix_vray_version = QLabel("V-Ray Version:")
        self.phoenix_vray_version_value = QLineEdit()
        self.phoenix_vray_version_value.setReadOnly(True)
        

        self.drag_and_drop = Group_ZIP_DropButton()
        self.zip_install_btn = QPushButton('Install')
        self.zip_install_btn.clicked.connect(self.zip_install_btn_function)

        #ADD WIDGETS TO LAYOUT
        mainLayout.addWidget(self.productName, 1,0)
        mainLayout.addWidget(self.productName_value,1,1)
        mainLayout.addWidget(self.product_version,1,2)
        mainLayout.addWidget(self.product_version_value, 1,3)
        mainLayout.addWidget(self.platformName, 1,4)
        mainLayout.addWidget(self.platformName_value,1,5)
        mainLayout.addWidget(self.platformVersion, 1,6)
        mainLayout.addWidget(self.platformVersion_value,1,7)
        mainLayout.addWidget(self.phoenix_vray_version, 1,8)
        mainLayout.addWidget(self.phoenix_vray_version_value,1,9)
        mainLayout.addWidget(self.drag_and_drop, 0, 0, 1, 9)
        mainLayout.addWidget(self.zip_install_btn, 2, 0, 1, 9)



        # mainLayout.setColumnStretch(0, 1)
        # mainLayout.setColumnStretch(1, 1)
        # mainLayout.setColumnStretch(2, 3)

        #HIDE WIDGETS
        self.productName.hide()
        self.productName_value.hide()
        self.product_version.hide()
        self.product_version_value.hide()
        self.platformName.hide()
        self.platformName_value.hide()
        self.platformVersion.hide()
        self.platformVersion_value.hide()
        self.phoenix_vray_version.hide()
        self.phoenix_vray_version_value.hide()
        self.zip_install_btn.hide()

        self.groupBox_ZIP_Installer.setLayout(mainLayout)

    def zip_install_btn_function(self):
        

        #CHECK IF HOST APP IS AVAILABLE:
        platformName=self.platformName_value.text()
        productName = self.productName_value.text()
        platformVersion = self.platformVersion_value.text()
        host_app_is_installed = CG_Utilities.instance.check_host_app_is_installed(productName=productName, platformName=platformName, platformVersion=platformVersion, App=CG)

        if host_app_is_installed == True:
            
            try:
                file_ext = self.drag_and_drop.build_name[-4:]
            except:
                file_ext = self.build_name[-4:]
            

            # CG_Utilities.killHostApp(productName=self.productName_value.text(),
            #                         platformName=self.platformName_value.text(),
            #                         platformVersion=self.platformVersion_value.text())

            #EXTRACT ZIP FILE AND START HOST APP
            
            # if file_ext.endswith('.zip'):
                
            if self.productName_value.text() == 'V-Ray':
                CG_ZIP_Installer.instance.install(productName=self.productName_value.text(),
                                                productVersion=self.product_version_value.text(),
                                                platformName=self.platformName_value.text(),
                                                platformVersion= self.platformVersion_value.text(),
                                                download_path=CG.download_path,
                                                build_full_path= self.drag_and_drop.build_full_path,
                                                build_name = self.drag_and_drop.build_name,
                                                remove_zip_files= CG.tab_MAIN.tab_Settings.qcheck_remove_zip_files.isChecked(),
                                                App = CG)
                

            elif self.productName_value.text() == 'Phoenix FD':
                    CG_ZIP_Installer.instance.install(productName=self.productName_value.text(),
                                                    productVersion=self.product_version_value.text(),
                                                    platformName=self.platformName_value.text(),
                                                    platformVersion= self.platformVersion_value.text(),
                                                    download_path=CG.download_path,
                                                    build_full_path= self.drag_and_drop.build_full_path,
                                                    build_name = self.drag_and_drop.build_name,
                                                    remove_zip_files= CG.tab_MAIN.tab_Settings.qcheck_remove_zip_files.isChecked(),
                                                    phoenix_vray_version=self.phoenix_vray_version_value.text(),
                                                    App = CG)

                
            # elif file_ext.endswith('.exe'):
            #     # build_path = 

            #     CG_Utilities.instance.install(download_path=self.drag_and_drop.file_path, 
            #                     build_file= self.drag_and_drop.file_name,
            #                     productName=self.productName_value.text(), 
            #                     productVersion= self.product_version.text(), 
            #                     platformName=self.platformName_value.text(),
            #                     platformVersion=self.platformVersion_value.text())


            # CG_ZIP_Installer.instance.startMaya(vray_from_zip_path=zip_path, maya_version=self.platformVersion_value.text())

        else:
            logging.info('Installation canceled')

        
class Group_ZIP_DropButton(QPushButton):

    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.setText("Drag and Drop / Browse Installation file (zip/exe)")
        self.setMinimumHeight(25)
        # self.setMaximumHeight(200)

        self.clicked.connect(self.browseFiles)

    
    def dragEnterEvent(self, file):

        if file.mimeData().hasFormat('text/uri-list'):
            file.accept()
        else:
            file.ignore()

        data = file.mimeData().urls()
        data = data[0].toString()
        self.setText(data)

    def dropEvent(self, file):

        logging.debug("ZIP dropEvent")
        #GET TEXT FROM DRAG AND DROP BUTTON: file:///C:/builds/1/vray_adv_43002_maya2018_x64.zip
        data = file.mimeData().urls()
        #CONVERT TEXT TO LOCAL PATH: file:///C:/builds/1/vray_adv_43002_maya2018_x64.zip > C:/builds/1/vray_adv_43002_maya2018_x64.zip
        self.build_full_path = data[0].toLocalFile()

        #GET FILENAME: C:/builds/1/vray_adv_43002_maya2018_x64.zip > vray_adv_43002_maya2018_x64.zip
        self.build_name = os.path.basename(self.build_full_path)

        logging.debug('build_name=' + self.build_name)
        self.showWidgets()

    def dragLeaveEvent(self, *args, **kwargs):
        self.setText("Drag and Drop / Browse Installation file (zip/exe)")


    def browseFiles(self):
        #('G:/Shared drives/3D SUPPORT/Scripts/Chaos-Installer/vray_adv_50050_maya2020_x64_30703_archive.zip', 'Archive files (*.zip)')
        self.build_full_path = QFileDialog.getOpenFileName(self, 'Select zip/exe build file', '',"Build files (*.zip *.exe)")[0]
        
        #IF CANCEL IS SELECTED, STOP HERE.
        if self.build_full_path != '':
            print(self.build_full_path)

            #GET FILENAME: C:/builds/1/vray_adv_43002_maya2018_x64.zip > vray_adv_43002_maya2018_x64.zip
            self.build_name = os.path.basename(self.build_full_path)

            #UPDATE BUTTON TEXT
            self.setText(self.build_full_path)

            self.showWidgets()


    def showWidgets(self):

        #GET VERSIONS DATA FROM FILE-NAME
        try:
            data = CG_ZIP_Installer.instance.getZipVersionsFromString(self.build_name)
        except:
            # pass
            CG_Utilities.instance.PyQTerrorMSG(error_msg = 'Cannot recognize zip-installation!', 
                    more_information='Make sure the proper zip installation file is dropped!', App=CG)
            self.hideVersionsWidgets()
            return

        #UPDATE WIDGETS
        CG.tab_MAIN.tab_Install.group_zip.productName_value.setText(data['productName'])
        CG.tab_MAIN.tab_Install.group_zip.product_version_value.setText(data['productVersion'])
        CG.tab_MAIN.tab_Install.group_zip.platformName_value.setText(data['platformName'])
        CG.tab_MAIN.tab_Install.group_zip.platformVersion_value.setText(data['platformVersion'])   
       
        #HIDE/SHOW WIDGETS
        CG.tab_MAIN.tab_Install.group_zip.productName.show()
        CG.tab_MAIN.tab_Install.group_zip.productName_value.show()
        CG.tab_MAIN.tab_Install.group_zip.product_version.show()
        CG.tab_MAIN.tab_Install.group_zip.product_version_value.show()
        CG.tab_MAIN.tab_Install.group_zip.platformName.show()
        CG.tab_MAIN.tab_Install.group_zip.platformName_value.show()
        CG.tab_MAIN.tab_Install.group_zip.platformVersion.show()
        CG.tab_MAIN.tab_Install.group_zip.platformVersion_value.show()
        CG.tab_MAIN.tab_Install.group_zip.zip_install_btn.show()

        if data['productName'] == 'V-Ray':
            CG.tab_MAIN.tab_Install.group_zip.phoenix_vray_version.hide()
            CG.tab_MAIN.tab_Install.group_zip.phoenix_vray_version_value.hide()

        elif data['productName'] == 'Phoenix FD':
            CG.tab_MAIN.tab_Install.group_zip.phoenix_vray_version.show()
            CG.tab_MAIN.tab_Install.group_zip.phoenix_vray_version_value.setText(data['phoenixVrayVersion'])
            CG.tab_MAIN.tab_Install.group_zip.phoenix_vray_version_value.show()
           

    def hideVersionsWidgets(self):
        CG.tab_MAIN.tab_Install.group_zip.productName.hide()
        CG.tab_MAIN.tab_Install.group_zip.productName_value.hide()
        CG.tab_MAIN.tab_Install.group_zip.product_version.hide()
        CG.tab_MAIN.tab_Install.group_zip.product_version_value.hide()
        CG.tab_MAIN.tab_Install.group_zip.platformName.hide()
        CG.tab_MAIN.tab_Install.group_zip.platformName_value.hide()
        CG.tab_MAIN.tab_Install.group_zip.platformVersion.hide()
        CG.tab_MAIN.tab_Install.group_zip.platformVersion_value.hide()
        CG.tab_MAIN.tab_Install.group_zip.phoenix_vray_version.hide()
        CG.tab_MAIN.tab_Install.group_zip.phoenix_vray_version_value.hide()



class Tab_Uninstaller(QWidget):

    def __init__(self):
        super().__init__()
        mainLayout = QVBoxLayout()
        layout_bottom = QHBoxLayout()

        layout_radio_btns = QHBoxLayout()
        layout_radio_btns.setAlignment(Qt.AlignLeft)

        layout_update_btn = QHBoxLayout()
        layout_update_btn.setAlignment(Qt.AlignRight)

        #ADD RADIO BUTTONS
        self.rbtn_uninstall_silent = QRadioButton("Silent Uninstall")
        self.rbtn_uninstall_silent.setChecked(True)
        rbtn_uninstall_gui = QRadioButton("GUI Uninstall")

        btn_reset = QPushButton("Update")
        btn_reset.clicked.connect(self.add_update_table_items)

        #SET TABLE PARAMETERS
        self.table = QTableWidget()
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setColumnCount(3)
        # self.table.setRowCount(len(CG_Uninstall.instance.product))
        self.table.verticalHeader().hide()
        self.table.setHorizontalHeaderLabels(['Product','Version','Uninstall'])
        self.table.setFrameStyle(QFrame.NoFrame)
        # self.table.setShowGrid(False)

        #SET TABLE COLUMN RESIZING   
        header = self.table.horizontalHeader()
        header.setStyleSheet('font-weight: bold')
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        # header.setSectionResizeMode(1, QHeaderView.Stretch)

        #ADD DATA TO TABLE
        self.add_update_table_items()

        #ADD WIDGET TO LAYOUT
        layout_radio_btns.addWidget(self.rbtn_uninstall_silent)
        layout_radio_btns.addWidget(rbtn_uninstall_gui)
        layout_update_btn.addWidget(btn_reset)
       
        mainLayout.addWidget(self.table)
        layout_bottom.addLayout(layout_radio_btns)
        layout_bottom.addLayout(layout_update_btn)

        # mainLayout.addSpacing(5)
        mainLayout.addLayout(layout_bottom)

        self.setLayout(mainLayout)


    def add_update_table_items(self):

        #RESET TABLE ROWS
        self.table.setRowCount(0)
        
        #GET NEW INSTANCE OF CG_UNINSTALL TO UPDATE ANY CHANGES
        self.cg_uninstall = CG_Uninstall.CG_Uninstall()
        num_of_rows = len(self.cg_uninstall.product)

        #GET NUMBER OF CHAOS PRODUCTS 
        self.table.setRowCount(num_of_rows)

        #ADD CHAOS PRODUCTS TO TABLE
        for i in range (len(self.cg_uninstall.product)):

            # print(self.cg_uninstall.platformName[i], self.cg_uninstall.platformVersion[i])

            product = self.cg_uninstall.product[i]
            product_version = self.cg_uninstall.version[i]

            self.table.setItem(i, 0, QTableWidgetItem(product))
            self.table.setItem(i, 1, QTableWidgetItem(product_version))

            btn_uninstall_gui = QPushButton("Uninstall")
            # btn_uninstall_gui.objectName = self.cg_uninstall.uninstall_string[i]
            btn_uninstall_gui.objectName = i
            btn_uninstall_gui.clicked.connect(self.btn_uninstall_gui_function)

            self.table.setCellWidget(i, 2, btn_uninstall_gui)

    def btn_uninstall_gui_function(self):

        #GET THE SENDER BUTTON ID
        sender = self.sender()
        # print(sender.objectName)
        sender_id = int(sender.objectName)

        #FIND UNINSTALL DETAILS FOR THE CLICKED UNINSTALL ID BUTTON
        productName = self.cg_uninstall.productName[sender_id]
        uninstall_string = self.cg_uninstall.uninstall_string[sender_id]
        platformName = self.cg_uninstall.platformName[sender_id]
        platformVersion = self.cg_uninstall.platformVersion[sender_id]

        CG.statusBar.showMessage('Uninstalling started')
        # print(self.rbtn_uninstall_silent.isChecked())

        #RUN UNINSTALL PROCESS
        output_msg = CG_Uninstall.instance.uninstall(productName=productName,
                                                    platformName=platformName,
                                                    platformVersion=platformVersion,
                                                    uninstall_string=uninstall_string,
                                                    silent_uninstall=self.rbtn_uninstall_silent.isChecked(),
                                                    App=CG)

        CG.statusBar.showMessage(output_msg)
        
        #UPDATE TABLE
        self.add_update_table_items()

        #LOGGING MSG
        logging.info('Unintall Tab Updated!')


class Tab_License(QWidget):

    def __init__(self):
        super().__init__()

        #FIRST LAYOUT

        self.mainLayout = QFormLayout()
        self.mainLayout.setVerticalSpacing(25)
        self.mainLayout.setHorizontalSpacing(25)
        self.mainLayout.setFormAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.mainLayout.setContentsMargins(50,0,50,0)

        
        #DEFINE WIDGETS
        self.qlabel_license_server_address = QLabel('License Server IP Address (localhost | 10.0.0.24):')
        self.qline_license_server_address = QLineEdit('127.0.0.1')

        self.qlabel_license_server_port = QLabel('License Server Port:')
        self.qline_license_server_port = QLineEdit('30304')

        self.qlabel_update_interval = QLabel('Update time (seconds):')
        self.qline_update_interval = QLineEdit('3')

        self.qlabel_license_server_version = QLabel('License server version:')
        self.qlabel_license_server_version.hide()

        self.qline_license_server_version = QLineEdit()
        self.qline_license_server_version.hide()
        self.qline_license_server_version.setReadOnly(True)

        self.btn_start_license_listener = QPushButton('Start License Listener')
        self.btn_start_license_listener.clicked.connect(self.btn_start_license_listener_function)

        self.btn_stop_license_listener = QPushButton('Stop License Listener')
        self.btn_stop_license_listener.clicked.connect(self.btn_stop_license_listener_function)
        self.btn_stop_license_listener.hide()

        self.qlabel_engaged_licenses = QLabel('Engaged Licenses:')
        self.qlabel_engaged_licenses.hide()
        self.qline_engaged_licenses = QTextEdit()
        self.qline_engaged_licenses.hide()
        self.qline_engaged_licenses.setReadOnly(True)


        self.qtable_available_licenses = QTableWidget(self)  # Create a table
        # self.qtable_available_licenses.minimumHeight()
        self.qtable_available_licenses.hide()
        self.qtable_available_licenses.setColumnCount(4) 
        self.qtable_available_licenses.setFrameStyle(QFrame.NoFrame)
        self.qtable_available_licenses.setEditTriggers(QTableWidget.NoEditTriggers)
        self.qtable_available_licenses.verticalHeader().hide()
        #SET TABLE COLUMN RESIZING   
        header = self.qtable_available_licenses.horizontalHeader()
        header.setStyleSheet('font-weight: bold')
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        


        # ADD WIDGETS TO FIRST LAYOUT
        self.mainLayout.addRow(self.qlabel_license_server_address, self.qline_license_server_address)
        self.mainLayout.addRow(self.qlabel_license_server_port, self.qline_license_server_port)
        
        self.mainLayout.addRow(self.qlabel_update_interval, self.qline_update_interval)
        self.mainLayout.addRow(self.btn_start_license_listener)


        #SET WIDGET LAYOUT
        self.setLayout(self.mainLayout)


    #CLICK BUTTONS FUNCTIONS
    def btn_start_license_listener_function(self):
        
        #CHECK LICENSE SERVER STATUS
        lic_server_status = self.get_lic_server_status()
        if lic_server_status == 'offline':
            return
        
        #RESIZE LAYOUT
        self.mainLayout.setVerticalSpacing(5)
        self.mainLayout.setContentsMargins(10,10,10,10)

        #REMOVE WIDGETS 
        for i in range(self.mainLayout.rowCount()):
            self.mainLayout.takeRow(0)

        #ADD WIDGETS
        self.mainLayout.addRow(self.qlabel_license_server_address, self.qline_license_server_address)
        self.mainLayout.addRow(self.qlabel_license_server_port, self.qline_license_server_port)
        self.mainLayout.addRow(self.qlabel_license_server_version, self.qline_license_server_version)
        self.mainLayout.addRow(self.qlabel_engaged_licenses, self.qline_engaged_licenses)
        self.mainLayout.addRow(self.qtable_available_licenses)
        self.mainLayout.addRow(self.btn_stop_license_listener)

        #HIDE/SHOW/LOCK/REMOVE WIDGETS
        self.qline_license_server_address.setReadOnly(True)
        self.qline_license_server_port.setReadOnly(True)
        self.qlabel_update_interval.hide()
        self.qline_update_interval.hide()
        self.qlabel_license_server_version.show()
        self.qline_license_server_version.show()
        self.qlabel_engaged_licenses.show()
        self.qline_engaged_licenses.show()
        self.btn_start_license_listener.hide()
        
        self.btn_stop_license_listener.show()
        self.qtable_available_licenses.show()

        #UPDATE DATA
        self.qlabel_license_server_address.setText('License Server IP Address:')
        self.update_engaged_licenses()
        self.qline_license_server_version.setText(self.lic_server.license_server_version)
        self.updateTimer()
        self.availabeLicenseFillTable()


    def btn_stop_license_listener_function(self):

        self.update_timer.stop()

        #RESIZE LAYOUT
        self.mainLayout.setVerticalSpacing(25)
        self.mainLayout.setContentsMargins(50,0,50,0)

        #REMOVE WIDGETS 
        for i in range(self.mainLayout.rowCount()):
            self.mainLayout.takeRow(0)
        
        # ADD WIDGETS TO FIRST LAYOUT
        self.mainLayout.addRow(self.qlabel_license_server_address, self.qline_license_server_address)
        self.mainLayout.addRow(self.qlabel_license_server_port, self.qline_license_server_port)
        self.mainLayout.addRow(self.qlabel_update_interval, self.qline_update_interval)
        self.mainLayout.addRow(self.btn_start_license_listener)

        
        #HIDE/SHOW/LOCK WIDGETS
        self.qline_license_server_address.setReadOnly(False)
        self.qline_license_server_port.setReadOnly(False)
        self.qlabel_update_interval.show()
        self.qline_update_interval.show()
        self.btn_start_license_listener.show()

        self.btn_stop_license_listener.hide()
        self.qtable_available_licenses.hide()
        self.qlabel_license_server_version.hide()
        self.qline_license_server_version.hide()
        self.qlabel_engaged_licenses.hide()
        self.qline_engaged_licenses.hide()

        #UPDATE DATA
        self.qlabel_license_server_address.setText('License Server IP Address (localhost | 10.0.0.24):')


    def availabeLicenseFillTable(self):

        licenses = self.lic_server.getAvailableOnlineLicenses()
        # print(licenses)

        self.qtable_available_licenses
        self.qtable_available_licenses.setRowCount(len(licenses))  # Set rows

        #Set table style
        # table.setStyleSheet("Background-color:rgb(100,100,100);border-radius:15px;")
        # stylesheet = "::section{Background-color:rgb(190,1,1);border-radius:14px;}"
        # table.horizontalHeader().setStyleSheet(stylesheet)


        # Set the table headers
        self.qtable_available_licenses.setHorizontalHeaderLabels(["Product", "Interface", "Render", "Network"])


        # Set the alignment to the headers
        self.qtable_available_licenses.horizontalHeaderItem(0).setTextAlignment(Qt.AlignLeft)
        self.qtable_available_licenses.horizontalHeaderItem(1).setTextAlignment(Qt.AlignHCenter)
        self.qtable_available_licenses.horizontalHeaderItem(2).setTextAlignment(Qt.AlignHCenter)
        self.qtable_available_licenses.horizontalHeaderItem(2).setTextAlignment(Qt.AlignHCenter)

        # Fill the table with licenses
        for row in range(len(licenses)):
            self.qtable_available_licenses.setItem(row, 0, QTableWidgetItem(licenses[row]['productLabel']))
            self.qtable_available_licenses.setItem(row, 1, QTableWidgetItem(str(licenses[row]['Interface'])))
            self.qtable_available_licenses.setItem(row, 2, QTableWidgetItem(str(licenses[row]['Render'])))
            self.qtable_available_licenses.setItem(row, 3, QTableWidgetItem(str(licenses[row]['Network'])))
            #ALIGN LICENSES IN THE MIDDLE
            self.qtable_available_licenses.item(row, 1).setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            self.qtable_available_licenses.item(row, 2).setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            self.qtable_available_licenses.item(row, 3).setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        # Do the resize of the columns by content
        self.qtable_available_licenses.resizeColumnsToContents()


    def updateTimer(self):
        logging.info('Update timer started...')
        self.update_interval = int(self.qline_update_interval.text()) * 1000
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_engaged_licenses)
        self.update_timer.start(self.update_interval)
        

    def update_engaged_licenses(self):

        #IF LICENSE SERVER NOT FOUND TERMINATE
        lic_server_status = self.get_lic_server_status()
        if lic_server_status == 'offline':
            try:
                self.update_timer.stop()
            except:
                pass

            self.btn_stop_license_listener_function()
            return

        self.engaged_licenses = self.lic_server.getLicenses()
        self.qline_engaged_licenses.setText(self.engaged_licenses)

        text_height = self.engaged_licenses.count('\n')
        if text_height == 0:
            self.qline_engaged_licenses.setFixedHeight(25)
        elif text_height < 5:
            self.qline_engaged_licenses.setFixedHeight(18*(text_height + 1))
        else:
            self.qline_engaged_licenses.setFixedHeight(18*5)

        logging.info('Update Licenses ...')

    
    def get_lic_server_status(self):

        self.lic_server = CG_License.CG_License_Listener(license_server_address=self.qline_license_server_address.text(),
                                                        license_server_port=self.qline_license_server_port.text())

        if self.lic_server.license_status == 'offline':
            error_msg = 'Cannot find license server: {}!'.format(self.qline_license_server_address.text())
            more_information = 'Make sure the server is up and running!'
            CG_Utilities.instance.PyQTerrorMSG(error_msg=error_msg, more_information=more_information, App=CG)

        return self.lic_server.license_status


class Tab_Settings(QWidget):

    def __init__(self):
        super().__init__()

        self.store_settings = True

        first_layout = QHBoxLayout()

        second_layout = QHBoxLayout()
        second_layout.setAlignment(Qt.AlignLeft)

        third_layout = QHBoxLayout()
        third_layout.setAlignment(Qt.AlignLeft)
        mainLayout = QVBoxLayout()

        # groupBox_remove_file = QGroupBox()

        #CACHE WIDGETS
        qlabel_install_folder = QLabel("Cache Folder:")

        self.qline_install_folder = QLineEdit("Installation Folder Value")
        self.qline_install_folder.setReadOnly(True)
        self.qline_install_folder.setText(ChaosGroup.download_path)
        self.qline_install_folder.textChanged.connect(self.qline_install_folder_updated)

        btn_browse = QPushButton("Browse")
        btn_browse.clicked.connect(self.browse_btn_pressed)

        btn_open_cache_dir = QPushButton('Open')
        btn_open_cache_dir.clicked.connect(self.btn_open_cache_dir_function)

        #SIZE INFORMATION
        cache_dir_size = self.get_cache_dir_size(ChaosGroup.download_path)
        label_cache_dir_size = QLabel('Cache Size:')
        label_cache_dir_size.setMaximumWidth(80)

        qline_cache_dir_size = QLineEdit()
        qline_cache_dir_size.setReadOnly(True)
        qline_cache_dir_size.setMaximumWidth(90)

        label_free_space = QLabel('Free Space:')
        label_free_space.setMaximumWidth(80)

        qline_free_space = QLineEdit()
        qline_free_space.setReadOnly(True)
        qline_free_space.setMaximumWidth(90)

        
        if platform.system() == 'Windows':
            free = shutil.disk_usage(ChaosGroup.download_path[:3])[2]
        elif platform.system() == 'Darwin' or platform.system() == 'Linux':
            free = shutil.disk_usage('/')[2]
        free = free / (2**30)

        qline_cache_dir_size.setText(cache_dir_size)
        qline_free_space.setText(str(free)[:4] + ' GB')

        #REMOVE FILES AFTER INSTALLATION
        qlabel_remove_after_install = QLabel('Remove files after install:')
        self.qcheck_remove_official_files = QCheckBox("Official")
        self.qcheck_remove_nightly_files = QCheckBox("Nightly")
        self.qcheck_remove_zip_files = QCheckBox("ZIP")
        self.qcheck_dont_show_warning = QCheckBox("Don't show warning dialog")

        #DARK THEME
        self.chbox_enable_dark_theme = QCheckBox('Dark Theme')
        self.chbox_enable_dark_theme.stateChanged.connect(self.chbox_enable_dark_theme_function)

        #RESET SETTINGS
        self.btn_reset_settings = QPushButton('Reset Settings')
        self.btn_reset_settings.clicked.connect(self.btn_reset_settings_function)
        

        #ADD WIDGETS TO LAYOUT
        first_layout.addWidget(qlabel_install_folder)
        first_layout.addWidget(self.qline_install_folder)
        first_layout.addWidget(btn_browse)
        first_layout.addWidget(btn_open_cache_dir)

        second_layout.addWidget(label_cache_dir_size)
        second_layout.addWidget(qline_cache_dir_size)
        second_layout.addWidget(label_free_space)
        second_layout.addWidget(qline_free_space)

        third_layout.addWidget(qlabel_remove_after_install)
        third_layout.addWidget(self.qcheck_remove_official_files)
        third_layout.addWidget(self.qcheck_remove_nightly_files)
        third_layout.addWidget(self.qcheck_remove_zip_files)
        third_layout.addWidget(self.qcheck_dont_show_warning)

        mainLayout.addLayout(first_layout)
        mainLayout.addLayout(second_layout)
        mainLayout.addLayout(third_layout)

        mainLayout.addWidget(self.chbox_enable_dark_theme)
        mainLayout.addWidget(self.btn_reset_settings)

        
        #############################
        # self.groupBox_remove_file.setLayout(third_layout)

        #LOADING SETTINGS
        # print(ChaosGroup.settings_global.value("remove official files"))
        # print(eval(ChaosGroup.settings_global.value("remove official files").title()))
        try:
            settings_remove_official_files =  eval(ChaosGroup.settings_global.value("remove official files").title())
            self.qcheck_remove_official_files.setChecked(settings_remove_official_files)

            settings_remove_nightly_files =  eval(ChaosGroup.settings_global.value("remove nightly files").title())
            self.qcheck_remove_nightly_files.setChecked(settings_remove_nightly_files)

            settings_remove_zip_files =  eval(ChaosGroup.settings_global.value("remove zip files").title())
            self.qcheck_remove_zip_files.setChecked(settings_remove_zip_files)

            settings_enable_dark_theme = eval(ChaosGroup.settings_global.value("enable dark theme").title())
            self.chbox_enable_dark_theme.setChecked(settings_enable_dark_theme)

            settings_dont_show_warning = eval(ChaosGroup.settings_global.value("dont show warning dialog").title())
            self.qcheck_dont_show_warning.setChecked(settings_dont_show_warning)

        except:
            logging.warning("Cannot load Settings")

        # mainLayout.addStretch(1)
        self.setLayout(mainLayout)


    def browse_btn_pressed(self):
        self.browse_folder = str(QFileDialog.getExistingDirectory(self, "Select Temp Directory", ChaosGroup.download_path)) + "/"
        if self.browse_folder != '/':
            self.qline_install_folder.setText(self.browse_folder)

    def btn_open_cache_dir_function(self):

        path = self.qline_install_folder.text()

        if platform.system() == 'Windows':
            os.startfile(path)

        elif platform.system() == 'Darwin':
            subprocess.check_call(["open", "--", path])
            
        elif platform.system() == 'Linux':
            os.system('xdg-open "%s"' % path)

    def qline_install_folder_updated(self):
        ChaosGroup.download_path = self.browse_folder

    
    def get_cache_dir_size(self, dir):

        total_size = 0
        for root, dirs, files in os.walk(dir):
            for f in files:
                total_size += os.path.getsize(os.path.join(root, f))

        if total_size < 1000000000:
            total_size /= 1000000
            return str(total_size)[:6] + ' MB'

        else:
            total_size /= 1000000000
            return str(total_size)[:4] + ' GB'

    def storeSettings(self):

        if self.store_settings == True:

            ChaosGroup.settings_global.setValue('window size', CG.size())
            ChaosGroup.settings_global.setValue('window position', CG.pos())
            ChaosGroup.settings_global.setValue('install folder', ChaosGroup.download_path)
            ChaosGroup.settings_global.setValue('start host app', CG.tab_MAIN.tab_Install.chbox_start_host_app_after_install.isChecked())
            ChaosGroup.settings_global.setValue('remove official files', CG.tab_MAIN.tab_Settings.qcheck_remove_official_files.isChecked())
            ChaosGroup.settings_global.setValue('remove nightly files', CG.tab_MAIN.tab_Settings.qcheck_remove_nightly_files.isChecked())
            ChaosGroup.settings_global.setValue('remove zip files', CG.tab_MAIN.tab_Settings.qcheck_remove_zip_files.isChecked())
            ChaosGroup.settings_global.setValue('enable dark theme', CG.tab_MAIN.tab_Settings.chbox_enable_dark_theme.isChecked())
            ChaosGroup.settings_global.setValue('dont show warning dialog', CG.tab_MAIN.tab_Settings.qcheck_dont_show_warning.isChecked())


            #TRY BLOCK IS NEEDED IN CASE THE USER IS NOT LOGGED IN THE OFFICIAL SECTION AND THE MENUS ARE NOT AVAILABLE
            try:
                ChaosGroup.settings_global.setValue('official productName', CG.tab_MAIN.tab_Install.group_login.group_official.cbox_official_productName.currentText())
                ChaosGroup.settings_global.setValue('official platformName', CG.tab_MAIN.tab_Install.group_login.group_official.cbox_official_platformName.currentText())
                ChaosGroup.settings_global.setValue('official platformVersion', CG.tab_MAIN.tab_Install.group_login.group_official.cbox_official_platformVersion.currentText())
            except:
                pass

            ChaosGroup.settings_global.setValue('nightly productName', CG.tab_MAIN.tab_Install.group_nightly.cbox_nightly_productName.currentText())
            ChaosGroup.settings_global.setValue('nightly platformName', CG.tab_MAIN.tab_Install.group_nightly.cbox_nightly_platformName.currentText())
            ChaosGroup.settings_global.setValue('nightly nightlyVersion', CG.tab_MAIN.tab_Install.group_nightly.cbox_nightly_version.currentText())

            # if CG.log_in_test.qcheckbox_remember_credentials.isChecked():
            #     ChaosGroup.settings_global.setValue('username', CG.login_username)
            #     ChaosGroup.settings_global.setValue('password', CG.login_password)
                
            logging.info('Settings Saved!')
            
        else:
            logging.info('Settings Reset activated. Settings will not be saved!')

    def chbox_enable_dark_theme_function(self):
        if self.chbox_enable_dark_theme.isChecked() == True:
            #SET DARK THEME
            # Force the style to be the same on all OSs:
            #https://pythonbasics.org/pyqt-style/
            app.setStyle("Fusion")
            # app.setStyle("Windows")

            # Now use a palette to switch to dark colors:
            palette = QPalette()
            palette.setColor(QPalette.Window, QColor(53, 53, 53))
            palette.setColor(QPalette.WindowText, Qt.white)
            palette.setColor(QPalette.Base, QColor(25, 25, 25))
            palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
            palette.setColor(QPalette.ToolTipBase, Qt.white)
            palette.setColor(QPalette.ToolTipText, Qt.white)
            palette.setColor(QPalette.Text, Qt.white)
            palette.setColor(QPalette.Button, QColor(53, 53, 53))
            palette.setColor(QPalette.ButtonText, Qt.white)
            palette.setColor(QPalette.BrightText, Qt.red)
            palette.setColor(QPalette.Link, QColor(42, 130, 218))
            palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
            palette.setColor(QPalette.HighlightedText, Qt.black)
            app.setPalette(palette)
        else:
            app.setStyle("WindowsVista")
            # app.setStyle("Fusion")
            app.setPalette(QApplication.style().standardPalette())


    def btn_reset_settings_function(self):
        ChaosGroup.settings_global.clear()
        self.store_settings = False
        self.btn_reset_settings.setText("Please restart the application to reset the settings!")


class Sudo_Login(QWidget):

    
    def __init__(self):
        super().__init__()
        
    
        self.mainLayout = QFormLayout()
        self.mainLayout.setVerticalSpacing(35)
        self.mainLayout.setHorizontalSpacing(35)
        self.mainLayout.setFormAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.mainLayout.setContentsMargins(100,0,100,0)

        #CREATE WIDGETS
        self.password_info = QLabel('Sudo-password is needed to use the Chaos Installer!')
        self.password_input = QLineEdit()
        self.password_input.setMinimumWidth(250)
        self.password_input.setPlaceholderText('Enter Sudo Password')
        self.password_input.setEchoMode(QLineEdit.Password)
        self.qcheckbox_remember_credentials = QCheckBox('Remember Credentials')

        self.login_btn = QPushButton('Login')
        self.login_btn.clicked.connect(self.login_btn_function)
       

        #ADD WIDGETS TO LAYOUT
        self.mainLayout.addRow(self.password_info)
        self.mainLayout.addRow(self.password_input,self.qcheckbox_remember_credentials)
        self.mainLayout.addRow(self.login_btn)
        
        self.setLayout(self.mainLayout)
        
        

    def login_btn_function(self):
        
        
        sudo_password = (self.password_input.text() + '\n').encode()
        #print(sudo_password, type(sudo_password))
        try:
            output = subprocess.check_output('sudo -k -S echo success', shell=True, input=sudo_password)
            if output == b'success\n':
                logging.info('Password accepted')
                ChaosGroup.sudo_password = sudo_password
                self.sudo_successful_login = True

                #STORE SUDO PASS IN SETTINGS
                if self.qcheckbox_remember_credentials.isChecked() == True:
                    ChaosGroup.settings_global.setValue('sudo_password', sudo_password)

                #RESET SETTINGS IF ENTERED PASSWORD IS INCORRECT
                self.password_input.clear()
                self.password_input.setPlaceholderText('Enter Sudo Password')

                #REPLACE CENTRAL-WIDGET FROM SUDO TO TAB-WIDGET
                CG.tab_MAIN.show()
                CG.setCentralWidget(CG.tab_MAIN)
  
        except:
            logging.info('Incorrect Password!')
            self.password_input.clear()
            self.password_input.setPlaceholderText('Incorrect Password!!!')



if __name__ == "__main__":

    app = QApplication(sys.argv)

    # Create and display the splash screen
    splash_pix = QPixmap('./images/splash_screen.png')
    splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
    splash.setMask(splash_pix.mask())
    splash.show()
    app.processEvents()

    #THIS IMPORT IS HERE IN ORDER TO SHOW SPLASH SCREEN BEFORE LOADING DATA SLOWDOWN FROM THE WEBSITE
    import CG_Official
    CG = ChaosGroup()
    CG.show()
    splash.finish(CG)


    #SET V-RAY AS DEFAULT PRODUCT FOR OFFICIAL GROUP
    #self.tab_installer_ref.mainLayout.addWidget(self.group_official.groupBox_Official)
    try:
        vray_index = CG.tab_MAIN.tab_Install.group_login.group_official.cbox_official_productName.findText("V-Ray")
        CG.tab_MAIN.tab_Install.group_login.group_official.cbox_official_productName.setCurrentIndex(vray_index)
        
        #SET LAST SELECTED PRODUCT TO OFFICIAL INSTALLER
        productName = ChaosGroup.settings_global.value('official productName')
        productName_index = CG.tab_MAIN.tab_Install.group_login.group_official.cbox_official_productName.findText(productName)
        if productName_index != -1:
            CG.tab_MAIN.tab_Install.group_login.group_official.cbox_official_productName.setCurrentIndex(productName_index)

        #SET LAST SELECTED HOST APP TO OFFICIAL INSTALLER
        platformName = ChaosGroup.settings_global.value('official platformName')
        platformName_index = CG.tab_MAIN.tab_Install.group_login.group_official.cbox_official_platformName.findText(platformName)
        if platformName_index != -1:
            CG.tab_MAIN.tab_Install.group_login.group_official.cbox_official_platformName.setCurrentIndex(platformName_index)

        #SET LAST SELECTED HOST APP VERSION TO OFFICIAL INSTALLER
        platformVersion = ChaosGroup.settings_global.value('official platformVersion')
        platformVersion_index = CG.tab_MAIN.tab_Install.group_login.group_official.cbox_official_platformVersion.findText(platformVersion)
        if platformVersion_index != -1:
            CG.tab_MAIN.tab_Install.group_login.group_official.cbox_official_platformVersion.setCurrentIndex(platformVersion_index)


    except:
        pass
    
    #SET V-RAY AS DEFAULT PRODUCT FOR NIGHTLY GROUP
    try:
        
        if CG.tab_MAIN.tab_Install.group_nightly.cbox_nightly_productName.count() > 1:
            CG.tab_MAIN.tab_Install.group_nightly.cbox_nightly_productName.setCurrentIndex(1)
            CG.tab_MAIN.tab_Install.group_nightly.cbox_nightly_productName.setCurrentIndex(0)
        
        else:#THIS IS A HACKY WAY TO UPDATE THE NIGHTLY GROUP WHEN ONLY V-RAY PRODUCT EXISTS FROM THE PRODUCT DROPDOWN MENU
            CG.tab_MAIN.tab_Install.group_nightly.cbox_nightly_productName.addItem('V-Ray')
            CG.tab_MAIN.tab_Install.group_nightly.cbox_nightly_productName.setCurrentIndex(1)
            CG.tab_MAIN.tab_Install.group_nightly.cbox_nightly_productName.setCurrentIndex(0)
            CG.tab_MAIN.tab_Install.group_nightly.cbox_nightly_productName.removeItem(1)


        #SET LAST SELECTED PRODUCT TO NIGHTLY INSTALLER
        productName = ChaosGroup.settings_global.value('nightly productName')
        productName_index = CG.tab_MAIN.tab_Install.group_nightly.cbox_nightly_productName.findText(productName)
        if productName_index != -1:
            CG.tab_MAIN.tab_Install.group_nightly.cbox_nightly_productName.setCurrentIndex(productName_index)

            
        #SET LAST SELECTED HOST APP TO NIGHTLY INSTALLER
        platformName = ChaosGroup.settings_global.value('nightly platformName')
        platformName_index = CG.tab_MAIN.tab_Install.group_nightly.cbox_nightly_platformName.findText(platformName)
        if platformName_index != -1:
            CG.tab_MAIN.tab_Install.group_nightly.cbox_nightly_platformName.setCurrentIndex(platformName_index)

        
        #SET LAST SELECTED NIGHTLY VERSION TO NIGHTLY INSTALLER
        nightlyVersion = ChaosGroup.settings_global.value('nightly nightlyVersion')
        nightlyVersion_index = CG.tab_MAIN.tab_Install.group_nightly.cbox_nightly_version.findText(nightlyVersion)
        if nightlyVersion_index != -1:
            CG.tab_MAIN.tab_Install.group_nightly.cbox_nightly_version.setCurrentIndex(nightlyVersion_index)

        
    except:
        pass


    #LOAD SETTINGS:
    try:
        start_host_app_status = eval(ChaosGroup.settings_global.value("start host app").title())
        CG.tab_MAIN.tab_Install.chbox_start_host_app_after_install.setChecked(start_host_app_status)
    except:
        pass
    
    #UPDATE NIGHLIES 
    def import_CG_Nightlies():
        CG.tab_MAIN.tab_Install.group_nightly.cg_nightlies = CG_Nightlies.Nightlies()

    update_ftp_timer = QTimer()
    update_ftp_timer.timeout.connect(import_CG_Nightlies)
    update_ftp_timer.start(60000)

    app.exec_()

