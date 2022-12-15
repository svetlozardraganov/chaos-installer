from PyQt5.QtWidgets import QApplication, QMessageBox

import zipfile
import subprocess
import pathlib
import threading
import csv
import os
import signal
import shutil
import xml.etree.ElementTree as ET
import time

import logging
logging.basicConfig(level=logging.INFO)

import platform
from pathlib import Path

if platform.system() == 'Windows':
    import winreg
    import CG_Registry


class ChaosUtilities():

    def __init__(self):

        #USE THIS VARIABLE TO STORE MACOS HOST-APP PATHS
        self.data = {'Cinema 4D': {}, 'Maya': {}, 'SketchUp':{}, 'Nuke':{}, 'Modo':{}, 'Houdini':{}}

    def PyQTerrorMSG(self,error_msg, more_information = None, App= None):
        #https://stackoverflow.com/questions/40227047/python-pyqt5-how-to-show-an-error-message-with-pyqt5

        logging.critical(error_msg)
        logging.critical(more_information)


        if App == None:
            app = QApplication([])
            msg = QMessageBox()
            
        else:
            msg = QMessageBox(App)

        msg.setIcon(QMessageBox.Critical)
        msg.setText(error_msg)
        msg.setInformativeText(more_information)
        msg.setWindowTitle("Error")

        if App == None:
            msg.exec_()
            exit()
        else:
            msg.show()

    def PyQtYesNoMessage(self,title, msg, App):

        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Critical)
        answer = msg_box.question(App, title, msg , msg_box.Yes | msg_box.No)
        msg_box.show()

        if answer == msg_box.Yes:
            return True
        elif answer == msg_box.No:
            return False

    def PyQTmessage(self,message, more_information, App):
        #https://stackoverflow.com/questions/40227047/python-pyqt5-how-to-show-an-error-message-with-pyqt5

        msg = QMessageBox(App)

        msg.setIcon(QMessageBox.Information)
        msg.setText(message)
        msg.setInformativeText(more_information)
        msg.setWindowTitle("Information")

        msg.show()

    
    def install(self, download_path='', build_file='', productName='', productVersion='', platformName='',
                platformVersion='', silent_install='', start_host_app='',
                remove_files_after_install = '', quit_after_install='', App= None):

        
        #INNITIAL VAR STATES, NEEDED FOR REMOVING FILES FUNCITON
        remove_extract_dir = False

        #KILL HOST APP        
        self.killHostApp(productName=productName, platformName=platformName, platformVersion=platformVersion)


        #SET ARG1 DEPENDING ON OS VERSION
        if platform.system() == 'Windows':

             #EXTRACT ARCHIVE FILES
            if build_file.endswith('.zip'):
                zip_output = self.zip_extract(download_path = download_path,
                                            build_file = build_file,
                                            productName = productName,
                                            productVersion = productVersion,
                                            platformName = platformName)

                arg1 = zip_output['extract_path'] + zip_output['build_name']
                logging.info('Installing {0}'.format(zip_output['build_name']))

                remove_extract_dir = True

            
            elif build_file.endswith('.exe'):
                arg1 = download_path + build_file
                logging.info('Installing {0}'.format(build_file))


            #SILENT INSTALL / SET ARG2-1RG
            if silent_install == True and (productName != 'V-Ray Benchmark' and productName != 'PDPlayer' and platformName != 'Houdini') :
                arg2 = '-auto'
                arg3 = '-gui=0'
                arg4 = '-quiet=0'
                arg5 = '-backup=0'

                if productName == 'V-Ray' and productVersion == '5':
                    arg6 = '-VARIABLE_MTLLIB_DOWNLOAD_CB=0'
                    logging.info("Installation CMD: {0} {1} {2} {3} {4} {5}".format(arg1, arg2, arg3, arg4, arg5, arg6))

                    subprocess.call([arg1, arg2, arg3, arg4, arg5, arg6], shell=True)
                

                else:
                    logging.info("Installation CMD: {0} {1} {2} {3} {4}".format(arg1, arg2, arg3, arg4, arg5))
                    subprocess.call([arg1, arg2, arg3, arg4, arg5], shell=True)
            
            #GUI INSTALLATION
            else:
                logging.info("Installating: {0}".format(arg1))
                subprocess.call([arg1], shell=True)


        elif platform.system() == 'Darwin':
            

            if build_file.endswith('.zip'):
                zip_output = self.zip_extract(download_path = download_path,
                                            build_file = build_file,
                                            productName = productName,
                                            productVersion = productVersion,
                                            platformName = platformName)

                # arg1 = zip_output['extract_path'] + zip_output['build_name']
                # logging.info('Installing {0}'.format(zip_output['build_name']))

                download_path = zip_output['extract_path']
                build_file = zip_output['build_name']

                remove_extract_dir = True

        
            build_file = self.mac_mount_disk(download_path=download_path, build_file=build_file)
            arg1 = './/' + build_file            
            

            #login using root account: https://stackoverflow.com/questions/51224674/execute-sudo-commands-with-subprocess-in-pycharm
            print(subprocess.check_output('sudo -S echo success', shell=True, input=App.sudo_password))

            # print('start installation')
            #run_silent_installer = subprocess.Popen(['.//' + build_file[0], '-gui=0', '-auto'])
            # arg2 = '-auto'
            # arg3 = '-gui=0'
            # arg4 = '-quiet=0'
            # arg5 = '-backup=0'
            # run_silent_installer = subprocess.call([arg1, arg2, arg3, arg4, arg5])
            # run_silent_installer.wait()
            # print('end installation')


            #SILENT INSTALL / SET ARG2-1RG
            if silent_install == True and (productName != 'V-Ray Benchmark' and productName != 'PDPlayer' and platformName != 'Houdini') :
                arg2 = '-auto'
                arg3 = '-gui=0'
                arg4 = '-quiet=0'
                arg5 = '-backup=0'

                if productName == 'V-Ray' and productVersion == '5':
                    arg6 = '-VARIABLE_MTLLIB_DOWNLOAD_CB=0'
                    logging.info("Installation CMD: {0} {1} {2} {3} {4} {5}".format(arg1, arg2, arg3, arg4, arg5, arg6))

                    subprocess.call([arg1, arg2, arg3, arg4, arg5, arg6])

                else:
                    logging.info("Installation CMD: {0} {1} {2} {3} {4}".format(arg1, arg2, arg3, arg4, arg5))
                    subprocess.call([arg1, arg2, arg3, arg4, arg5])
         
            
            #GUI INSTALLATION
            elif platformName == 'Houdini':

                logging.info("Installating: {0}".format(arg1))
                install_process = subprocess.check_call([arg1], shell=True)              

                #ENSURE HOUDIDI INSTALLATION IS COMPLETED
                while True:
                    data = subprocess.Popen(['ps','aux'], stdout=subprocess.PIPE).stdout.readlines()
                    is_installation_running = False

                    for line in data:
                        if b'/Volumes/V-Ray for Houdini' in line:
                            is_installation_running = True

                    if is_installation_running == True:
                        #logging.info('Installation is running')
                        time.sleep(3)
                    else:
                        # logging.info('Installation completed')
                        break

            elif productName == 'V-Ray Benchmark':
                if ' ' in arg1:
                    arg1 = arg1.replace(' ', '\\ ')
                install_process = subprocess.check_call([arg1], shell=True)

            elif productName == 'PDPlayer':

                try:
                    #REMOVE PDPLAYER DIR
                    subprocess.check_output('sudo rm -R /Applications/ChaosGroup/pdplayer', shell=True, input=App.sudo_password)
                except:
                    pass
                finally:
                    #CREATE PDPLAYER DIR
                    print(subprocess.check_output('sudo mkdir /Applications/ChaosGroup/pdplayer/', shell=True, input=App.sudo_password))
                    #COPY PDPLAYER 
                    cmd = ['sudo', 'cp', '-R', self.mount_volume + '/Pdplayer 64.app', '/Applications/ChaosGroup/pdplayer/Pdplayer 64.app']
                    copy = subprocess.Popen(cmd)
                    copy.wait()

                    #START PDPLAYER
                    # subprocess.Popen(['/Applications/ChaosGroup/pdplayer/Pdplayer 64.app/Contents/MacOS/Pdplayer 64'], shell=True, stdin=None, stdout=None, stderr=None, close_fds=True)

                    cmd = '/Applications/ChaosGroup/pdplayer/Pdplayer 64.app/Contents/MacOS/Pdplayer 64'
                    subprocess.Popen(cmd)
                    self.PyQTmessage(message='PDPlayer installed in:', more_information='/Applications/ChaosGroup/pdplayer/Pdplayer 64', App=App)


            else:
                logging.info("Installating: {0}".format(arg1))
                install_process = subprocess.check_call([arg1], shell=True)
                


            #REMOVE MOUNT DISK IF SYSTEM=MACOS
            #THIS PROCESS IS MOVED TO CLOSE-EVENT SINCE FOR SOME REASON IT CAUSES MAYA TO CRASH WHEN EXECUTED HERE
            #unmount_process = subprocess.Popen(['diskutil', 'unmountDisk', 'force', self.mount_disk])
            os.chdir(str(Path.home())) #change current working dir to home
            unmount_process = subprocess.Popen(['diskutil', 'unmountDisk', self.mount_disk])
            #App.mounted_volumes.append(self.mount_disk)


        elif platform.system() == 'Linux':
            
            if build_file.endswith('.zip'):
                zip_output = self.zip_extract(download_path = download_path,
                                            build_file = build_file,
                                            productName = productName,
                                            productVersion = productVersion,
                                            platformName = platformName)

                # arg1 = zip_output['extract_path'] + zip_output['build_name']
                # logging.info('Installing {0}'.format(zip_output['build_name']))

                download_path = zip_output['extract_path']
                build_file = zip_output['build_name']

            arg1 = download_path + build_file

            #ADD EXECUTE RIGHTS TO THE BUILD
            os.chmod(arg1, 0o0777)

            #SUDO LOGIN
            print(subprocess.check_output('sudo -S echo success', shell=True, input=App.sudo_password))


            #SILENT INSTALL
            if silent_install == True and productName != 'V-Ray Benchmark' and productName != 'V-Ray AppSDK' and productName != 'PDPlayer' and platformName != 'Houdini':

                arg2 = '-auto'
                arg3 = '-gui=0'
                arg4 = '-quiet=0'
                arg5 = '-backup=0'
                arg6 = '-VARIABLE_MTLLIB_DOWNLOAD_CB=0'
                
                if platformName != 'Nuke':

                    if productName == 'V-Ray' and productVersion == '5':
                        logging.info("Installation CMD: {0} {1} {2} {3} {4} {5}".format(arg1, arg2, arg3, arg4, arg5, arg6))
                        subprocess.call(['sudo', arg1, arg2, arg3, arg4, arg5, arg6])
                
                    else:
                        logging.info("Installation CMD: {0} {1} {2} {3} {4}".format(arg1, arg2, arg3, arg4, arg5))
                        subprocess.call(['sudo', arg1, arg2, arg3, arg4, arg5])
                        
                else:
                    
                    nuke_install_path = self.linux_get_nuke_install_path(platformVersion=platformVersion)
                    self.linux_gen_nuke_config_xml(download_path = download_path, nuke_install_path = nuke_install_path)

                    arg2 = '-configFile="' + download_path + 'config_nuke.xml"'

                    print("Installation CMD: {0} {1} {2}".format('sudo', arg1, arg2))

                    subprocess.call(['sudo', arg1, arg2])


            #IF PRODUCT IS PDPLAYER
            elif productName == 'PDPlayer':

                #SET CURRENT WORKING DIR TO DOWNLOAD PATH
                os.chdir(download_path)

                #EXTRACT FILE
                if arg1.endswith("tar.gz"):
                    subprocess.call(['tar', 'xzf', arg1])
                    
                #FIND EXTRACTED DIRECTORY
                dirs = os.listdir()
                for dir in dirs:
                    if 'pdplayer' in dir:
                        if os.path.isdir(download_path + dir)==True:

                            try:
                                #REMOVE PDPLAYER DIR
                                subprocess.check_output('sudo rm -r /usr/ChaosGroup/pdplayer', shell=True, input=App.sudo_password)
                            except:
                                pass
                            finally:
                                #CREATE PDPLAYER DIR
                                print(subprocess.check_output('sudo mkdir /usr/ChaosGroup/pdplayer', shell=True, input=App.sudo_password))
                                #COPY PDPLAYER 
                                cmd = ['sudo', 'cp', '-r', download_path + dir + '/pdplayer', '/usr/ChaosGroup/']
                                copy = subprocess.Popen(cmd)
                                copy.wait()

                                #START PDPLAYER
                                # subprocess.Popen(['/Applications/ChaosGroup/pdplayer/Pdplayer 64.app/Contents/MacOS/Pdplayer 64'], shell=True, stdin=None, stdout=None, stderr=None, close_fds=True)

                                # cmd = '/Applications/ChaosGroup/pdplayer/Pdplayer 64.app/Contents/MacOS/Pdplayer 64'
                                # subprocess.Popen(cmd)
                                # self.PyQTmessage(message='PDPlayer installed in:', more_information='/Applications/ChaosGroup/pdplayer/Pdplayer 64', App=App)


                #LAUCH PDPLAYER
                subprocess.Popen(['/usr/ChaosGroup/pdplayer/pdplayer64'], shell=True, stdin=None, stdout=None, stderr=None, close_fds=True)

                self.PyQTmessage(message='PDPlayer installed in:', more_information='/usr/ChaosGroup/pdplayer', App=App)

            #GUI INSTALLATION
            else:
                logging.info("Installating: {0}".format(arg1))
                subprocess.call(['sudo', arg1])
                    
       
        logging.info("Installation completed")

        
        #REMOVE DOWNLOADED/EXTRACTED FILES:
        if remove_files_after_install == True and remove_extract_dir == True:
            self.removeFilesAfterInstall(App=App,
                                        remove_file_after_install = remove_files_after_install,
                                        file_full_path = download_path + '\\' + build_file,
                                        remove_extract_dir = remove_extract_dir,
                                        extract_dir = zip_output['extract_path'])

        elif remove_files_after_install == True and remove_extract_dir == False:
            self.removeFilesAfterInstall(App=App,
                                        remove_file_after_install = remove_files_after_install,
                                        file_full_path = download_path + '\\' + build_file)

        #START HOST APPLICATION
        if start_host_app == True:
            self.startHostApp(productName=productName, productVersion=productVersion, platformName=platformName, platformVersion=platformVersion)


        
        # if platformName == '3ds Max' and platformVersion == '2021':
        #     self.startHostApp(platformName=platformName, platformVersion=platformVersion)

            #-VARIABLE_OPEN_CHANGELOG = 0 added as argument can override installer options
            #" -VARIABLE_MTLLIB_DOWNLOAD_CB=1"

        # if self.cbox_official_productName.currentText() == "V-Ray AppSDK":
        #     VRayAppSDK.VRayAppSDK_Instance.install(download_path, self.build_file)


        #QUIT AFTER INSTALLATION
        if quit_after_install == True:
            exit()

        


    def zip_extract(self, download_path, build_file, productName ='', productVersion='', platformName=''):
        # download_path = r'C:\Users\SvetlozarDraganov\AppData\Local\Temp\Chaos Installer\\'
        # build_file = 'vray_adv_50010_max2018_x64_29945_install.zip'

        extract_path = download_path + build_file[:-4] + r'/' #REMOVING .ZIP EXTENTION
        zip_file_path = download_path + build_file
        zf = zipfile.ZipFile(zip_file_path)

        uncompress_size = sum((file.file_size for file in zf.infolist()))
        uncompress_size_mb = int(uncompress_size / (1024*1024))
        logging.info('<Extracting> {0} / {1}MB'.format(build_file,uncompress_size_mb))
        logging.info('Extract Path = {0}'.format(extract_path))

        extracted_size = 0

        for file in zf.infolist():
            # extracted_size += file.file_size
            # print("%s %%" % (extracted_size * 100/uncompress_size))
            
            #FIND THE NAME OF THE EXTRACTED .EXE FILE
            if productName == 'V-Ray' and productVersion[0] == '3' and platformName == 'Maya':
                if file.filename.startswith('vray') and file.filename.endswith('.exe'):         #vray_adv_36005_maya2018_x64.exe
                    build_name = file.filename
            else:
                build_name = file.filename


            logging.info('Extracting: {0}'.format(file.filename))

            zf.extract(file, extract_path)

        return {'extract_path': extract_path, 'build_name': build_name}



    def killHostApp(self, productName='', platformName='', platformVersion=''):
        

        if platform.system() == 'Windows':

            #STOP V-RAY SPAWNWER/SWARM SERVICES BEFORE KILLING HOST-APPS
            #get windows services
            services = subprocess.run(['net', 'start'], stdout=subprocess.PIPE)
            #remove new lines and convert services output to a regular list
            services = services.stdout.splitlines()

            for item in services:
                #remove the first three empty spaces
                item = item[3:] 

                #if VRaySpawner is found, stop it
                if b'VRaySpawner' in item:
                    item = item.decode("utf-8")
                    subprocess.run(['net', 'stop', item], stdout=subprocess.PIPE)
                
                elif b'V-Ray Swarm' in item:
                    item = item.decode("utf-8")
                    subprocess.run(['net', 'stop', item], stdout=subprocess.PIPE)



            # processes = subprocess.check_output(['wmic', 'process', 'get', 'executablepath,processid', '/format:csv'])

            #GET PROCESS-PATH AND PROCESS-ID
            #https://stackoverflow.com/questions/8880461/python-subprocess-output-to-list-or-file
            #https://www.pearsonitcertification.com/articles/article.aspx?p=1700427&seqNum=4
            #https://www.geeksforgeeks.org/python-get-list-of-running-processes/
            processes = subprocess.Popen(['wmic', 'process', 'get', 'ExecutablePath,ProcessId,CommandLine', '/format:csv'], stdout = subprocess.PIPE)
            stdout, stderr = processes.communicate()

            reader = csv.DictReader(stdout.decode('ascii').splitlines(), delimiter=',', skipinitialspace=True, fieldnames=['Node','CommandLine', 'ExecutablePath','ProcessId'])

            #SET HOST APP SEARCH-STRING TO FIND THE RIGHT PROCESS
            searchString = ''
            

            if productName == 'V-Ray' or productName == 'Phoenix FD':

                #SET SEARCH STRING TO FIND THE CORRESPONDING APPLICATION AND ITS VERSION.
                #FOR SOME PRODUCT VERSION IS NOT NEEDED CAUSE THE INSTALLER SUPPORTS MULTIPLE VERSIONS MEANING ALL INSTANCES SHOULD BE KILLED
                if platformName == '3ds Max':
                    searchString = platformName + ' ' + platformVersion
                elif platformName == 'Maya':
                    searchString = platformName + platformVersion
                elif platformName == 'Cinema 4D':
                    searchString = 'Cinema 4D.exe'
                elif platformName == 'SketchUp':
                    searchString = 'SketchUp.exe'
                elif platformName == 'Modo':
                    searchString = 'modo.exe'
                elif platformName == 'Revit':
                    searchString = 'Revit.exe'
                elif platformName == 'Rhino':
                    searchString = ['Rhino.exe', 'Rhino4.exe']
                elif platformName == 'Unreal':
                    searchString = 'UE4Editor.exe'
                elif platformName == 'Houdini':
                    searchString = platformName + ' ' + platformVersion
                elif platformName == 'Nuke':
                    searchString = platformName + platformVersion + '.exe'

                print(searchString)
                
                #FIND AND KILL THE PROCESES
                for row in reader:

                    #print(row)

                    #SEARCH-STRING CONTAINS A SINGLE VALUE
                    if platformName != 'Rhino' and platformName != 'Standalone' and platformName != 'AppSDK':
                        if searchString.lower() in row['ExecutablePath'].lower() and \
                            'vrayspawner' not in row['ExecutablePath'].lower(): #exclude vrayspawner because V-Ray for 3ds Max 2021 searchString is found on both 3dsmax.exe and vrayspawer****.exe and it gives na error.

                            print(row['ExecutablePath'], row['ProcessId'])
                            logging.info('Terminating: {0}'.format(row['ExecutablePath']))
                            os.kill(int(row['ProcessId']), signal.SIGTERM)

                    #SEARCH-STRING IS A LIST OF VALUES
                    elif platformName == 'Rhino':
                        if any(item.lower() in row['ExecutablePath'].lower() for item in searchString):
                            print(row['ExecutablePath'], row['ProcessId'])
                            logging.info('Terminating: {0}'.format(row['ExecutablePath']))
                            os.kill(int(row['ProcessId']), signal.SIGTERM)


                    #KILL VRAY.EXE PROCESS
                    if 'vray.exe' in row['CommandLine']:
                        print(row['CommandLine'], row['ProcessId'])
                        logging.info('Terminating: {0}'.format(row['CommandLine']))
                        os.kill(int(row['ProcessId']), signal.SIGTERM)

                    #KILL VRAY SPAWNER PROCESS
                    if 'vrayspawner' in row['CommandLine']:
                        print(row['CommandLine'], row['ProcessId'])
                        logging.info('Terminating: {0}'.format(row['CommandLine']))
                        os.kill(int(row['ProcessId']), signal.SIGTERM)

                #exit()
            
            elif productName == 'Lavina' or productName =='PDPlayer':

                if productName == 'Lavina':
                    searchString = 'lavina.exe'
                elif productName == 'PDPlayer':
                    searchString = 'pdplayer64.exe'

                for row in reader:
                    if searchString.lower() in row['ExecutablePath'].lower():
                        print(row['ExecutablePath'], row['ProcessId'])
                        logging.info('Terminating: {0}'.format(row['ExecutablePath']))
                        os.kill(int(row['ProcessId']), signal.SIGTERM)


        else:
            
            searchString = platformName.lower()
            platformVersion = platformVersion.lower()

            if 'PDPlayer' in productName:
                searchString = productName.lower()


            if productName == 'V-Ray' or productName == 'PDPlayer':
                #LIST PROCESSES USING PS COMMAND
                running_processes = subprocess.check_output(['ps', '-eo', 'pid,command'])
                running_processes = running_processes.decode('ascii').splitlines()

                #CHECK IF HOST APP IS CURRENTLY RUNNING
                for line in running_processes:
                    line = line.lower()

                    #REMOVE LEADING SPACES
                    line = line.lstrip(' ')

                    if (searchString in line) and (platformVersion in line):
                        
                        #SPLIT PID AND COMMAND
                        line = line.split(' ',1)
                        #LINUX OUTPUT STARTS WITH A SPACE, TO REMOVE IT RUN THIS SAME COMMAND ONE MORE TIME
                        # if platform.system() == 'Linux':
                        #     line = line[1].split(' ',1)

                        logging.info('Kill | App={0} | PID={1}'.format(line[1], line[0]))
                        subprocess.Popen(['kill', '-9', line[0]])
                    


            # if productName == 'V-Ray' or productName == 'V-Ray Benchmark' or productName == 'PDPlayer':
            #     #LIST PROCESSES USING PS COMMAND - TWO PROCS ARE USED TO SIMULATE GREP-COMMAND
            #     proc1 = subprocess.Popen(['ps', '-eo', 'pid,command'], stdout=subprocess.PIPE)
            #     proc2 = subprocess.Popen(['grep', searchString], stdin=proc1.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            #     proc1.stdout.close() # Allow proc1 to receive a SIGPIPE if proc2 exits.
            #     out, err = proc2.communicate()

            #     #SPLIT OUT-CMD TO SEPARATE LINES
            #     out = out.decode('ascii').splitlines()
                

            #     for row in out:
            #         row = row.lower()
            #         #SPLIT PID AND CMD 
            #         row = row.split(' ',1)
            #         #LINUX OUTPUT STARTS WITH A SPACE, TO REMOVE IT RUN THIS SAME COMMAND ONE MORE TIME
            #         if platform.system() == 'Linux':
            #             row = row[1].split(' ',1)
            #         logging.info('PID={0}, CMD={1}'.format(row[0], row[1]))

            #         #IF searchString AND PLATFORM VERSION ARE IN CMD, FIND PID AND KILL APP
            #         if (searchString and platformVersion) in row[1]:
            #             logging.info('Kill | App: {0} | PID : {1}'.format(row[1], row[0]))
            #             subprocess.Popen(['kill', '-9', row[0]])

                

    def removeFilesAfterInstall(self, App,  remove_file_after_install='', file_full_path='',remove_extract_dir='', extract_dir=''):

        dont_show_warning = App.tab_MAIN.tab_Settings.qcheck_dont_show_warning.isChecked()
        #SHOW WARNING WINDOW
        if dont_show_warning == False:

            #SET MESSAGE TEXT DEPENDING ON WHAT WILL BE REMOVED
            msg = 'Are you sure you want to remove the following data? \n\n'
            if remove_file_after_install == True and remove_extract_dir == True:
                msg += file_full_path + '\n\n' + extract_dir
            elif remove_file_after_install == True:
                msg += file_full_path
            elif remove_extract_dir == True:
                msg += extract_dir

            title = 'Removing files...'
            
            #DISPLAY YES/NO USER DIALOG
            remove_file_user_output = self.PyQtYesNoMessage(title=title, msg = msg, App=App)
        
        else:
            remove_file_user_output = True

        if remove_file_user_output == True or remove_extract_dir == True:
            
            #REMOVE DOWNLOADED FILE
            if remove_file_after_install == True:
                if os.path.exists(file_full_path):
                    os.remove(file_full_path)
                    logging.info('Removing file: {}!'.format(file_full_path))
                else:
                    logging.info('{} does not exists!'.format(file_full_path))

            #REMOVE EXTRACTED DIR
            if remove_extract_dir == True:
                if os.path.exists(extract_dir):
                    shutil.rmtree(extract_dir)
                    logging.info('Removing directory: {}!'.format(extract_dir))
                else:
                    logging.info('{} does not exists!'.format(extract_dir))

        else:
            logging.info('File: {} not removed!'.format(file_full_path))


    def startHostApp(self, productName='', productVersion='', platformName='', platformVersion=''):
        
        if platform.system() == 'Windows':

            if platformName == '3ds Max' or platformName == 'Maya' or platformName == 'Nuke' or platformName == 'Houdini' or \
                    platformName == 'Cinema 4D':

                #IF PLATFORM NAME IS V-RAY OR PHOENIX / NOT LAVINA,APPSDK,PDPLAYER,LICENSE SERVER
                if platformName != '' and platformVersion !='':
                    host_app = CG_Registry.registry.data[platformName][platformVersion]
                

                logging.info('Host App = {}'.format(host_app))

                #SET HOST APP ENVIRONMENT VARS, OTHERWISE V-RAY GIVES ENV-VAR ERROR ON HOST APP STARTUP
                env = self.setHostAppEnvVars(productName = productName, productVersion = productVersion,
                                    platformName=platformName, platformVersion=platformVersion)

            
                #START HOST APP ON SEPARATE CPU THREAD
                run_host_app_on_separate_thread = Threading(host_app=host_app, env=env)
                run_host_app_on_separate_thread.start()
                
            
            elif platformName == 'Revit':

                host_app = CG_Registry.registry.data[platformName]
                revit_location = []
                #ADD REVIT VERSIONS TO 
                for k,v in host_app.items():
                    revit_location.append(v)

                #IF ONLY ONE VERSION OF HOST APP IS INSTALLED
                if len(revit_location) == 1:
                    # print(revit_location[0])
                    env=os.environ.copy()
                    run_host_app_on_separate_thread = Threading(host_app=revit_location[0], env=env)
                    run_host_app_on_separate_thread.start()
                else:
                    pass
                    #TODO add option to select which host app version should be installed

            if productName == 'Chaos Vantage':

                host_app = CG_Registry.registry.data['chaosgroup'][productName]['install_location']
                logging.info('Host App = {}'.format(host_app))

                env=os.environ.copy()
                run_host_app_on_separate_thread = Threading(host_app=host_app, env=env)
                run_host_app_on_separate_thread.start()

        elif platform.system() == 'Darwin':

            if platformName != 'Standalone' and productName == 'V-Ray':
                host_app = self.mac_get_host_app_path(platformName=platformName, platformVersion=platformVersion)
                logging.info('Launching {0}'.format(host_app))
                
                
                run_host_app_on_separate_thread = Threading(host_app=host_app)
                run_host_app_on_separate_thread.start()
                

        elif platform.system() == 'Linux':

            host_app = self.linux_get_host_app_path(platformName=platformName, platformVersion=platformVersion)

            #SET HOST APP ENVIRONMENT VARS, OTHERWISE V-RAY GIVES ENV-VAR ERROR ON HOST APP STARTUP
            env = self.setHostAppEnvVars(productName = productName, productVersion = productVersion,
                                    platformName=platformName, platformVersion=platformVersion)

            logging.info('Launching {}'.format(host_app))
            
            run_host_app_on_separate_thread = Threading(host_app=host_app, env=env)
            run_host_app_on_separate_thread.start()



    def setHostAppEnvVars(self, productName, productVersion, platformName, platformVersion):

        #SET ENV VARS SINCE NEW HOST APP INSTANCE CAN'T GET THE UPDATES AUTOMATICALLY, HENCE THEY NEED TO BE PASSED MANUALLY
        #https://stackoverflow.com/questions/38348556/how-to-set-a-thread-specific-environment-variable-in-python

        #GET ALL ENVIRONMENT VARIABLES BEFORE THE INSTALLATION
        env = os.environ.copy()
        
        if platform.system() == 'Windows':
            #UPDATE VRAY_MAIN VARIABLE WITH IT'S NEW VALUE AFTER INSTALLATION
            if productName == 'V-Ray':
                vray_version =  productVersion[0]

                if platformName == '3ds Max':

                    if vray_version != '3':
                        VRAY_MAIN_var = 'VRAY' + vray_version + '_FOR_3DSMAX' + platformVersion + '_MAIN'   #'VRAY5_FOR_3DSMAX2021_MAIN'
                    else:
                        VRAY_MAIN_var = 'VRAY30_RT_FOR_3DSMAX' + platformVersion + '_MAIN_x64'                   #VRAY30_RT_FOR_3DSMAX2020_MAIN_x64
                    
                    VRAY_MAIN_val = self.win_getEnvVarFromRegistry(VRAY_MAIN_var)                                    #'VRAY5_FOR_3DSMAX2021_MAIN'
                    env[VRAY_MAIN_var] = VRAY_MAIN_val

                    logging.info('{}  = {}'.format(VRAY_MAIN_var, VRAY_MAIN_val))

                elif platformName == 'Maya':

                    if vray_version != '3':
                        VRAY_MAIN_var = 'VRAY_FOR_MAYA' + platformVersion + '_MAIN'                              #'VRAY_FOR_MAYA2020_MAIN'
                        VRAY_PLUGINS_var = 'VRAY_FOR_MAYA' + platformVersion + '_PLUGINS'                        #VRAY_FOR_MAYA2016_PLUGINS
                        
                    else:
                        VRAY_MAIN_var = 'VRAY_FOR_MAYA' + platformVersion + '_MAIN_x64'                          #VRAY_FOR_MAYA2018_MAIN_x64
                        VRAY_PLUGINS_var = 'VRAY_FOR_MAYA' + platformVersion + '_PLUGINS_x64'                        #VRAY_FOR_MAYA2018_PLUGINS_x64

                    VRAY_MAIN_val = self.win_getEnvVarFromRegistry(VRAY_MAIN_var)                                #'VRAY_FOR_MAYA2020_MAIN'
                    VRAY_PLUGINS_val = self.win_getEnvVarFromRegistry(VRAY_PLUGINS_var)

                    env[VRAY_MAIN_var] = VRAY_MAIN_val
                    env[VRAY_PLUGINS_var] = VRAY_PLUGINS_val

                    logging.info('{}  = {}'.format(VRAY_MAIN_var, VRAY_MAIN_val))

                elif platformName == 'Nuke':

                    platformVersion = platformVersion.replace('.','_')
                    VRAY_PLUGINS_var = 'VRAY_FOR_NUKE_' + platformVersion + '_PLUGINS'                        #VRAY_FOR_NUKE_12_2_PLUGINS
                    VRAY_PLUGINS_val = self.win_getEnvVarFromRegistry(VRAY_PLUGINS_var)
                    env[VRAY_PLUGINS_var] = VRAY_PLUGINS_val

                    logging.info('{}  = {}'.format(VRAY_PLUGINS_var, VRAY_PLUGINS_val))

        elif platform.system() == 'Linux':
            
            if productName == 'V-Ray':
                vray_version =  productVersion[0]


                if platformName == 'Maya':
                    #VRAY_FOR_MAYA2020_MAIN="/usr/autodesk/maya2020/vray"

                    VRAY_MAIN_var = 'VRAY_FOR_MAYA' + platformVersion + '_MAIN'                          #VRAY_FOR_MAYA2018_MAIN_x64
                    VRAY_PLUGINS_var = 'VRAY_FOR_MAYA' + platformVersion + '_PLUGINS'                        #VRAY_FOR_MAYA2018_PLUGINS_x64
                    
                    VRAY_MAIN_val = self.linux_get_host_app_path(platformName=platformName, platformVersion=platformVersion)
                    VRAY_MAIN_val = VRAY_MAIN_val.replace('/bin/maya','/vray')
                    
                    VRAY_PLUGINS_val = VRAY_MAIN_val + '/vrayplugins'

                    env[VRAY_MAIN_var] = VRAY_MAIN_val
                    env[VRAY_PLUGINS_var] = VRAY_PLUGINS_val

                    logging.info('{}  = {}'.format(VRAY_MAIN_var, VRAY_MAIN_val))

                elif platformName == 'Nuke':
                    #VRAY_FOR_NUKE_12_2_PLUGINS="/home/support/Nuke12.2v2/plugins/vray"

                    VRAY_PLUGINS_val = self.linux_get_host_app_path(platformName=platformName, platformVersion=platformVersion) #/home/support/Nuke12.2v2/Nuke12.2
                    split_index = VRAY_PLUGINS_val.rfind('/Nuke')
                    VRAY_PLUGINS_val = VRAY_PLUGINS_val[:split_index]
                    VRAY_PLUGINS_val += '/plugins/vray'

                    platformVersion = platformVersion.replace('.','_')

                    VRAY_PLUGINS_var = 'VRAY_FOR_NUKE_' + platformVersion + '_PLUGINS'                        #VRAY_FOR_NUKE_12_2_PLUGINS
                    
                    env[VRAY_PLUGINS_var] = VRAY_PLUGINS_val

                    logging.info('{}  = {}'.format(VRAY_PLUGINS_var, VRAY_PLUGINS_val))
            

        return env


    def win_getEnvVarFromRegistry(self, env_var_name):
        #https://stackoverflow.com/questions/38545262/how-to-read-out-new-os-environment-variables-in-python

        key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, r"System\CurrentControlSet\Control\Session Manager\Environment")
        return winreg.QueryValueEx(key, env_var_name)[0]


    def check_host_app_is_installed(self, productName='', platformName='', platformVersion='', App=''):

        platformName=platformName
        platformVersion=platformVersion
        productName = productName
        
        if productName == 'V-Ray' or productName == 'Phoenix FD':

            if platform.system() == 'Windows':

                if platformName in ['3ds Max', 'Cinema 4D', 'Houdini', 'Maya', 'Nuke']:

                    try:
                        host_app = CG_Registry.registry.data[platformName][platformVersion]
                        if os.path.exists(host_app):
                            logging.info('{} {} Installation found {}'.format(platformName, platformVersion, host_app))
                            return True
                        else:
                            return False
                    except:
                        title = 'Host App Not Found!'
                        msg = '{} {} not found! \n Proceeding with installation may lead to non-working product. \n Would you like to proceed with the installation?'.format(platformName,platformVersion) 
                        host_app_available = self.PyQtYesNoMessage(title=title, msg=msg, App=App)
                        return host_app_available
                
                else:
                    return True
                    # try:
                    #     host_app = CG_Registry.registry.data[platformName]
                    #     # if os.path.exists(host_app):
                    #     print(host_app)
                    # except:
                    #     pass

            elif platform.system() == 'Darwin' or platform.system() == 'Linux':
                
                if platformName in ['Cinema 4D', 'Houdini', 'Maya', 'Modo', 'SketchUp', 'Nuke']:

                    if platform.system() == 'Linux':
                        host_app = self.linux_get_host_app_path(platformName=platformName, platformVersion=platformVersion)
                    if platform.system() == 'Darwin':
                        host_app = self.mac_get_host_app_path(platformName=platformName, platformVersion=platformVersion)

                    if host_app != 'Not Installed':

                        if os.path.exists(host_app):
                            logging.info('{} {} Installation found {}'.format(platformName, platformVersion, host_app))
                            return True

                        else:
                            title = 'Host App Not Found!'
                            msg = '{} {} not found! \n Proceeding with installation may lead to non-working product. \n Would you like to proceed with the installation?'.format(platformName,platformVersion) 
                            host_app_available = self.PyQtYesNoMessage(title=title, msg=msg, App=App)
                            return host_app_available

                    else:
                        title = 'Host App Not Found!'
                        msg = '{} {} not found! \n Proceeding with installation may lead to non-working product. \n Would you like to proceed with the installation?'.format(platformName,platformVersion) 
                        host_app_available = self.PyQtYesNoMessage(title=title, msg=msg, App=App)
                        return host_app_available

                
                else:
                    return True

            else:
                print('TODO - make sure host app is indeed installed on Linux/Macos')
                return True
                    

        else:
            return True

   
    #MACOS/LINUX FUNCTIONS

    def mac_mount_disk(self, download_path, build_file, unpack_install=False):

        print(download_path, build_file)
        
        print(os.getcwd)
        mount_process = subprocess.Popen(['hdiutil', 'attach', download_path + build_file], stdout=subprocess.PIPE) #mount .dmg file

        out, err = mount_process.communicate() #get output from mount cmd
        # print('output:', out, 'error:', err)
        out = str(out) #convert bytes to string
        out = out.replace('\\n', '') #remove the new line symbol if found
        out = out.replace("'", "") # remove the '-symbol

        out = out.split('\\t')  #split string to list by \t (tab) symbol
        self.mount_disk = out[2] #get the second item from the list, which is the actual mounting point. We will need that to unmount the disk later.
        self.mount_disk = self.mount_disk.strip() #remove white-spaces
        print('mount disk = ',self.mount_disk)


        self.mount_volume = out[-1] #get the latest element from the out-list which is the volume name
        print(self.mount_volume)

        #IF PRODUCT IS PDPLAYER, NO NEED TO PROCEED FUTHER.
        if 'pdplayer' in build_file:
            return ''

        list_files = subprocess.Popen(['ls', self.mount_volume], stdout=subprocess.PIPE) #list files in mounted volume
        out, err = list_files.communicate()
        root_file = out.decode("utf-8") #decode byte object to string
        root_file = root_file.strip() #strip white-spaces

        #IF PRODUCT IS BENCHMARK, THERE ARE TWO FILES IN THE MAIN DIR, WE NEED THE 
        if 'Benchmark' in root_file:
            root_file_list = root_file.split('\n')
            for item in root_file_list:
                if 'Benchmark' in item:
                    root_file = item

        print(root_file)
        install_file_path = self.mount_volume + '/' + root_file + '/Contents/MacOS/' # get install path

        #change current working directory to instal-file location
        os.chdir(install_file_path)

        #list files in install_file_path
        list_files = subprocess.Popen(['ls', install_file_path], stdout=subprocess.PIPE) #list files in mounted volume
        out, err = list_files.communicate()
        install_app = out.decode("utf-8") #decode byte object to string
        install_app = install_app.split('\n')
        install_app = list(filter(None, install_app)) #remove empty items from list
        print('>>>>',install_app, type(install_app), len(install_app))

        #IF THERE ARE MULTIPLE FILES IN CONTENTS/MACOS FOLDER:
        if len(install_app)>1:
            for item in install_app:
                #IF PRODUCT IS VRAY SWARM
                if 'vrswrm' in item:
                    install_app = item
                    break
                #IF PRODUCT IS LICENSE SERVER
                if 'vrlservice' in item and 'ibin' not in item:
                    install_app = item

        elif len(install_app) == 1:
            install_app = install_app[0]

        if unpack_install==False:
            return install_app
        else:
            return [install_app, install_file_path]



    def mac_get_host_app_path(self, platformName, platformVersion):

        #THIS FUNCTION RETURNS THE HOST-PLATFORM PATH IF SUCH IS ALREADY STORED IN DATA-VARIABLE
        #IF NOT IT CALLS THE SEARCH FUNCTION TO FIND AND STORE THE HOST-APP PATH FOR THE RESPECTIVE HOST-APP

        if platformName == 'Houdini':    

            try:
                return self.data[platformName][platformVersion]
            except:
                self.mac_search_host_app_path(search_path='/Applications/Houdini', max_depth=2, platformName=platformName)
                
        
        elif platformName == 'Cinema 4D':    

            try:
                return self.data[platformName][platformVersion]
            except:
                self.mac_search_host_app_path(search_path='/Applications', max_depth=3, platformName=platformName)


        elif platformName == 'SketchUp':    

            try:
                return self.data[platformName][platformVersion]
            except:
                self.mac_search_host_app_path(search_path='/Applications/', max_depth=2, platformName=platformName)


        elif platformName == 'Maya':

            try:
                return self.data[platformName][platformVersion]
            except:
                self.mac_search_host_app_path(search_path='/Applications/Autodesk', max_depth=2, platformName=platformName)
   

        elif platformName == 'Modo':

            try:
                return self.data[platformName][platformVersion]
            except:
                self.mac_search_host_app_path(search_path='/Applications', max_depth=1, platformName=platformName)


        #RETURN DATA AFTER EXECUTING SEARCH
        if platformName in ['Houdini', 'Cinema 4D', 'SketchUp', 'Maya', 'Modo']:
            try:
                return self.data[platformName][platformVersion]
            except:
                #self.data[platformName][platformVersion] = '{} {} not installed!'.format(platformName, platformVersion)
                self.data[platformName][platformVersion] = 'Not Installed'
                return self.data[platformName][platformVersion]
        else:
            #return '{} {} not yet supported!'.format(platformName, platformVersion)
            return 'Not Installed'

    def mac_search_host_app_path(self, search_path, max_depth, platformName):

        #THIS IS A RECURSIVE FUNCTION WHICH SEARCHES FOR THE HOST-APP-PATH
        #THE FUNCTION WORKS IN COOPERATION WITH THE MAC_GET_HOST_APP_PATH()

        if max_depth == 0:
            #print('Max Depth reached')
            return

        #GET THE CURRENT SEARCH DIRECTORY
        currentDirectory = pathlib.Path(search_path)

        #ROOT ALL ITEMS IN CURRENT DIRECTORY
        for currentFile in currentDirectory.iterdir():
            
            #IF ITEM IS DIRECTORY, CHECK IF HOST-APP IS FOUND AND IF NOT CALL THIS FUNCTION RECURSIVELY
            if currentFile.is_file() != True:
                #print('dir {}'.format(currentFile))

                if platformName == 'Houdini':
                    #print(currentFile)

                    if 'houdini fx' in currentFile.name.lower() and '.app' in currentFile.name.lower():

                        version = currentFile.name.lower().replace('houdini fx ', '')
                        version = version.replace('.app', '')
                        self.data['Houdini'][version] = currentFile.as_posix() + '/Contents/MacOS/houdinifx'
                        #print('file {}'.format(currentFile))

                        return

                    else:
                        self.mac_search_host_app_path(currentFile, max_depth=max_depth-1, platformName=platformName)

                elif platformName == 'Cinema 4D':

                    if 'cinema 4d.app' in currentFile.name.lower():

                        index_end = currentFile.as_posix().lower().rfind('/cinema 4d.app')
                        index_start = currentFile.as_posix().lower().rfind('cinema 4d ') + len('cinema 4d ')
                        version = currentFile.as_posix()[index_start : index_end]
                        
                        self.data['Cinema 4D'][version] = currentFile.as_posix() + '/Contents/MacOS/Cinema 4D'

                        return

                    else:
                        self.mac_search_host_app_path(currentFile, max_depth=max_depth-1, platformName=platformName)

                elif platformName == 'SketchUp':
                    
                    if 'sketchup.app' in currentFile.name.lower():
                
                        if '.app/contents' not in currentFile.as_posix().lower():
                            
                            index_start = currentFile.as_posix().lower().rfind('/sketchup ') + len('/sketchup ')
                            index_end = currentFile.as_posix().lower().rfind('/sketchup.app')
                            version = currentFile.as_posix()[index_start : index_end]

                            self.data['SketchUp'][version] = currentFile.as_posix() + '/Contents/MacOS/SketchUp'

                            #FIND THE NEWEST VERSION
                            try:
                                newest = int(self.data['SketchUp']['newest'])
                                version = int(version)
                                if version > newest:
                                    self.data['SketchUp']['newest'] = str(version)
                                    self.data['SketchUp'][''] = currentFile.as_posix() + '/Contents/MacOS/SketchUp'

                            except:
                                self.data['SketchUp']['newest'] = version
                                self.data['SketchUp'][''] = currentFile.as_posix() + '/Contents/MacOS/SketchUp'

                    else:
                        self.mac_search_host_app_path(currentFile, max_depth=max_depth-1, platformName=platformName)
                    
                elif platformName == 'Maya':

                    if 'maya.app' in currentFile.name.lower():

                        index_end = currentFile.as_posix().lower().rfind('/maya.app')
                        index_start = currentFile.as_posix().lower().find('/maya') + len('/maya')
                        version = currentFile.as_posix()[index_start : index_end]

                        self.data['Maya'][version] = currentFile.as_posix() + '/Contents/MacOS/Maya'

                    else:
                        self.mac_search_host_app_path(currentFile, max_depth=max_depth-1, platformName=platformName)
                
                elif platformName == 'Modo':

                    if 'modo' in currentFile.name.lower() and '.app' in currentFile.name.lower():

                        if 'Safe' not in currentFile.name:
                            index_start = currentFile.as_posix().lower().rfind('/modo') + len('/modo')
                            index_end = currentFile.as_posix().lower().rfind('.app')
                            version = currentFile.as_posix()[index_start : index_end]

                            if 'v' in version:
                                version = version.split('v')[0]

                            self.data['Modo'][version] = currentFile.as_posix() + '/Contents/MacOS/modo'

                            #FIND THE NEWEST VERSION
                            try:
                                newest = int(self.data['Modo']['newest'])
                                version = int(version)
                                if version > newest:
                                    self.data['Modo']['newest'] = str(version)
                                    self.data['Modo'][''] = currentFile.as_posix() + '/Contents/MacOS/modo'

                            except:
                                self.data['Modo']['newest'] = version
                                self.data['Modo'][''] = currentFile.as_posix() + '/Contents/MacOS/modo'
                    
                    else:
                        self.mac_search_host_app_path(currentFile, max_depth=max_depth-1, platformName=platformName)
            
            
            else:
                #print('file {}'.format(currentFile))
                pass




    def mac_get_host_app_path_OLD(self, platformName, platformVersion):

        data = {'Cinema 4D': {}, 'Maya': {}, 'SketchUp':{}, 'Nuke':{}, 'Modo':{}, 'Houdini':{}}

        for root, dirs, files in os.walk('/Applications'):

            for dir in dirs:

                path = os.path.join(root, dir)
                
                if 'Cinema 4D.app' in dir:

                    index_end = path.rfind('/Cinema 4D.app')
                    index_start = path.rfind('Cinema 4D ') + len('Cinema 4D ')
                    version = path[index_start : index_end]
                    
                    data['Cinema 4D'][version] = path + '/Contents/MacOS/Cinema 4D'

                elif 'Maya.app' in dir:

                    index_end = path.rfind('/Maya.app')
                    index_start = path.rfind('/maya') + len('/maya')
                    version = path[index_start : index_end]

                    data['Maya'][version] = path + '/Contents/MacOS/Maya'

                elif 'Nuke' in dir and '.app' in dir:
                    pass
                    # if 'Studio' not in path and 'commercial' not in path and 'NukeX' not in path and 'Assist' not in path:
                            
                    #     index_start = path.rfind('/Nuke') + len('/Nuke')
                    #     index_end = path.rfind('.app')
                    #     full_version = path[index_start : index_end]

                    #     if 'v' in full_version:
                    #         version = full_version.split('v')[0]

                    #     data['Nuke'][version] = path + '/Contents/MacOS/Nuke' + full_version

                    #     print(version)

                elif 'Modo' in dir and '.app' in dir:

                    if 'Safe' not in path:
                        index_start = path.rfind('/Modo') + len('/Modo')
                        index_end = path.rfind('.app')
                        version = path[index_start : index_end]

                        if 'v' in version:
                            version = version.split('v')[0]

                        data['Modo'][version] = path + '/Contents/MacOS/modo'

                        #FIND THE NEWEST VERSION
                        try:
                            newest = int(data['Modo']['newest'])
                            version = int(version)
                            if version > newest:
                                data['Modo']['newest'] = str(version)
                                data['Modo'][''] = path + '/Contents/MacOS/modo'

                        except:
                            data['Modo']['newest'] = version
                            data['Modo'][''] = path + '/Contents/MacOS/modo'

                elif 'SketchUp.app' in dir:
                    
                    if '.app/Contents' not in path:
                        
                        index_start = path.rfind('/SketchUp ') + len('/SketchUp ')
                        index_end = path.rfind('/SketchUp.app')
                        version = path[index_start : index_end]

                        data['SketchUp'][version] = path + '/Contents/MacOS/SketchUp' #BACKUP FOR SUBPROCESS-APP-LAUNCH
                        #data['SketchUp'][version] = path

                        #FIND THE NEWEST VERSION
                        try:
                            newest = int(data['SketchUp']['newest'])
                            version = int(version)
                            if version > newest:
                                data['SketchUp']['newest'] = str(version)
                                data['SketchUp'][''] = path + '/Contents/MacOS/SketchUp' #BACKUP FOR SUBPROCESS-APP-LAUNCH
                                #data['SketchUp'][''] = path

                        except:
                            data['SketchUp']['newest'] = version
                            data['SketchUp'][''] = path + '/Contents/MacOS/SketchUp' #BACKUP FOR SUBPROCESS-APP-LAUNCH
                            #data['SketchUp'][''] = path

                elif 'Houdini FX' in dir and '.app' in dir:

                    version = dir.replace('Houdini FX ', '')
                    version = version.replace('.app', '')
                    data['Houdini'][version] = path + '/Contents/MacOS/houdinifx'

        return data[platformName][platformVersion]


    def linux_get_host_app_path(self, platformName, platformVersion):

        #self.data = {'Maya': {}, 'Nuke':{}, 'Houdini':{}}
  

        try:
            return self.data[platformName][platformVersion]
        except:
            self.linux_search_host_app_path(platformName=platformName)


        #RETURN DATA AFTER EXECUTING SEARCH
        if platformName in ['Houdini', 'Maya', 'Nuke']:
            try:
                return self.data[platformName][platformVersion]
            except:
                self.data[platformName][platformVersion] = 'Not Installed'
                return self.data[platformName][platformVersion]
        else:
            return 'Not Installed'


    def linux_search_host_app_path(self, platformName=''):
        
        if platformName == 'Maya':
            dirs = os.listdir('/usr/autodesk')
            for dir in dirs:
                try:
                    if dir[-4:].isdigit():
                    
                        version = dir[-4:]
                        path = '/usr/autodesk/' + dir + '/bin/maya'
                        if os.path.exists(path):
                            self.data['Maya'][version] = path
                            logging.info('found: {}'.format(path))
                except:
                    pass
        
        elif platformName == 'Houdini':
            dirs = os.listdir('/opt')
            for dir in dirs:
                if 'hfs' in dir:
                    # if 'v' in dir:
                    #     executable_name = dir.split('v')[0]
                    version = dir.replace('hfs', '')

                    path = (Path('/opt') / dir / 'bin' / 'houdinifx').as_posix()
                    
                    if os.path.exists(path):
                        self.data['Houdini'][version] = path
                        logging.info('found: {}'.format(path))

        elif platformName == 'Nuke':
            dirs = os.listdir(str(Path.home()))
            for dir in dirs:
                if 'Nuke' in dir:
                    if 'v' in dir:
                        executable_name = dir.split('v')[0]
                        version = executable_name.replace('Nuke', '')

                    path = (Path.home() / dir / executable_name).as_posix()
                    
                    if os.path.exists(path):
                        self.data['Nuke'][version] = path
                        logging.info('found: {}'.format(path))



    def linux_get_host_app_path_OLD(self, platformName='', platformVersion=''):

        data = {'Maya': {}, 'Nuke':{}, 'Houdini':{}}

        dirs = os.listdir('/usr/autodesk')
        for dir in dirs:
            try:
                if dir[-4:].isdigit():
                
                    version = dir[-4:]
                    path = '/usr/autodesk/' + dir + '/bin/maya'
                    if os.path.exists(path):
                        data['Maya'][version] = path
                        logging.info('found: {}'.format(path))
            except:
                pass


        dirs = os.listdir(str(Path.home()))
        for dir in dirs:
            if 'Nuke' in dir:
                if 'v' in dir:
                    executable_name = dir.split('v')[0]
                    version = executable_name.replace('Nuke', '')

                path = (Path.home() / dir / executable_name).as_posix()
                
                if os.path.exists(path):
                    data['Nuke'][version] = path
                    logging.info('found: {}'.format(path))


        dirs = os.listdir('/opt')
        for dir in dirs:
            if 'hfs' in dir:
                # if 'v' in dir:
                #     executable_name = dir.split('v')[0]
                version = dir.replace('hfs', '')

                path = (Path('/opt') / dir / 'bin' / 'houdinifx').as_posix()
                
                if os.path.exists(path):
                    data['Houdini'][version] = path
                    logging.info('found: {}'.format(path))


        return data[platformName][platformVersion]


    #GENERATE CONFIG.XML FILE NEEDED FOR VRAY FOR NUKE INSTALLATION IN LINUX
    def linux_gen_nuke_config_xml(self, download_path = '', nuke_install_path = ''): 
        configXml = r'''<DefValues>
        <Value Name="PLUGINS" DataType="value">/home/support/Nuke12.2v2A/plugins/vray</Value>
        <Value Name="NUKEROOT" DataType="value">/home/support/Nuke12.2v2A</Value>
        </DefValues>
        '''

        xml = ET.ElementTree(ET.fromstring(configXml))
        root = xml.getroot()


        root[0].text = nuke_install_path  + '/plugins/vray'
        root[1].text = nuke_install_path


        xml.write(download_path + 'config_nuke.xml')


    #FIND NUKE INSTALLATIONS IN LINUX
    def linux_get_nuke_install_path(self, platformVersion=''):

        current_user_home_dir = os.path.expanduser("~")
        dirs = os.listdir(current_user_home_dir)
        dirs.sort(reverse=True)

        for dir in dirs:
            if 'Nuke' in dir:
                if platformVersion in dir:
                    # print(os.path.join(current_user_home_dir,dir))
                    return os.path.join(current_user_home_dir,dir)


#https://stackoverflow.com/questions/2882308/spawning-a-thread-in-python
class Threading (threading.Thread):

    def __init__(self, host_app, env=''):

        self.host_app = host_app

        if env != '':
            self.env = env
        else:
            self.env = ''

        threading.Thread.__init__(self)

    def run (self):

        if self.env != '':
            subprocess.run(self.host_app, env=self.env)
        else:
            subprocess.run(self.host_app)



instance = ChaosUtilities()




if __name__ == "__main__":
    #instance.startHostApp( productName='V-Ray', productVersion='5.10.03', platformName='3ds Max', platformVersion='2022')
    pass

    # instance.startHostApp(platformName='3ds Max', platformVersion='2020')
    # x = instance.win_getEnvVarFromRegistry('PATH')
    # print(x)


    #instance.startHostApp(platformName='Revit')
    # x = instance.win_getEnvVarFromRegistry('PATH')
    # print(x)



    # download_path = 'C:\\Users\\SvetlozarDraganov\\AppData\\Local\\Temp\\Chaos Installer\\'
    # build_file = 'vray_adv_37001_max2020_x64_29549.rar'
    # instance.zip_extract(download_path, build_file)
    # instance.install(download_path, build_file)

 