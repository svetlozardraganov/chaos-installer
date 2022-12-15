import platform

import subprocess
import os
import logging
from PyQt5.QtCore import QTimer
import CG_Utilities
import time

logging.basicConfig(level=logging.INFO)


if platform.system() == 'Windows':
    import winreg

    class CG_Uninstall():

        cg_uninstall_products = []
        version = []
        uninstall_string = []
        product = []

        def __init__(self):

            #CLEAR PARAMETERS WHEN CLASS IS REINITIALIZAED - NEEDED FOR THE UPDATE OF THE UNINSTALL WIDGETS
            self.cg_uninstall_products = []
            self.version = []
            self.uninstall_string = []
            self.product = []

            #THIS IS THE ROOT OF THE UNINSTALL REGISTRY KEY WHERE ALL APPLICATION ARE LISTED
            uninstall_root_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall", 0,(winreg.KEY_WOW64_64KEY + winreg.KEY_READ))

            #LOOP THROUGH ENTIRE LIST AND FIND CHAOSGROUP FOLDERS
            try:
                count = 0
                while 1:
                    product = []
                    uninstall_folder_name = winreg.EnumKey(uninstall_root_key, count)

                    #IF V-RAY IS FOUND IN FOLDER NAME GET ANOTHER KEY FROM THIS FOLDER AND LOOP THROUGH ITS SUBKEYS
                    if "V-Ray" in uninstall_folder_name or "Phoenix FD" in uninstall_folder_name or \
                            "Project Lavina" in uninstall_folder_name or "Chaos License Server" in uninstall_folder_name or \
                            "pdplayer" in uninstall_folder_name or 'Vantage' in uninstall_folder_name:
                        print(uninstall_folder_name)

                        #GET THE KEY
                        cg_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall" +"\\" + uninstall_folder_name, 0, (winreg.KEY_WOW64_64KEY + winreg.KEY_READ))

                        #LOOP THROUGH SUBKEYS
                        try:
                            i = 0
                            while True:
                                cg_subKey = winreg.EnumValue(cg_key, i)
                                # CONVERT TUPLE TO LIST AND KEEP ONLY THE FIRST TWO ITEMS FROM IT
                                # print(list(cg_subKey)[0:2])
                                product.append(list(cg_subKey)[0:2])
                                i += 1
                        except WindowsError:
                            self.cg_uninstall_products.append(product)

                    count = count + 1
            #WHEN LOOP ENDS, PRINT AN ERROR AND ADD FOUNDED ITEMS IN CLASS VARIABLES
            except WindowsError as err:
                logging.critical(err)
                self.version = self.getVersions()
                self.uninstall_string = self.getUninstallString()
                self.product = self.getCgProduct()

                output = self.getPlatformDetailsFromProductName(self.product)
                self.productName = output['productName']
                self.platformName = output['platformName']
                self.platformVersion = output['platformVersion']

        def getVersions(self):
            output = []
            for i in self.cg_uninstall_products:
                for j in i:
                    if j[0] == "DisplayVersion":
                        output.append(j[1])
            return output

        def getUninstallString(self):
            output = []
            for i in self.cg_uninstall_products:
                for j in i:
                    if j[0] == "UninstallString":
                        output.append(j[1])
            return output

        def getCgProduct(self):
            output = []
            for i in self.cg_uninstall_products:
                for j in i:
                    if j[0] == "DisplayName":
                        output.append(j[1])
            return output

        def getPlatformDetailsFromProductName(self, productNameFullList):

            productNameList = []
            platformNameList = []
            platformVersionList = []

            for item in productNameFullList:
                productNameFull = item
                productName = ''
                platformName = ''
                platformVersion = ''

                if 'V-Ray for 3dsmax' in productNameFull:
                    productName = 'V-Ray'
                    platformName = '3ds Max'
                    start_index = productNameFull.find('3dsmax') + len('3dsmax') + 1
                    end_index = productNameFull.find('for', start_index) -1
                    platformVersion = productNameFull[start_index : end_index]

                elif 'V-Ray for Cinema 4D' in productNameFull:
                    productName = 'V-Ray'
                    platformName = 'Cinema 4D'
                    start_index = productNameFull.find('4D') + len('4D') + 1
                    platformVersion = productNameFull[start_index : ]

                elif 'for Houdini' in productNameFull:
                    productName = 'V-Ray'
                    platformName = 'Houdini'
                    start_index = productNameFull.find('Houdini') + len('Houdini') + 1
                    platformVersion = productNameFull[start_index : ]

                elif 'V-Ray for Maya' in productNameFull:
                    productName = 'V-Ray'
                    platformName = 'Maya'
                    start_index = productNameFull.find('Maya') + len('Maya') + 1
                    end_index = productNameFull.find('for', start_index) -1
                    platformVersion = productNameFull[start_index : end_index]

                elif 'V-Ray for MODO' in productNameFull:
                    productName = 'V-Ray'
                    platformName = 'Modo'

                elif 'V-Ray for Nuke' in productNameFull:
                    productName = 'V-Ray'
                    platformName = 'Nuke'
                    start_index = productNameFull.find('Nuke') + len('Nuke') + 1
                    platformVersion = productNameFull[start_index : ]

                elif 'V-Ray for Revit' in productNameFull:
                    productName = 'V-Ray'
                    platformName = 'Revit'
                
                elif 'V-Ray for Rhinoceros' in productNameFull:
                    productName = 'V-Ray'
                    platformName = 'Rhino'

                elif 'V-Ray for SketchUp' in productNameFull:
                    productName = 'V-Ray'
                    platformName = 'SketchUp'

                elif 'V-Ray Standalone' in productNameFull:
                    productName = 'V-Ray'
                    platformName = 'Standalone'

                elif 'V-Ray for Unreal' in productNameFull:
                    productName = 'V-Ray'
                    platformName = 'Unreal'

                elif 'V-Ray Swarm' in productNameFull:
                    productName = 'V-Ray'
                    platformName = 'Swarm'

                elif 'V-Ray Application SDK' in productNameFull:
                    productName = 'V-Ray'
                    platformName = 'Application SDK'



                elif 'Phoenix FD for 3ds Max' in productNameFull:
                    productName = 'Phoenix FD'
                    platformName = '3ds Max'
                    start_index = productNameFull.find('3ds Max') + len('3ds Max') + 1
                    platformVersion = productNameFull[start_index : ]
                
                elif 'Phoenix FD for Maya' in productNameFull:
                    productName = 'Phoenix FD'
                    platformName = 'Maya'
                    start_index = productNameFull.find('Maya') + len('Maya') + 1
                    end_index = productNameFull.find('for', start_index) -1
                    platformVersion = productNameFull[start_index : end_index]

                elif 'Project Lavina' in productNameFull:
                    productName = 'Lavina'
                    # platformName = 'Lavina'

                elif 'Pdplayer 64' in productNameFull:
                    productName = 'PDPlayer'
                    # platformName = 'Pdplayer'

                elif 'Chaos License Server' in productNameFull:
                    productName = 'License Server'
                    # platformName = 'License Server '
                    
                productNameList.append(productName)
                platformNameList.append(platformName)
                platformVersionList.append(platformVersion)
                
            return {'productName':productNameList ,'platformName':platformNameList, 'platformVersion':platformVersionList}


        def uninstall(self,productName, platformName, platformVersion, silent_uninstall, App, uninstall_string = None): #"C:\Program Files\Chaos Group\V-Ray\3ds Max 2017\uninstall\installer.exe" -uninstall="C:\Program Files\Chaos Group\V-Ray\3ds Max 2017\uninstall\install.log" -uninstallApp="V-Ray for 3dsmax 2017 for x64"
            

            CG_Utilities.instance.killHostApp(productName=productName, platformName=platformName, platformVersion=platformVersion)

            #IF UNINSTALL STRING IS NOT SUBMITTED, GET IT.
            if uninstall_string == None:
                uninstall_string = self.getUninstallStringByProduct(productName=productName, platformName=platformName, platformVersion=platformVersion )

                #IF UNINSTALL STRING CANNOT BE FOUND, THE PRODUCT IS NOT INSTALLED, THERE IS NO NEED TO RUN UNINSTALLATION
                if uninstall_string == None:
                    logging.info('Uninstallatalation of previous version is not needed')
                    return
            

            split_1 = uninstall_string.find("-uninstall=")
            split_2 = uninstall_string.find("-uninstallApp=")

            arg1 = uninstall_string[1:split_1 - 2]
            arg2 = uninstall_string[split_1:split_2 - 1]
            arg3 = uninstall_string[split_2:]

            if silent_uninstall == True:
                arg4 = "-gui=0"
                logging.info("Installation cmd: " + arg1 + " " + arg2 + " " + arg3 + " " + arg4)
                subprocess.call([arg1, arg2, arg3, arg4], shell=True)
                self.checkUnintallProcessRunning()

                #RETURN PRODUCT NAME TO PRINT MSG IN STATUS BAR THE UNINSTALLATION IS COMPLETED
                return uninstall_string[split_2 + len("-uninstallApp=") +1: -1] + ' Sucessfully uninstalled!'
                
            else:
                logging.info("Installation cmd: " + arg1 + " " + arg2 + " " + arg3)
                subprocess.call([arg1, arg2, arg3], shell=True)


            #WAIT THE PRODUCT ROOT DIR TO BE REMOVED - THIS MEANS THE UNINSTALL PROCESS IS COMPLETED SUCCESSFULLY
            # if silent_uninstall == True:
            #     parent_dir_1 = os.path.abspath(os.path.join(arg1, os.pardir))
            #     parent_dir_2 = os.path.abspath(os.path.join(parent_dir_1, os.pardir))
            #     # timer = QTimer()
            #     timer = 0
            #     while os.path.exists(parent_dir_2):
            #         time.sleep(1)
            #         # QTimer.singleShot(500, App ,lambda: print('yes'))
            #         timer +=1
            #         if timer > 5:
            #             error_msg = uninstall_string[split_2 + len("-uninstallApp=") +1: -1] + ' Uninstallation FAILED!'
            #             more_information = 'Try to uninstall product manually and clean up the leftover files!'
            #             CG_Utilities.instance.PyQTerrorMSG(error_msg=error_msg, more_information=more_information, App=App)
            #             return error_msg

                        
                
            #     #RETURN PRODUCT NAME TO PRINT MSG IN STATUS BAR THE UNINSTALLATION IS COMPLETED
            #     return uninstall_string[split_2 + len("-uninstallApp=") +1: -1] + ' Sucessfully uninstalled!'
        

        def getUninstallStringByProduct(self, productName='', platformName='', platformVersion=''):
            # print(len(self.product))
            
            for i in range(len(self.product)):
                if (productName in self.product[i]) and (platformName.lower() in self.product[i].lower()) and (platformVersion in self.product[i]):
                    logging.info("Uninstalling {0}".format(self.product[i]))
                    return self.uninstall_string[i]
            


        def checkUnintallProcessRunning(self):
            #CHAOS UNINSTALL PROCESS IS RUNNING IN ANOTHER PROCESS, SO THE DEFAULT EXIT-CODES FROM SUBPROCESS DOESN'T GIVE PROPER RESULT FOR THE PROCESS-END
            #THIS FUNCTIONS CHECKS IF VRAYUNINST-PROCESS IS RUNNING AND WAITS UNTIL IT'S FINISHED
            
            wmic_cmd = ['wmic',
                'process',
                'get',
                'Name',
                '/format:csv']

            while True:

                process = subprocess.Popen(wmic_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                output = process.communicate()[0]
                # exitCode = process.returncode
                # process_pid = process.pid

                if b'vrayuninst' in output:
                    pass
                    # print('still running')
                else:
                    break
                    # print('completed!!!!')

            
elif platform.system() == 'Darwin' or platform.system() == 'Linux':

    class CG_Uninstall():

        cg_uninstall_products = []
        product = []
        version = []
        uninstall_string = []

        productName = []
        platformName = []
        platformVersion = []


        def __init__(self):
            
            #RESET VARIABLES IN ORDER TO UPDATE UNINSTALL TAB PROPERLY AFTER REMOVING AN APP
            self.cg_uninstall_products = []
            self.product = []
            self.version = []
            self.uninstall_string = []

            self.productName = []
            self.platformName = []
            self.platformVersion = []


            #GET UNINSTALL DATA FROM CHAOS-INSTALLS
            chaos_installs_path = '/var/log/chaos_installs'
            chaos_installs_file = open(chaos_installs_path, 'r')            

            for item in chaos_installs_file:

                #FIND LINE CONTAINING '=[UN]'
                if '=[UN]' in item:
                    item = item.split('=[UN]')[1] #V-Ray for Cinema 4D R23=[UN]/Applications/ChaosGroup/V-Ray/Cinema4DR23/uninstall/installer.app/Contents/MacOS/installer.bin -uninstallApp="V-Ray for Cinema 4D R23" -log="/Applications/ChaosGroup/V-Ray/Cinema4DR23/uninstall/install.log"
                    item = item.split(' -')
                    path = item[0].replace('"', '')
                    app = '-' + item[1]
                    log = '-' + item[2].strip('\n')
                    
                    #GET THE PATH TO INSTALLATION FOLDER
                    index = path.find('installer')
                    uninstall_path = path[:index]


                    #FIND INSTALLATION .XML FILE WHERE VERSION ARE WRITTEN
                    try:
                        for file in os.listdir(uninstall_path):

                            #REMOVE CHAOS PLAYER FROM THE SEARCH
                            if file.endswith(".xml") and 'chaosplayer_install' not in file:
                                #print(file)
                                #logging.info("{} found ".format(file))

                                #GET VERSION/PRODUCT NAME FROM .XML FILE

                                major_ver = self.find_in_xml(xml=uninstall_path+file, text='MajorVersion')
                                minor_ver = self.find_in_xml(xml=uninstall_path+file, text='MinorVersion')
                                minest_ver = self.find_in_xml(xml=uninstall_path+file, text='MinestVersion')
                                version = major_ver + '.' + minor_ver + '.' + minest_ver

                                

                                product_full_name = self.find_in_xml(xml=uninstall_path+file, text='Fullname')

                                #logging.info('\n uninstall_arg1 = {} \n uninstall_arg2 = {} \n uninstall_arg3 = {} \n product_full_name = {} \n version = {} \n'.format(path, app, log, product_full_name, version))
                                
                                self.product.append(product_full_name)
                                self.version.append(version)
                                self.uninstall_string.append(path + ' ' + app + ' ' + log)
                                #print(path + ' ' + app + ' ' + log + '\n')

                                output = self.getPlatformDetailsFromProductName(product_full_name)
                                self.productName.append(output['productName'])
                                self.platformName.append(output['platformName'])
                                self.platformVersion.append(output['platformVersion'])


                    except:
                        pass
                    #     logging.info(".xml file not found in {} ".format(uninstall_path))
                    #     data.append({'uninstall_arg1':path, 'ininstall_arg2':app, 'uninstall_arg3':log})
                        
                    #print('\n')
                    # data.append({'uninstall_arg1':path, 'ininstall_arg2':app, 'uninstall_arg3':log, 'product_full_name':product_full_name, 'version':version})
                    # data.append({'uninstall_arg1':path, 'ininstall_arg2':app, 'uninstall_arg3':log})     
            
            chaos_installs_file.close()

        def find_in_xml(self, xml, text):

            text_start = '<' + text + '>'
            text_end = '</' + text + '>'

            with open(xml, 'r') as xml_file:
                
                while True:
                    readline = xml_file.readline()
                    
                    if text in readline and '!' not in readline:
                        ind_start = readline.find(text_start) + len(text_start)
                        ind_end = readline.find(text_end)
                        output = readline[ind_start:ind_end]
                        
                        logging.info('Output = {}'.format(output))
                        return output

        def getPlatformDetailsFromProductName(self, productNameFull):
            
            productName = ''
            platformName = ''
            platformVersion = ''

            #print('>>>>>>> {}'.format(productNameFull))

            if 'V-Ray for Cinema 4D' in productNameFull:
                productName = 'V-Ray'
                platformName = 'Cinema 4D'
                start_index = productNameFull.find('4D') + len('4D') + 1
                platformVersion = productNameFull[start_index : ]

            elif 'for Houdini' in productNameFull:
                productName = 'V-Ray'
                platformName = 'Houdini'
                start_index = productNameFull.find('Houdini') + len('Houdini') + 1
                platformVersion = productNameFull[start_index : ]

            elif 'V-Ray for Maya' in productNameFull:
                productName = 'V-Ray'
                platformName = 'Maya'
                start_index = productNameFull.find('Maya') + len('Maya') + 1
                end_index = productNameFull.find('for', start_index) -1
                platformVersion = productNameFull[start_index : end_index]

            elif 'V-Ray for MODO' in productNameFull:
                productName = 'V-Ray'
                platformName = 'Modo'


            elif 'V-Ray for SketchUp' in productNameFull:
                productName = 'V-Ray'
                platformName = 'SketchUp'

            elif 'V-Ray Standalone' in productNameFull:
                productName = 'V-Ray'
                platformName = 'Standalone'


            elif 'V-Ray Swarm' in productNameFull:
                productName = 'V-Ray'
                platformName = 'Swarm'

            elif 'V-Ray Application SDK' in productNameFull:
                productName = 'V-Ray'
                platformName = 'Application SDK'


            elif 'Pdplayer 64' in productNameFull:
                productName = 'PDPlayer'
                # platformName = 'Pdplayer'

            elif 'Chaos License Server' in productNameFull:
                productName = 'License Server'
                

            elif 'Chaos Cosmos Browser' in productNameFull:
                productName = 'Chaos Cosmos'

            elif 'Chaos Cloud Client' in productNameFull:
                productName = 'Chaos Cloud Client'
            
            
            return {'productName':productName ,'platformName':platformName, 'platformVersion':platformVersion}
        
 

        def uninstall(self,productName, platformName, platformVersion, silent_uninstall, App, uninstall_string = None): #"C:\Program Files\Chaos Group\V-Ray\3ds Max 2017\uninstall\installer.exe" -uninstall="C:\Program Files\Chaos Group\V-Ray\3ds Max 2017\uninstall\install.log" -uninstallApp="V-Ray for 3dsmax 2017 for x64"
            

            CG_Utilities.instance.killHostApp(productName=productName, platformName=platformName, platformVersion=platformVersion)

            #IF UNINSTALL STRING IS NOT SUBMITTED, GET IT.
            if uninstall_string == None:
                uninstall_string = self.getUninstallStringByProduct(productName=productName, platformName=platformName, platformVersion=platformVersion )

                #IF UNINSTALL STRING CANNOT BE FOUND, THE PRODUCT IS NOT INSTALLED, THERE IS NO NEED TO RUN UNINSTALLATION
                if uninstall_string == None:
                    logging.info('Uninstallatalation of previous version is not needed')
                    return
            

            split_1 = uninstall_string.find("-uninstallApp=")
            split_2 = uninstall_string.find("-log=")

            arg1 = uninstall_string[:split_1 - 1]
            arg2 = uninstall_string[split_1:split_2 - 1]
            arg3 = uninstall_string[split_2:]

            if silent_uninstall == True:
                arg4 = "-gui=0"
                
                #SUDO LOGIN
                print(subprocess.check_output('sudo -S echo success', shell=True, input=App.sudo_password))


                logging.info("Installation cmd: " + arg1 + " " + arg2 + " " + arg3 + " " + arg4)
                subprocess.call([arg1, arg2, arg3, arg4])
                #self.checkUnintallProcessRunning()

                #RETURN PRODUCT NAME TO PRINT MSG IN STATUS BAR THE UNINSTALLATION IS COMPLETED
                return uninstall_string[split_1 + len("-uninstallApp=") +1: -1] + ' Sucessfully uninstalled!'
                
            else:
                logging.info("Installation cmd: " + arg1 + " " + arg2 + " " + arg3)
                subprocess.call([arg1, arg2, arg3])


            #WAIT THE PRODUCT ROOT DIR TO BE REMOVED - THIS MEANS THE UNINSTALL PROCESS IS COMPLETED SUCCESSFULLY
            # if silent_uninstall == True:
            #     parent_dir_1 = os.path.abspath(os.path.join(arg1, os.pardir))
            #     parent_dir_2 = os.path.abspath(os.path.join(parent_dir_1, os.pardir))
            #     # timer = QTimer()
            #     timer = 0
            #     while os.path.exists(parent_dir_2):
            #         time.sleep(1)
            #         # QTimer.singleShot(500, App ,lambda: print('yes'))
            #         timer +=1
            #         if timer > 5:
            #             error_msg = uninstall_string[split_2 + len("-uninstallApp=") +1: -1] + ' Uninstallation FAILED!'
            #             more_information = 'Try to uninstall product manually and clean up the leftover files!'
            #             CG_Utilities.instance.PyQTerrorMSG(error_msg=error_msg, more_information=more_information, App=App)
            #             return error_msg

                        
                
            #     #RETURN PRODUCT NAME TO PRINT MSG IN STATUS BAR THE UNINSTALLATION IS COMPLETED
            #     return uninstall_string[split_2 + len("-uninstallApp=") +1: -1] + ' Sucessfully uninstalled!'
        

        def getUninstallStringByProduct(self, productName='', platformName='', platformVersion=''):
            # print(len(self.product))
            
            for i in range(len(self.product)):
                if (productName in self.product[i]) and (platformName.lower() in self.product[i].lower()) and (platformVersion in self.product[i]):
                    logging.info("Uninstalling {0}".format(self.product[i]))
                    return self.uninstall_string[i]

        
        def getChaosProductVersion(self, productName ='', platformName='', platformVersion=''):

            if productName == 'V-Ray AppSDK':
                productName = 'V-Ray Application SDK'

            for i in range(len(self.product)):
                if (productName in self.product[i]) and (platformName.lower() in self.product[i].lower()) and (platformVersion in self.product[i]):
                    logging.info("Product Version: {0}".format(self.version[i]))

                    return self.version[i]
                    
            return 'Not Installed'

#CG_Uninstall_Instance = CG_Uninstall()
instance = CG_Uninstall()

# CG_Uninstall_Instance.uninstallByProduct(productName='V-Ray', platformName='Maya', platformVersion="2018")
