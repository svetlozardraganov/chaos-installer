from asyncio.format_helpers import extract_stack
import shutil
import os
import zipfile
import subprocess
import platform
import pathlib
import time
import json

if platform.system() == 'Windows':
    import CG_Registry
import CG_Uninstall
import CG_Utilities
 
import logging
logging.basicConfig(level=logging.DEBUG)

from PyQt5.QtCore import  QThreadPool
from PyQt5.Qt import QRunnable, pyqtSlot, QObject, pyqtSignal

import xml.etree.ElementTree as ET



class CG_ZIP_Installer():


    def install(self, productName, productVersion, platformName, platformVersion, download_path,
                build_full_path, build_name, App, remove_zip_files, phoenix_vray_version = '', start_host_app=''):
        
        #KILL HOST APP
        CG_Utilities.instance.killHostApp(productName=productName, platformName=platformName, platformVersion=platformVersion)

        #REMOVE PREVIOUS INSTALLATION
        CG_Uninstall.instance.uninstall(productName=productName, platformName=platformName, platformVersion=platformVersion,silent_uninstall=True, App=App)

        #EXTRACT ZIP / UNPACK INSTALL
        #extract_path = self.extractArchive(download_path=download_path, build_full_path=build_full_path, build_name=build_name, platformVersion=platformVersion)
        if platformName != 'Cinema 4D':
            if build_name.endswith('.zip'):
                extract_path = self.extractArchive(download_path=download_path, build_full_path=build_full_path)
            else: #efif build_name.endswith('.exe'):
                extract_path = self.unpackInstall(download_path=download_path, build_full_path=build_full_path, build_name = build_name, App=App)

        #START HOST APP
        if productName == 'V-Ray':

            if platformName == 'Maya':
                # self.startMayaVRay(zip_path=extract_path, maya_version=platformVersion, vray_version=productVersion)
                output = self.startMayaVRay(zip_path=extract_path, maya_version=platformVersion, vray_version=productVersion)
                host_app_path = output['host_app_path']
                env = output['env']
                self.ThreadingQThreadPool(host_app_path=host_app_path, env=env, App=App, remove_zip_files=remove_zip_files,
                    remove_extract_dir=remove_zip_files, extract_dir = extract_path)

            if platformName == 'Nuke':
                output = self.startNukeVRay(zip_path=extract_path, nuke_version=platformVersion, vray_version=productVersion)
                host_app_path = output['host_app_path']
                env = output['env']
                self.ThreadingQThreadPool(host_app_path=host_app_path, env=env, App=App, remove_zip_files=remove_zip_files,
                    remove_extract_dir=remove_zip_files, extract_dir = extract_path)

            if platformName == 'Cinema 4D':
                self.startCinema4dVRay(platformName=platformName, platformVersion=platformVersion, 
                                        start_host_app=start_host_app, download_path=download_path, 
                                        build_full_path=build_full_path, App=App)

            if platformName == 'Houdini':
                self.startHoudiniVRay(extract_path=extract_path, platformName=platformName, platformVersion=platformVersion,start_host_app=start_host_app, App=App)

        elif productName == 'Phoenix FD':
            # self.startMayaPhoenixFD(zip_path=extract_path, platformVersion=platformVersion,  vray_version= phoenix_vray_version)
            output = self.startMayaPhoenixFD(zip_path=extract_path, platformVersion=platformVersion, vray_version=phoenix_vray_version, phoenix_version = productVersion)
            host_app_path = output['host_app_path']
            env = output['env']
            print("Env Before Launching Host App")
            print(env)
            self.ThreadingQThreadPool(host_app_path=host_app_path, env=env, App=App, remove_zip_files=remove_zip_files,
                remove_extract_dir=remove_zip_files, extract_dir = extract_path)

        #START V-RAY STANDALONE:
        # self.startVrayStandalone(zip_path=extract_path)

        #REMOVE FILES
        # self.removeFiles(remove_zip_files=remove_zip_files, extract_path=extract_path)
        # if remove_zip_files == True:
            # CG_Utilities.instance.removeFilesAfterInstall(App=App,
            #                                             remove_extract_dir=remove_zip_files,
            #                                             extract_dir=extract_path)

    def extractArchive(self, download_path, build_full_path, output_path = None):

        #REPLACE SLASH SYMBOL SINSE SOMETIMES QT USES A RIGHT-SLASH INSTEAD OF LEFT ONE
        #download_path = download_path.replace('/', '\\')
        #build_full_path = build_full_path.replace('/', '\\')

        logging.info('\n' + '========================== Extract Archive ==========================')
        buildFile = pathlib.Path(build_full_path).name #get filename
        #buildFile = build_full_path.split('\\')[-1] #C:/builds/1/vray_adv_43002_maya2018_x64 (1).zip
        logging.info('download_path=' + download_path)
        logging.info('buildFile='+ buildFile)
        

        if output_path == None:
            extract_path = pathlib.Path(download_path) 
            extract_path = (extract_path / 'ZIP' / buildFile[:-4]).as_posix()
        else:
            extract_path = output_path

        print('extract_path=' + extract_path)
        print(build_full_path)
        
        # Check if directory exists
        # if os.path.isdir(download_path + )== True:
        #     print("Directory " + download_path + buildFile + "already exists. Removing it!")
            # shutil.rmtree(download_path)

        

        zip_ref = zipfile.ZipFile(build_full_path, 'r')

        uncompress_size = sum((file.file_size for file in zip_ref.infolist()))
        extracted_size = 0

        for file in zip_ref.infolist():
            extracted_size += file.file_size
            # print("%s %%" % int(extracted_size * 100 / uncompress_size))
            zip_ref.extract(file, extract_path)


        # zip_ref.extractall(extract_path)
        zip_ref.close()
        print('Extract completed')

        # return extract_path
        return extract_path

    def unpackInstall(self, download_path, build_full_path, build_name, App):
        download_path = pathlib.Path(download_path)
        logging.info('Unpacking ' + build_full_path)

        if platform.system() == 'Windows':
            extract_path = (download_path / 'ZIP'/ build_name[:-4]).as_posix()
            #extract_path = download_path + "\\ZIP\\" + build_name[:-4]
            subprocess.run([build_full_path, "-unpackInstall=" + extract_path])
        
        elif platform.system() == 'Linux':
            #ADD EXECUTE RIGHTS TO THE BUILD
            os.chmod(build_full_path, 0o0777)

            extract_path = (download_path / 'ZIP'/ build_name).as_posix()
            subprocess.run([build_full_path, "-unpackInstall=" + extract_path])

        elif platform.system() == 'Darwin':
            print("This is MacOS")

            build_path = os.path.split(os.path.abspath(build_full_path))[0] + '/' #get path only
            build_file = os.path.split(os.path.abspath(build_full_path))[1] #get filename only
            output = CG_Utilities.instance.mac_mount_disk(download_path=build_path, build_file=build_file, unpack_install=True)
            install_app = output[0]
            install_path = output[1]
            extract_path = (download_path / 'ZIP'/ build_file[:-4]).as_posix()

            for file in install_app:
                    
                #login using root account: https://stackoverflow.com/questions/51224674/execute-sudo-commands-with-subprocess-in-pycharm
                #print(subprocess.check_output('sudo -S echo success', shell=True, input=App.sudo_password))
                print(install_path+file + " -unpackInstall=" + extract_path)
                subprocess.run([install_path+file, "-unpackInstall=" + extract_path])
            

        logging.info('Unpack completed!')
        logging.info("Extract Path={}".format(extract_path))
        return extract_path


    def OLDextractArchive(self, download_path, build_full_path, build_name, platformVersion):


        logging.info('\n' + '========================== Extract Archive ==========================')
        logging.info('download_path=' + download_path)
        logging.info('build_name='+ build_name)
        #extract_path = download_path + 'ZIP\\' + build_name[:-4]# + '\\'
        extract_path = os.path.join(download_path,'ZIP',build_name[:-4])
        logging.info('extract_path=' + extract_path)

        logging.info(build_full_path)
        
        # Check if directory exists
        # if os.path.isdir(download_path + )== True:
        #     print("Directory " + download_path + buildFile + "already exists. Removing it!")
            # shutil.rmtree(download_path)

        

        zip_ref = zipfile.ZipFile(build_full_path, 'r')

        uncompress_size = sum((file.file_size for file in zip_ref.infolist()))
        extracted_size = 0

        for file in zip_ref.infolist():
            extracted_size += file.file_size
            # print("%s %%" % int(extracted_size * 100 / uncompress_size))
            zip_ref.extract(file, extract_path)


        # zip_ref.extractall(extract_path)
        zip_ref.close()
        print('Extract completed')

        # return extract_path
        return extract_path

    def OLDstartMayaTHISFILE(self, zip_path, maya_version):

        maya_exe = CG_Registry.registry.data['Maya'][maya_version] + r'bin\maya.exe'
        print(maya_exe)
        

        print('\n' + '========================== Set ZIP installation environment variables ==========================')

        my_env = os.environ.copy()

        my_env['MAYA_RENDER_DESC_PATH'] = zip_path + r'\maya_root\bin\rendererDesc'
        print("MAYA_RENDER_DESC_PATH=" + my_env['MAYA_RENDER_DESC_PATH'])

        my_env['VRAY_FOR_MAYA' + maya_version + '_MAIN'] = zip_path + r'\maya_vray'
        print('VRAY_FOR_MAYA' + maya_version + '_MAIN=' + my_env['VRAY_FOR_MAYA' + maya_version + '_MAIN'])

        my_env['VRAY_FOR_MAYA' + maya_version + '_PLUGINS'] = zip_path + r'\maya_vray\vrayplugins'
        print('VRAY_FOR_MAYA' + maya_version + '_PLUGINS=' + my_env['VRAY_FOR_MAYA' + maya_version + '_PLUGINS'])

        my_env['VRAY_AUTH_CLIENT_FILE_PATH'] = r'C:\Program Files\Common Files\ChaosGroup'
        print('VRAY_AUTH_CLIENT_FILE_PATH=' + my_env['VRAY_AUTH_CLIENT_FILE_PATH'])

        my_env['VRAY_OSL_PATH_MAYA' + maya_version] = zip_path + r'\vray\opensl'
        print('VRAY_OSL_PATH_MAYA' + maya_version + '=' + my_env['VRAY_OSL_PATH_MAYA' + maya_version])

        my_env['PATH'] = zip_path + r'\maya_root\bin;' + my_env['PATH']
        print('\n' + 'PATH=' + my_env['PATH'] + '\n')

        try:
            my_env['MAYA_PLUG_IN_PATH'] = zip_path + r'\maya_vray\plug-ins;' + my_env['MAYA_PLUG_IN_PATH']
        except:
            my_env['MAYA_PLUG_IN_PATH'] = zip_path + r'\maya_vray\plug-ins'
        print('MAYA_PLUG_IN_PATH=' + my_env['MAYA_PLUG_IN_PATH'])

        try:
            my_env['MAYA_SCRIPT_PATH'] = zip_path + r'\maya_vray\scripts;' + my_env['MAYA_SCRIPT_PATH']
        except:
            my_env['MAYA_SCRIPT_PATH'] = zip_path + r'\maya_vray\scripts'
        print('MAYA_SCRIPT_PATH=' + my_env['MAYA_SCRIPT_PATH'])

        try:
            my_env['PYTHONPATH'] = zip_path + r'\maya_vray\scripts;' + my_env['PYTHONPATH']
        except:
            my_env['PYTHONPATH'] = zip_path + r'\maya_vray\scripts'
        print('PYTHONPATH=' + my_env['PYTHONPATH'])

        try:
            my_env['XBMLANGPATH'] = zip_path + r'\maya_vray\icons;' + my_env['XBMLANGPATH']
        except:
            my_env['XBMLANGPATH'] = zip_path + r'\maya_vray\icons'
        print('XBMLANGPATH=' + my_env['XBMLANGPATH'])

        print('\n' + '========================== Starting Maya ==========================')
        maya = subprocess.Popen(maya_exe, env=my_env)
        maya.wait()

    def startMayaVRay(self, zip_path, maya_version, vray_version):
        
        #CONVERT STRING-PATH TO PATHLIB OBJECT
        zip_path = pathlib.Path(zip_path)
        
        maya_exe= self.getPlatformPath(platformName = 'Maya', platformVersion = maya_version)
        # maya_exe = CG_Registry.registry.data['Maya'][maya_version]
        logging.info(maya_exe)

        logging.info( '\n' + '========================== Set ZIP installation environment variables ==========================')

        my_env = os.environ.copy()
        

        #CHECK IF VERSION IS OLDER OR NEWER THAN > IS V-RAY 5 UPDATE 1  (ENV-VAR SETUP IS DIFFERENT)
        vray5_sp1_and_above = pathlib.Path(zip_path / 'maya_vray/rendererDesc').exists()
        
        if vray5_sp1_and_above == True:
           
            my_env['MAYA_RENDER_DESC_PATH'] = (zip_path / 'maya_vray/rendererDesc').as_posix() #CONVERT PATHLIB OBJECT TO STRING-PATH
            logging.info("MAYA_RENDER_DESC_PATH=" + my_env['MAYA_RENDER_DESC_PATH'])

        else:

            if platform.system() != 'Darwin':
                my_env['MAYA_RENDER_DESC_PATH'] = (zip_path / 'maya_root/bin/rendererDesc').as_posix() #CONVERT PATHLIB OBJECT TO STRING-PATH
            else:
                my_env['MAYA_RENDER_DESC_PATH'] = (zip_path / 'maya_root/Maya.app/Contents/bin/rendererDesc').as_posix() #CONVERT PATHLIB OBJECT TO STRING-PATH
            logging.info("MAYA_RENDER_DESC_PATH=" + my_env['MAYA_RENDER_DESC_PATH'])

        
        my_env['VRAY_FOR_MAYA' + maya_version +'_MAIN'] = (zip_path / 'maya_vray').as_posix()
        logging.info('VRAY_FOR_MAYA' + maya_version +'_MAIN=' + my_env['VRAY_FOR_MAYA' + maya_version +'_MAIN'])
        
        my_env['VRAY_FOR_MAYA' + maya_version +'_PLUGINS'] = (zip_path / 'maya_vray/vrayplugins').as_posix()
        logging.info('VRAY_FOR_MAYA' + maya_version +'_PLUGINS=' + my_env['VRAY_FOR_MAYA' + maya_version +'_PLUGINS'])
        

        if platform.system() != 'Windows':
            my_env['VRAY_AUTH_CLIENT_FILE_PATH'] =  (pathlib.Path.home() / '.ChaosGroup').as_posix()
        else:
            my_env['VRAY_AUTH_CLIENT_FILE_PATH'] = r'C:\Program Files\Common Files\ChaosGroup'
        print('VRAY_AUTH_CLIENT_FILE_PATH=' + my_env['VRAY_AUTH_CLIENT_FILE_PATH'])


        my_env['VRAY_OSL_PATH_MAYA' + maya_version] = (zip_path / 'vray/opensl').as_posix()
        logging.info('VRAY_OSL_PATH_MAYA' + maya_version + '=' + my_env['VRAY_OSL_PATH_MAYA' + maya_version])


        if platform.system() == 'Windows':
            
            if vray5_sp1_and_above == True:

                try:
                    my_env['PATH'] = (zip_path / 'maya_vray/bin/hostbin').as_posix() + os.pathsep +\
                                     (zip_path / 'maya_vray/bin').as_posix() + os.pathsep + my_env['PATH']
                except:
                    my_env['PATH'] = (zip_path / 'maya_vray/bin/hostbin').as_posix() + os.pathsep +\
                                     (zip_path / 'maya_vray/bin').as_posix() + os.pathsep
                logging.info('\n' + 'PATH=' + my_env['PATH'] + '\n')
            

            else:
                try:
                    my_env['PATH'] = (zip_path / 'maya_root/bin').as_posix() + os.pathsep + my_env['PATH']
                except:
                    my_env['PATH'] = (zip_path / 'maya_root/bin').as_posix()
                logging.info('\n' + 'PATH=' + my_env['PATH'] + '\n')

        elif platform.system() == 'Linux':
            
            if vray5_sp1_and_above != True:
                try:
                    my_env['LD_LIBRARY_PATH'] = (zip_path / 'maya_root/lib').as_posix() + os.pathsep + my_env['LD_LIBRARY_PATH']
                except:
                    my_env['LD_LIBRARY_PATH'] = (zip_path / 'maya_root/lib').as_posix()
                logging.info('\n' + 'LD_LIBRARY_PATH=' + my_env['LD_LIBRARY_PATH'] + '\n')

        elif platform.system() == 'Darwin':

            if vray5_sp1_and_above != True:
                    
                try:
                    my_env['DYLD_LIBRARY_PATH'] = (zip_path / 'maya_root/Maya.app/Contents/MacOS').as_posix() + os.pathsep + my_env['DYLD_LIBRARY_PATH']
                except:
                    my_env['DYLD_LIBRARY_PATH'] = (zip_path / 'maya_root/Maya.app/Contents/MacOS').as_posix()
                logging.info('\n' + 'DYLD_LIBRARY_PATH=' + my_env['DYLD_LIBRARY_PATH'] + '\n')
        
        
        try:
            my_env['MAYA_PLUG_IN_PATH'] = (zip_path / 'maya_vray/plug-ins').as_posix() + os.pathsep + my_env['MAYA_PLUG_IN_PATH']
        except:
            my_env['MAYA_PLUG_IN_PATH'] = (zip_path / 'maya_vray/plug-ins').as_posix()
        logging.info('MAYA_PLUG_IN_PATH=' + my_env['MAYA_PLUG_IN_PATH'])

        
        try:
            my_env['MAYA_SCRIPT_PATH'] = (zip_path / 'maya_vray/scripts').as_posix() + os.pathsep + my_env['MAYA_SCRIPT_PATH']
        except:
            my_env['MAYA_SCRIPT_PATH'] = (zip_path / 'maya_vray/scripts').as_posix()
        logging.info('MAYA_SCRIPT_PATH=' + my_env['MAYA_SCRIPT_PATH'])

        
        try:
            my_env['PYTHONPATH'] = (zip_path / 'maya_vray/scripts').as_posix() + os.pathsep + my_env['PYTHONPATH']
        except:
            my_env['PYTHONPATH'] = (zip_path / 'maya_vray/scripts').as_posix()
        logging.info('PYTHONPATH=' + my_env['PYTHONPATH'])


        if platform.system() != 'Linux':
            try:
                my_env['XBMLANGPATH'] = (zip_path / 'maya_vray/icons/').as_posix() + os.pathsep + my_env['XBMLANGPATH']
            except:
                my_env['XBMLANGPATH'] = (zip_path / 'maya_vray/icons/').as_posix()     
        else:
            try:
                my_env['XBMLANGPATH'] = (zip_path / 'maya_vray/icons/%B').as_posix() + os.pathsep + my_env['XBMLANGPATH']
            except:
                my_env['XBMLANGPATH'] = (zip_path / 'maya_vray/icons/%B').as_posix()
        logging.info('XBMLANGPATH=' + my_env['XBMLANGPATH'])


        if vray_version[0]=='5':
            try:
                my_env['MAYA_PRESET_PATH'] = (zip_path / 'maya_vray/presets').as_posix() + os.pathsep + my_env['MAYA_PRESET_PATH']
            except:
                my_env['MAYA_PRESET_PATH'] = (zip_path / 'maya_vray/presets').as_posix()
            logging.info('MAYA_PRESET_PATH=' + my_env['MAYA_PRESET_PATH'])


        try:
            my_env['MAYA_CUSTOM_TEMPLATE_PATH'] = (zip_path / 'maya_vray/scripts').as_posix() + os.pathsep + my_env['MAYA_CUSTOM_TEMPLATE_PATH']
        except:
            my_env['MAYA_CUSTOM_TEMPLATE_PATH'] = (zip_path / 'maya_vray/scripts').as_posix()
        logging.info('MAYA_CUSTOM_TEMPLATE_PATH=' + my_env['MAYA_CUSTOM_TEMPLATE_PATH'])


        logging.info( '\n' + '========================== Starting Maya ==========================')


        return {'host_app_path': maya_exe, 'env':my_env}

        # run_host_app_on_separate_thread = CG_Utilities.Threading(host_app=maya_exe, env=my_env)
        # run_host_app_on_separate_thread.start()


        # maya = subprocess.Popen(maya_exe, env=my_env)
        # maya.wait()

    def startCinema4dVRay(self, platformName, platformVersion, start_host_app, download_path, build_full_path, App):
        
        cinema_4d_exe= self.getPlatformPath(platformName = platformName, platformVersion = platformVersion)
        #cinema_4d_exe = CG_Registry.registry.data[platformName][platformVersion]

        if platform.system() == 'Windows':
            cinema_4d_plugins_path = cinema_4d_exe.replace('Cinema 4D.exe', 'plugins\\')
            logging.info('{} {} Installation found {}'.format(platformName, platformVersion, cinema_4d_exe))
            logging.info('Extracting files to {}'.format(cinema_4d_plugins_path))

            #EXTRACT ARCHIVE TO RESPECTIVE CINEMA 4D PLUGINS FOLDER
            while True:
                try:
                    self.extractArchive(download_path=download_path, build_full_path=build_full_path, output_path=cinema_4d_plugins_path)
                    break
                except:
                    logging.info('{} is locked. Wait 1s and try again'.format(cinema_4d_plugins_path + 'V-Ray'))
                    time.sleep(1)

        if start_host_app == True:
            my_env = os.environ.copy()
            self.ThreadingQThreadPool(host_app_path=cinema_4d_exe, env=my_env, App=App)
            
    def startHoudiniVRay(self, extract_path, platformName, platformVersion, start_host_app, App):
        
        
        houdini_exe= self.getPlatformPath(platformName=platformName, platformVersion=platformVersion)
        if platform.system() == 'Windows':
            houdini_packages_path = houdini_exe.replace('bin\houdinifx.exe', 'packages')
        elif platform.system() == 'Darwin':
             #Houdini Packages folder MacOs    
            #'/Applications/Houdini/Houdini18.5.408/Houdini FX 18.5.408.app/Contents/MacOS/houdinifx'
            #/Applications/Houdini/Houdini18.5.408/Frameworks/Houdini.framework/Versions/18.5/Resources/packages/vray_for_houdini.json

            find_app_index = houdini_exe.find('.app')
            find_split_inxed = houdini_exe.rfind('/', 0, find_app_index)
            houdini_packages_path = houdini_exe[:find_split_inxed] + '/Frameworks/Houdini.framework/Versions/' + platformVersion[:4] + '/Resources/packages/'
        elif platform.system() == 'Linux':
            houdini_packages_path = houdini_exe.replace('bin/houdinifx', 'packages')

        #GET SUBFOLDER OF EXTRACTED DIR
        sub_folder = os.listdir(extract_path)

        for item in sub_folder:
            if 'vray' in item:
                sub_folder = item
                break

        extract_path = os.path.join(extract_path, sub_folder)
        logging.info(extract_path)
        json_path = os.path.join(extract_path, 'deploy', 'docs', 'packages', 'vray_for_houdini.json')
        logging.info(json_path)

        #SET PATH IN JSON FILE
        json_file = open(json_path, "r")
        json_object = json.load(json_file)
        json_file.close()
        print(json_object)
        json_object["env"][0] = {'INSTALL_ROOT': extract_path}
        print(json_object)
        json_file = open(json_path, "w")
        json.dump(json_object, json_file)
        json_file.close()

        print(houdini_packages_path)

        #COPY JSON TO HOUDINI FOLDER
        if platform.system() == 'Windows' or platform.system() == 'Darwin':
            shutil.copy(json_path, houdini_packages_path)

        elif platform.system() == 'Linux':
            #SUDO LOGIN
            print(subprocess.check_output('sudo -S echo success', shell=True, input=App.sudo_password))
            cmd = ['sudo', 'cp', json_path, houdini_packages_path]
            copy = subprocess.Popen(cmd)
            copy.wait()



        if start_host_app == True:
            my_env = os.environ.copy()
            self.ThreadingQThreadPool(host_app_path=houdini_exe, env=my_env, App=App)


    def startMayaPhoenixFD(self, zip_path, platformVersion, vray_version, phoenix_version):

        #CONVERT STRING-PATH TO PATHLIB OBJECT
        zip_path = pathlib.Path(zip_path)
        
        maya_exe= self.getPlatformPath(platformName = 'Maya', platformVersion = platformVersion)
        #maya_exe = CG_Registry.registry.data['Maya'][platformVersion]
        logging.info(maya_exe)
        
        logging.info("========================== Set ZIP installation environment variables ==========================")
        my_env = os.environ.copy()
        # print('############## Get Env Vars ################')
        # print(my_env)
        
        my_env['PHX_FOR_MAYA' + platformVersion + '_MAIN'] = (zip_path / 'maya_phoenix').as_posix()

        #NEW VARIABLES PHOENIX 5
        #my_env['PHX_FOR_MAYA' + platformVersion + '_MAIN_x64'] = (zip_path / 'maya_phoenix').as_posix()

        if platform.system() == "Windows" or platform.system() == "Linux":
            my_env['PHX_FOR_MAYA' + platformVersion + '_BIN'] = (zip_path / 'phoenix/bin').as_posix()
            my_env['PHX_FOR_MAYA' + platformVersion + '_STNDPLUGS'] = (zip_path / 'phoenix/bin/plugins').as_posix()

        if platform.system() == "Darwin":
            my_env['PHX_FOR_MAYA' + platformVersion + '_BIN'] = (zip_path / 'ChaosPhoenix.app/Contents/MacOS').as_posix()
            my_env['PHX_FOR_MAYA' + platformVersion + '_STNDPLUGS'] = (zip_path / 'ChaosPhoenix.app/Contents/MacOS/plugins').as_posix()


        my_env['MAYA_PLUG_IN_PATH'] = (zip_path / 'maya_phoenix/plug-ins').as_posix()
        my_env['MAYA_SCRIPT_PATH'] = (zip_path / 'maya_phoenix/scripts').as_posix()

        if platform.system() == 'Windows':
            my_env['XBMLANGPATH'] = (zip_path / 'maya_phoenix/icons').as_posix()
        elif platform.system() == 'Linux':
            my_env['XBMLANGPATH'] = (zip_path / 'maya_phoenix/icons/%B').as_posix()
        elif platform.system()== 'Darwin':
            my_env['XBMLANGPATH'] = (zip_path / 'maya_phoenix/icons').as_posix()

        logging.info('PHX_FOR_MAYA' + platformVersion + '_MAIN =' + my_env['PHX_FOR_MAYA' + platformVersion + '_MAIN'])
        logging.info('MAYA_PLUG_IN_PATH =' + my_env['MAYA_PLUG_IN_PATH'])
        logging.info('MAYA_SCRIPT_PATH =' + my_env['MAYA_SCRIPT_PATH'])
        logging.info('XBMLANGPATH =' + my_env['XBMLANGPATH'])

        # if vray_version == '3':
        #     try:
        #         my_env['VRAY_FOR_MAYA' + platformVersion + '_PLUGINS_x64'] = my_env['VRAY_FOR_MAYA' + platformVersion + '_PLUGINS_x64'] + os.pathsep + (zip_path / 'maya_vray/vrayplugins').as_posix()
        #     except:
        #         my_env['VRAY_FOR_MAYA' + platformVersion + '_PLUGINS_x64'] = (zip_path / 'maya_vray/vrayplugins').as_posix()

        #     logging.info('VRAY_FOR_MAYA' + platformVersion + '_PLUGINS_x64 =' + my_env['VRAY_FOR_MAYA' + platformVersion + '_PLUGINS_x64'])
            
        # if vray_version == '4' or vray_version == '5':

        #     try:
        #         my_env['VRAY_FOR_MAYA' + platformVersion + '_PLUGINS'] = my_env['VRAY_FOR_MAYA' + platformVersion + '_PLUGINS'] + os.pathsep + (zip_path / 'phoenix/vray5plugins').as_posix()
        #     except:
        #         my_env['VRAY_FOR_MAYA' + platformVersion + '_PLUGINS'] = (zip_path / 'phoenix/vray5plugins').as_posix()
            

        # if vray_version == '5' or vray_version == '6':
        if platform.system()=='Windows' or platform.system()=='Linux':
            try:
                my_env['VRAY_FOR_MAYA' + platformVersion + '_PLUGINS'] = my_env['VRAY_FOR_MAYA' + platformVersion + '_PLUGINS'] + os.pathsep + (zip_path / ('phoenix/vray' + vray_version + 'plugins')).as_posix()
            except:
                my_env['VRAY_FOR_MAYA' + platformVersion + '_PLUGINS'] = (zip_path / ('phoenix/vray' + vray_version + 'plugins')).as_posix()
        
        elif platform.system()=='Darwin':
            try:
                my_env['VRAY_FOR_MAYA' + platformVersion + '_PLUGINS'] = my_env['VRAY_FOR_MAYA' + platformVersion + '_PLUGINS'] + os.pathsep + (zip_path / 'ChaosPhoenix.app/Contents/MacOS/' / ('vray' + vray_version + 'plugins')).as_posix()
            except:
                my_env['VRAY_FOR_MAYA' + platformVersion + '_PLUGINS'] = (zip_path / 'ChaosPhoenix.app/Contents/MacOS/' / ('vray' + vray_version + 'plugins')).as_posix()
        
            


            # if phoenix_version[0]=='4': #if Phoenix version is 4
            #     try:
            #         my_env['VRAY_FOR_MAYA' + platformVersion + '_PLUGINS'] = my_env['VRAY_FOR_MAYA' + platformVersion + '_PLUGINS'] + os.pathsep + (zip_path / 'maya_vray/vrayplugins').as_posix()
            #     except:
            #         my_env['VRAY_FOR_MAYA' + platformVersion + '_PLUGINS'] = (zip_path / 'maya_vray/vrayplugins').as_posix()
            
            # elif phoenix_version[0] == '5': #if Phoenix version is 5
            #     try:
            #         my_env['VRAY_FOR_MAYA' + platformVersion + '_PLUGINS'] = my_env['VRAY_FOR_MAYA' + platformVersion + '_PLUGINS'] + os.pathsep + (zip_path / 'phoenix/vray5plugins').as_posix()
            #     except:
            #         my_env['VRAY_FOR_MAYA' + platformVersion + '_PLUGINS'] = (zip_path / 'phoenix/vray5plugins').as_posix()
            

        logging.info('VRAY_FOR_MAYA' + platformVersion + '_PLUGINS =' + my_env['VRAY_FOR_MAYA' + platformVersion + '_PLUGINS'])
        
        logging.info("Launching Maya")
        # maya = subprocess.Popen(maya_exe)
        # maya.wait()
        # print("################## Set Env Vars ###############")
        # print(my_env)

        return {'host_app_path': maya_exe, 'env':my_env}

    def startNukeVRay(self, zip_path, nuke_version, vray_version):

        #CONVERT STRING-PATH TO PATHLIB OBJECT
        zip_path = pathlib.Path(zip_path)
        
        nuke_exe = self.getPlatformPath(platformName = 'Nuke', platformVersion = nuke_version)
        #nuke_exe = CG_Registry.registry.data['Nuke'][nuke_version]

        my_env = os.environ.copy()
        nuke_version = nuke_version.replace(".","_")

        my_env['VRAY_FOR_NUKE_' + nuke_version + '_PLUGINS'] = (zip_path / 'nuke_vray').as_posix()
        #THIS IF FOR STANDALONE
        #my_env['VRAY_FOR_NUKE_' + nuke_version + '_PLUGINS'] = (zip_path / 'vray_std').as_posix() + os.pathsep + my_env['VRAY_FOR_NUKE_' + nuke_version + '_PLUGINS']
        logging.info('VRAY_FOR_NUKE_' + nuke_version + '_PLUGINS=' + my_env['VRAY_FOR_NUKE_' + nuke_version + '_PLUGINS'])

        my_env['VRAY_RT_GPU_LIBRARY_PATH'] = (zip_path / 'vray_std').as_posix()
        logging.info('VRAY_RT_GPU_LIBRARY_PATH=' + my_env['VRAY_RT_GPU_LIBRARY_PATH'])

        try:
            my_env['NUKE_PATH'] = (zip_path / 'nuke_plugins').as_posix() + os.pathsep + my_env['NUKE_PATH']
        except:
            my_env['NUKE_PATH'] = (zip_path / 'nuke_plugins').as_posix()
        logging.info('NUKE_PATH=' + my_env['NUKE_PATH']),        
        
        if platform.system() == 'Windows':
            my_env['PATH'] = (zip_path / 'nuke_root').as_posix() + os.pathsep + my_env['PATH']
            logging.info('PATH=' + my_env['PATH'])

            
        elif platform.system() == 'Linux':
            try:
                my_env['LD_LIBRARY_PATH'] = (zip_path / 'nuke_root').as_posix() + os.pathsep + my_env['LD_LIBRARY_PATH']
            except:
                my_env['LD_LIBRARY_PATH'] = (zip_path / 'nuke_root').as_posix()
            logging.info('LD_LIBRARY_PATH=' + my_env['LD_LIBRARY_PATH'])

        
        #EDIT vrayconfig.xml TO ENABLE STANDALONE RENDERING IN NUKE
        #xml_file = r"C:\Users\SvetlozarDraganov\AppData\Local\Temp\Chaos-Installer\ZIP\vray_adv_51010_nuke13.0_x64_31135_archive\vray_std\vrayconfig.xml"
        xml_file = (zip_path / 'vray_std' / 'vrayconfig.xml').as_posix()
        tree = ET.parse(xml_file)
        root = tree.getroot()
        logging.info('vrayconfig.xml=' + root[0][0].text)
        root[0][0].text = (zip_path / 'nuke_vray' / 'vrayplugins').as_posix()
        tree.write(xml_file)

        nuke = subprocess.Popen(nuke_exe, env=my_env)

        return {'host_app_path': nuke_exe, 'env':my_env}

    def getPlatformPath(self, platformName, platformVersion):


        if platform.system() == 'Windows':
            platformPath = CG_Registry.registry.data[platformName][platformVersion]
            

        elif platform.system() == 'Linux':
            platformPath = CG_Utilities.instance.linux_get_host_app_path(platformName=platformName, platformVersion=platformVersion)


        elif platform.system() == 'Darwin':
            platformPath = CG_Utilities.instance.mac_get_host_app_path(platformName=platformName, platformVersion=platformVersion)


        return platformPath



    def removeFiles(self, remove_zip_files, extract_path):

        if remove_zip_files == True:
            print("removing folder: {}".format(extract_path))

            if os.path.isdir(extract_path)==True:
                print("Directory " + extract_path + "already exists. Removing it!")
                shutil.rmtree(extract_path)

    def startVrayStandalone(self, zip_path):
        my_env = os.environ.copy()

        my_env['PATH'] = zip_path + r'\maya_root\bin;' + zip_path + r'\vray\bin;' + my_env['PATH']
        print(my_env['PATH'])

        try:
            my_env['VRAY_PLUGINS'] = zip_path + r'\maya_vray\vrayplugins;' + my_env['VRAY_PLUGINS']
        except:
            my_env['VRAY_PLUGINS'] = zip_path + r'\maya_vray\vrayplugins'
        print(my_env['VRAY_PLUGINS'])

        my_env['VRAY_OSL_PATH'] = zip_path + r'\vray\opensl'
        print(my_env['VRAY_OSL_PATH'])

        my_env['VRAY_AUTH_CLIENT_FILE_PATH'] = r'C:\Program Files\Common Files\ChaosGroup'
        print(my_env['VRAY_AUTH_CLIENT_FILE_PATH'])

        vrayStandalone = subprocess.Popen('cmd.exe', env = my_env, cwd = zip_path + r'\maya_vray\bin')
        vrayStandalone.wait()

    def getZipInstallationsFromFolder(self, path):

        # list_subfolders_with_paths = [f.path for f in os.scandir(path) if f.is_dir()]
        try:
            zip_folders = next(os.walk(path))[1]
            return zip_folders
        except:
            logging.info("Zip Installation folder is empty")
        # print(zip_folders)

        
        # data = self.getZipVersionsFromString(zip_folders[0])

        #START HOST APPLICATION WITH V-RAY FROM SPECIFIC FOLDER
        # self.startMayaVRay(zip_path= path + data['zip_folder'], 
        #                     maya_version= data['platformVersion'],
        #                     vray_version= data['productVersion'][0])

    def getZipVersionsFromString(self, input_string):

        input_string = input_string.lower()

        logging.info("Input string = {}".format(input_string))
        # import re

        if 'vray' in input_string and 'phoenixfd' not in input_string:
            productName = 'V-Ray'

            if 'maya' in input_string:

                platformName = 'Maya'

                platform_version_start_index = input_string.find('_maya') + len('_maya')
                
                if '.5' not in input_string:
                    platform_version_end_index = platform_version_start_index + 4
                else:
                    platform_version_end_index = platform_version_start_index + 6
   
                platform_version = input_string[platform_version_start_index : platform_version_end_index]

                productVersion_start_index = input_string.find('vray_adv_') + len('vray_adv_')
                productVersion_end_index = input_string.find('_maya', productVersion_start_index)
                productVersion = input_string[productVersion_start_index:productVersion_end_index]
                productVersion = productVersion[:1] + '.' + productVersion[1:3] + '.' + productVersion[3:]

            elif 'nuke' in input_string:
                #!vray_adv_50000_nuke12.2_x64.zip / vray_adv_50000_nuke12.2_centos6.zip / vray_adv_36001_nuke11.0_linux_x64.zip
                platformName = 'Nuke'

                platform_version_start_index = input_string.find('_nuke') + len('_nuke')
                if platform.system() == 'Windows':
                    platform_version_end_index = input_string.find('_x64', platform_version_start_index)
                elif platform.system() == 'Linux':
                    if 'linux' in input_string:
                        platform_version_end_index = input_string.find('_linux', platform_version_start_index)
                    elif 'centos' in input_string:
                        platform_version_end_index = input_string.find('_centos', platform_version_start_index)
                platform_version = input_string[platform_version_start_index : platform_version_end_index]

                productVersion_start_index = input_string.find('vray_adv_') + len('vray_adv_')
                productVersion_end_index = input_string.find('_nuke', productVersion_start_index)
                productVersion = input_string[productVersion_start_index:productVersion_end_index]
                productVersion = productVersion[:1] + '.' + productVersion[1:3] + '.' + productVersion[3:]

            elif 'max' in input_string:
                #vray_adv_43002_max2021_x64.exe

                platformName = '3ds Max'

                platform_version_start_index = input_string.find('_max') + len('_max')
                platform_version_end_index = input_string.find('_x64', platform_version_start_index)
                platform_version = input_string[platform_version_start_index : platform_version_end_index]

                productVersion_start_index = input_string.find('vray_adv_') + len('vray_adv_')
                productVersion_end_index = input_string.find('_max', productVersion_start_index)
                productVersion = input_string[productVersion_start_index:productVersion_end_index]
                productVersion = productVersion[:1] + '.' + productVersion[1:3] + '.' + productVersion[3:]


        #IF PHOENIX FD 
        elif 'vray' in input_string and 'phoenixfd' in input_string:
                
            productName = 'Phoenix FD'
            platformName = 'Maya'

            platform_version_start_index = input_string.find('_maya') + len('_maya')
            platform_version_end_index = input_string.find('_vray', platform_version_start_index)
            platform_version = input_string[platform_version_start_index : platform_version_end_index]
            
            productVersion_start_index = input_string.find('phoenixfd_adv_') + len('phoenixfd_adv_')
            productVersion_end_index = input_string.find('_maya', productVersion_start_index)
            productVersion = input_string[productVersion_start_index:productVersion_end_index]
            productVersion = productVersion[:1] + '.' + productVersion[1:3] + '.' + productVersion[3:]

            vrayVersion_index = input_string.find('vray') + len('vray')
            phoenix_vray_version = input_string[vrayVersion_index]



        #PRINT BUILD VERSIONS:
        logging.info("Product = {}".format(productName))
        logging.info('Product Name = {} for {}'.format(productName, platformName))
        logging.info("Product Version = {}".format(productVersion))
        logging.info("Platform Name = {}".format(platformName))
        logging.info("Platform Version = {}".format(platform_version))

        if productName == 'Phoenix FD':
            logging.info('Phoenix FD for V-Ray: {}'.format(phoenix_vray_version))
        

        #RETURN BUILD VERSION DATA
        if productName == 'V-Ray':
            return {'zip_folder': input_string, 'productName': productName, 'productVersion':productVersion,
                    'platformName':platformName, 'platformVersion':platform_version}

        elif productName == 'Phoenix FD':
            return {'zip_folder': input_string, 'productName': productName, 'productVersion':productVersion,
                    'platformName':platformName, 'platformVersion':platform_version, 'phoenixVrayVersion': phoenix_vray_version}

    def startHostAppFromZipFolder(self, path, folder, App):

        data = self.getZipVersionsFromString(input_string=folder)
        
        #START HOST APPLICATION WITH V-RAY FROM SPECIFIC FOLDER
        # self.startMayaVRay(zip_path= path + folder, 
        #                     maya_version= data['platformVersion'],
        #                     vray_version= data['productVersion'][0])

        if 'vray' in folder and 'maya' in folder and 'phoenix' not in folder:
            output = self.startMayaVRay(zip_path=path + folder, maya_version=data['platformVersion'], vray_version=data['productVersion'][0])
            host_app_path = output['host_app_path']
            env = output['env']
            self.ThreadingQThreadPool(host_app_path=host_app_path, env=env, App=App)

        if 'maya' in folder and 'phoenix' in folder:
            output = self.startMayaPhoenixFD(zip_path=path + folder, platformVersion=data['platformVersion'], vray_version=data['productVersion'][0])
            host_app_path = output['host_app_path']
            env = output['env']
            self.ThreadingQThreadPool(host_app_path=host_app_path, env=env, App=App)

        if 'vray' in folder and 'nuke' in folder:
            output = self.startNukeVRay(zip_path=path + folder, nuke_version=data['platformVersion'], vray_version=data['productVersion'][0])
            host_app_path = output['host_app_path']
            env = output['env']
            self.ThreadingQThreadPool(host_app_path=host_app_path, env=env, App=App)

    def OLDnightly_zip_install(self, download_path, build_file, productName, productVersion, platformName, platformVersion,
                            silent_install, start_host_app, remove_files_after_install, quit_after_install, App):
        
        #KILL HOST APP
        CG_Utilities.instance.killHostApp(productName=productName, platformName=platformName, platformVersion=platformVersion)

        #REMOVE PREVIOUS INSTALLATION
        CG_Uninstall.instance.uninstall(productName=productName, platformName=platformName, platformVersion=platformVersion,silent_uninstall=True, App=App)

        if platform.system() == 'Windows':
            if platformName == 'Cinema 4D':

                cinema_4d_exe = CG_Registry.registry.data[platformName][platformVersion]
                cinema_4d_plugins_path = cinema_4d_exe.replace('Cinema 4D.exe', 'plugins\\')
                logging.info('{} {} Installation found {}'.format(platformName, platformVersion, cinema_4d_exe))
                
                logging.info('Extracting files to {}'.format(cinema_4d_plugins_path))


                #self.extractArchive(download_path=download_path, build_full_path=download_path + build_file, output_path=cinema_4d_plugins_path)
                while True:
                    try:
                        self.extractArchive(download_path=download_path, build_full_path=download_path + build_file, output_path=cinema_4d_plugins_path)
                        break
                    except:
                        logging.info('{} is locked. Wait 1s and try again'.format(cinema_4d_plugins_path + 'V-Ray'))
                        time.sleep(1)

                if start_host_app == True:
                    my_env = os.environ.copy()
                    self.ThreadingQThreadPool(host_app_path=cinema_4d_exe, env=my_env, App=App)


    #THE FOLLOWING DEFS ARE FOR RUNNING HOST APP ON A SEPARATE THREAD
    def ThreadingQThreadPool(self, host_app_path, env, App, remove_zip_files='', remove_extract_dir='', extract_dir=''):

        self.threadpool = QThreadPool()
        logging.info("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())

        self.host_app_process = ThreadingRunProcess(host_app_path=host_app_path, env=env)

        #SIGNALS CONNECTION
        self.host_app_process.signals.finished.connect(lambda: 
                self.ThreadingQThreadPoolFinished(App=App,
                                                remove_zip_files=remove_zip_files,
                                                remove_extract_dir=remove_extract_dir,
                                                extract_dir=extract_dir))

        #START SEPARATE THREAD
        self.threadpool.start(self.host_app_process)

    def ThreadingQThreadPoolFinished(self, App, remove_zip_files, remove_extract_dir, extract_dir):

        #THIS FUNCTION REMOVE ZIP-FILES AFTER HOST-APP-EXIT
        if remove_zip_files == True:
            CG_Utilities.instance.removeFilesAfterInstall(App=App,
                                                        remove_extract_dir=remove_extract_dir,
                                                        extract_dir=extract_dir)

        



class ThreadingSignals(QObject):
    finished = pyqtSignal()


class ThreadingRunProcess(QRunnable):

    def __init__(self, host_app_path, env):
        super(ThreadingRunProcess, self).__init__()

        self.signals = ThreadingSignals()
        self.host_app_path = host_app_path
        self.env = env

        # self.run()

    @pyqtSlot()
    def run(self):

        print(self.host_app_path)
        subprocess.call(self.host_app_path, env=self.env)

        self.signals.finished.emit()


instance = CG_ZIP_Installer()




