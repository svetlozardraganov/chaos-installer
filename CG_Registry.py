import winreg
import re
import logging
import os

logging.basicConfig(level=logging.INFO)

#Notes
    #IMPORTANT REGISTRY PLACES
    #Computer\HKEY_USERS\S-1-5-21-2633894342-2101855249-4104172794-1001\Software\Foundry\Modo13.2v1
    #Computer\HKEY_USERS\S-1-5-21-2712349333-3186455151-1702377714-1002\Software\Foundry\Modo13.0v1
    #Computer\HKEY_LOCAL_MACHINE\SOFTWARE\WOW6432Node\Foundry\Nuke12.0v1
    #Computer\HKEY_LOCAL_MACHINE\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\Nuke12.0v1
    #Computer\HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall
    #Computer\HKEY_LOCAL_MACHINE\SYSTEM\ControlSet001\Control\Session Manager\Environment
    #Computer\HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Session Manager\Environment
    #Computer\HKEY_USERS\S-1-5-21-2712349333-3186455151-1702377714-1001\Software\Microsoft\Windows\CurrentVersion\UFH\SHC
    #Computer\HKEY_USERS\S-1-5-21-2712349333-3186455151-1702377714-1002\Software\Microsoft\Windows\CurrentVersion\UFH\SHC
    #Computer\HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\UFH\SHC
    #Computer\HKEY_CURRENT_USER\Software\Foundry\Modo13.0v1

class Registry():

    def __init__(self):

        self.data = {'3ds Max': {}, 'Cinema 4D': {}, 'Maya': {}, 'chaosgroup': {}, 'SketchUp':{}, 'Rhino':{}, 'Nuke':{}, 'Modo':{}, 'Houdini':{}, 'Revit':{}}
        self.getUninstallRegistry()
        self.getUninstallRegistry_x64()
        # self.getRhinoRegistry()
        # print('>'*10,self.getAllRegistry('Modo'))
        # print('>'*10,self.getAllRegistry('Rhino'))


    def getUninstallRegistry(self):

        #CONNECT TO HKEY_LOCAL_MACHINE REGISTRY
        access_registry = winreg.ConnectRegistry(None,winreg.HKEY_LOCAL_MACHINE)

        #READ THE UNINSTALL REGISTRY/FOLDER
        uninstall_key = winreg.OpenKey(access_registry, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall", 0, (winreg.KEY_WOW64_64KEY + winreg.KEY_READ))


        #GET THE NUMBER OF FOLDERS/KEYS INSIDE UNINSTALL FOLDER/KEY
        number_of_uninstall_keys = winreg.QueryInfoKey(uninstall_key)[0]
        # print("number_of_uninstall_keys=%s" % number_of_uninstall_keys)

        #LOOP THROUGH UNINSTALL KEYS/FOLDERS
        for n in range(number_of_uninstall_keys):

            #GET THE NAME OF THE UNINSTALL KEY/FOLDER
            uninstall_key_name = winreg.EnumKey(uninstall_key, n)
            # print(uninstall_key_name)

            #OPEN THE REGISITRY SUBKEY/SUBFOLDER
            uninstall_sub_key = winreg.OpenKey(uninstall_key, uninstall_key_name)

            #GET THE NUMBER OF SUBKEYS/SUBFOLDERS
            number_of_uninstall_sub_key = winreg.QueryInfoKey(uninstall_sub_key)[1]
            # print("number_of_uninstall_sub_key=%s" % number_of_uninstall_sub_key)


            #LOOP THROUGH ALL SUBKEYS/SUBFOLDERS
            for j in range(number_of_uninstall_sub_key):
                uninstall_sub_key_name = winreg.EnumValue(uninstall_sub_key, j)
                # print("\t", uninstall_sub_key_name)

                if 'maya.exe' in str(uninstall_sub_key_name[1]) and 'bin' in str(uninstall_sub_key_name[1]) :
                    # print(uninstall_sub_key_name[1])
                    version = uninstall_sub_key_name[1].split("\\")[-3][4:]
                    install_location = uninstall_sub_key_name[1][:-12] + 'bin\\maya.exe'
                    self.data["Maya"][version] = install_location
                    # print(version, install_location)

                #This code captures 3ds Max 2021 and above
                if '3dsmax.exe' in str(uninstall_sub_key_name[1]):
                    version = uninstall_sub_key_name[1].split('\\')[-2][8:]
                    install_location = uninstall_sub_key_name[1][:-10] + '3dsmax.exe'
                    self.data["3ds Max"][version] = install_location
                    # print(version, install_location)


                if uninstall_sub_key_name[0] == 'InstallLocation':


                    if "cinema 4d" in uninstall_sub_key_name[1].lower() and 'corona' not in uninstall_sub_key_name[1].lower():
                        version = uninstall_sub_key_name[1][-3:]
                        install_location = uninstall_sub_key_name[1] + '\\Cinema 4D.exe'
                        self.data["Cinema 4D"][version] = install_location
                        # print(version,install_location)

                    #This code captures 3ds Max 2020 and bellow
                    if "3ds max" in uninstall_sub_key_name[1].lower() and "corona" not in uninstall_sub_key_name[1].lower():
                        version = uninstall_sub_key_name[1][-5:-1]
                        install_location = uninstall_sub_key_name[1] + '3dsmax.exe'
                        self.data["3ds Max"][version] = install_location
                        # print(version, install_location)

                    
                    #TESTED ONLY WITH REVIT 2021
                    if "revit" in uninstall_sub_key_name[1].lower():

                        search_pattern = '\\\\Revit\s\d\d\d\d\\\\'
                        regex = re.findall(search_pattern, str(uninstall_sub_key_name[1]))
                        #IF SEARCH_PATTER IS FOUND
                        if regex:
                            version = uninstall_sub_key_name[1][-5:-1]
                            install_location = uninstall_sub_key_name[1] + 'Revit.exe'
                            self.data["Revit"][version] = install_location
                            # print(version, install_location)


                    if "sketchup" in uninstall_sub_key_name[1].lower():
                        version = uninstall_sub_key_name[1][-5:-1]
                        install_location = uninstall_sub_key_name[1] + 'SketchUp.exe'
                        self.data["SketchUp"][version] = install_location
                        # print(version,install_location)

                    #This code doesn't get Nuke installations, only 11.3
                    if "nuke" in uninstall_sub_key_name[1].lower():
                        version = uninstall_sub_key_name[1][-7:-1]
                        index = version.find('v')
                        version_without_v1_v2 = version[:index]
                        install_location = uninstall_sub_key_name[1] + 'Nuke' + version_without_v1_v2 + '.exe'
                        self.data["Nuke"][version_without_v1_v2] = install_location
                        # print(version,install_location)
                        # print(uninstall_key_name)


                #Get Houdini versions / install locations
                if uninstall_sub_key_name[0] == 'DisplayIcon' and 'Houdini' in uninstall_sub_key_name[1] and "V-Ray" not in uninstall_sub_key_name[1]:
                    version = uninstall_sub_key_name[1].split('\\')[-2] #D:\Program Files\Side Effects Software\Houdini 18.0.391\Uninstall Houdini.exe
                    version = version.replace('Houdini ', '') #Houdini 18.0.391
                    split_index = uninstall_sub_key_name[1].rfind('\\') #D:\Program Files\Side Effects Software\Houdini 18.0.391\Uninstall Houdini.exe
                    install_location = uninstall_sub_key_name[1][:split_index] #D:\Program Files\Side Effects Software\Houdini 18.0.391\Uninstall Houdini.exe
                    install_location += '\\bin\\houdinifx.exe'
                    self.data["Houdini"][version] = install_location
                    # print(version, install_location)
                    
 

                # CHAOSGROUP
                if uninstall_sub_key_name[0] == 'Publisher' and uninstall_sub_key_name[1] == 'Chaos Software Ltd' or \
                        uninstall_sub_key_name[0] == 'Publisher' and uninstall_sub_key_name[1] == 'Chaos Group Inc.':

                    for i in range(number_of_uninstall_sub_key):
                        uninstall_sub_key_name = winreg.EnumValue(uninstall_sub_key, i)

                        if uninstall_sub_key_name[0] == 'DisplayName':
                            product_name = uninstall_sub_key_name[1]
                            
                        if uninstall_sub_key_name[0] == 'DisplayVersion':
                            version = uninstall_sub_key_name[1]

                        if uninstall_sub_key_name[0] == 'UninstallString':
                            uninstall_path = uninstall_sub_key_name[1]

                        if uninstall_sub_key_name[0] == 'DisplayIcon' or uninstall_sub_key_name[0] == 'InstallLocation':
                            install_location = uninstall_sub_key_name[1]

                    #SET PROPER VALUE FOR INSTALL LOCATION FOR VANTAGE, LICENSE SERVER, PDPLAYER
                    if product_name == 'Chaos Vantage':
                        install_location = install_location.replace('/uninstall/installer.exe', '\\vantage.exe')

                    elif product_name == 'Chaos License Server':
                        install_location = install_location.replace('/uninstall/installer.exe','\\vrol.exe')

                    elif 'Pdplayer 64' in product_name:
                        install_location = install_location + 'pdplayer64.exe'

                    self.data['chaosgroup'][product_name] = {'version': version,'install_location':install_location, 'uninstall_path': uninstall_path}
                    # print(product_name, version, uninstall_path, install_location)
                    # print(product_name, install_location)


                    #print(product_name, version, uninstall_path)
                    
    #SOME PLATFORMS LIKE NUKE ARE STORRING REGISTRY KEYS IN WOW6432NODE FOLDER
    #FIRST HALF OF THIS METHOD IS A COPY FROM THE ABOVE FUNCTION - IT SHOULD BE OPTIMIZED
    def getUninstallRegistry_x64(self):

        #CONNECT TO HKEY_LOCAL_MACHINE REGISTRY
        access_registry = winreg.ConnectRegistry(None,winreg.HKEY_LOCAL_MACHINE)

        #READ THE UNINSTALL REGISTRY/FOLDER
        uninstall_key = winreg.OpenKey(access_registry, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall", 0, (winreg.KEY_WOW64_64KEY + winreg.KEY_READ))


        #GET THE NUMBER OF FOLDERS/KEYS INSIDE UNINSTALL FOLDER/KEY
        number_of_uninstall_keys = winreg.QueryInfoKey(uninstall_key)[0]
        # print("number_of_uninstall_keys=%s" % number_of_uninstall_keys)

        #LOOP THROUGH UNINSTALL KEYS/FOLDERS
        for n in range(number_of_uninstall_keys):

            #GET THE NAME OF THE UNINSTALL KEY/FOLDER
            uninstall_key_name = winreg.EnumKey(uninstall_key, n)
            # print(uninstall_key_name)

            #OPEN THE REGISITRY SUBKEY/SUBFOLDER
            uninstall_sub_key = winreg.OpenKey(uninstall_key, uninstall_key_name)

            #GET THE NUMBER OF SUBKEYS/SUBFOLDERS
            number_of_uninstall_sub_key = winreg.QueryInfoKey(uninstall_sub_key)[1]
            # print("number_of_uninstall_sub_key=%s" % number_of_uninstall_sub_key)


            #LOOP THROUGH ALL SUBKEYS/SUBFOLDERS
            for j in range(number_of_uninstall_sub_key):
                uninstall_sub_key_name = winreg.EnumValue(uninstall_sub_key, j)
                # print("\t", uninstall_sub_key_name)

                if uninstall_sub_key_name[0] == 'DisplayIcon':

                    #FINDING NUKE VERSION AND INSTALL LOCATION
                    if "nuke" in uninstall_sub_key_name[1].lower():
                        version = uninstall_sub_key_name[1][-8:-4]
                        install_location = uninstall_sub_key_name[1]
                        self.data["Nuke"][version] = install_location
                        # print(version,install_location)
                        # print(uninstall_key_name)


    

    #RHINO DOESN'T STORE DATA IN UNINSTALL FOLDER
    def getRhinoRegistry(self):


        path = r"SOFTWARE\McNeel\Rhinoceros"

        def recursiveCall(path):

            # CONNECT TO HKEY_LOCAL_MACHINE REGISTRY
            access_registry = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)

            # READ THE UNINSTALL REGISTRY/FOLDER
            uninstall_key = winreg.OpenKey(access_registry, path, 0, (winreg.KEY_WOW64_64KEY + winreg.KEY_READ))

            # GET THE NUMBER OF FOLDERS/KEYS INSIDE UNINSTALL FOLDER/KEY
            number_of_uninstall_keys = winreg.QueryInfoKey(uninstall_key)[0]
            # print("number_of_uninstall_keys=%s" % number_of_uninstall_keys)

            # LOOP THROUGH UNINSTALL KEYS/FOLDERS
            for n in range(number_of_uninstall_keys):

                sub_keys_array = []
                # GET THE NAME OF THE UNINSTALL KEY/FOLDER
                name_of_uninstall_key = winreg.EnumKey(uninstall_key, n)
                # print(name_of_uninstall_key)

                if name_of_uninstall_key == 'Install':

                    # OPEN THE REGISITRY SUBKEY/SUBFOLDER
                    uninstall_sub_key = winreg.OpenKey(uninstall_key, name_of_uninstall_key)

                    # GET THE NUMBER OF SUBKEYS/SUBFOLDERS
                    number_of_uninstall_sub_key = winreg.QueryInfoKey(uninstall_sub_key)[1]
                    # print("number_of_uninstall_sub_key=%s" % number_of_uninstall_sub_key)

                    # LOOP THROUGH ALL SUBKEYS/SUBFOLDERS
                    for j in range(number_of_uninstall_sub_key):
                        name_of_uninstall_sub_key = winreg.EnumValue(uninstall_sub_key, j)
                        # print("\t", name_of_uninstall_sub_key)

                        #IF SUBKEY/FUBFOLD = INSTALLPATH
                        if name_of_uninstall_sub_key[0] == 'InstallPath':

                            #GET RHINO VERSION
                            if 'Rhino 5' in name_of_uninstall_sub_key[1] or 'Rhinoceros 5' in name_of_uninstall_sub_key[1]:
                                version = '5'
                            if 'Rhino 6' in name_of_uninstall_sub_key[1]:
                                version = '6'

                            #GET INSTALL LOCATION
                            install_location = name_of_uninstall_sub_key[1]

                            # print(version, install_location)
                            self.data["Rhino"][version] = install_location


                        # sub_keys_array.append(name_of_uninstall_sub_key)


                # print(path + '\\' + name_of_uninstall_key)
                recursiveCall(path + '\\' + name_of_uninstall_key)

        #CALL FUNCTION AGAIN TO WALK THROUGH ALL SUBFOLDERS/SUBKEYS
        recursiveCall(path)


    def getAllRegistry(self, platform_name):

        output = []

        # CONNECT TO REGISTRY
        reg_hkey_classes_root = winreg.ConnectRegistry(None, winreg.HKEY_CLASSES_ROOT)
        reg_hkey_current_user = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
        reg_hkey_local_machine = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
        reg_hkey_users = winreg.ConnectRegistry(None, winreg.HKEY_USERS)
        reg_hkey_current_config = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_CONFIG)


        def recursiveCall(registry, path, depth, find_sub_key, find_key, check_subkeys):

            # READ THE REGISTRY KEYS/FOLDER
            keys = winreg.OpenKey(registry, path, 0, (winreg.KEY_WOW64_64KEY + winreg.KEY_READ))

            ############uninstall_sub_key = winreg.OpenKey(uninstall_key, name_of_uninstall_key)

            # GET THE NUMBER FOLDERS/KEYS
            keys_num = winreg.QueryInfoKey(keys)[0]
            # print('\t'*depth, "(keys=%s" % keys_num, 'depth=%s)' % depth)

            #WALK THROUGH ALL THE REGISTRY KEYS AND LOOK FOR FIND_ME VARIABLE
            for i in range(keys_num):
                key_name = winreg.EnumKey(keys, i)
                # print('\t' * depth, key_name)

                #RUN THIS STATEMENT ONLY IF TEXT IS FOUND AND FUNCTION IS CALLED RECURSEVELY TO CHECK ALL KEYS/SUBKEYS
                if find_key == 'alreadyFound':
                    pass
                    #print('\t'*depth, key_name)

                #IF FIND_KEY IS FOUND IN KEYNAME ENABLE CHECK_SUBKEYS SUBMIT A NEW RECURSIVE CALL AND CHECK SUBKEYS
                if find_key in key_name:
                    # print(key_name)
                    # print(path)
                    recursiveCall(registry, path + key_name + '\\', depth, find_sub_key, find_key='alreadyFound', check_subkeys = True)

                #BY DEFAULT THE FUNCTION DOESN'T CHECK THE SUBKEYS/SUBFOLDERS. WHEN FIND_ME TEXT IS FOUND IN THE KEYNAME START LOOKING FOR SUBKEYS AS WELL
                if check_subkeys == True:
                    try:
                        sub_key = winreg.OpenKey(keys, key_name)
                        sub_keys_num = winreg.QueryInfoKey(sub_key)[1]
                        # print('\t\t' * depth, "sub_keys=%s" % sub_keys_num, 'depth=%s' % depth)

                        if find_key == 'alreadyFound':
                            pass
                            # print('\t\t' * depth, "sub_keys=%s" % sub_keys_num, 'depth=%s' % depth)


                        for j in range(sub_keys_num):
                            sub_key_name = winreg.EnumValue(sub_key, j)
                            # print('\t\t'*depth, sub_key_name)

                            if find_key == 'alreadyFound':
                                # print('\t\t' * depth, sub_key_name)
                                if find_sub_key == sub_key_name[0]:
                                    # pass
                                    # print(sub_key_name)
                                    #ADD HOST APP INSTALL PATH TO OUTPUT
                                    output.append(sub_key_name[1])

                    except Exception as e:
                        # print('\t'*depth, e)
                        pass

                #FOR EACH SUBKEY CALL THE FUNCTION RECURSEVELY IN ORDER TO GET SUBKEY SUBKEYS
                try:
                    if depth < 3:
                        # path += + key_name + '\\'
                        recursiveCall(registry, path + key_name + '\\', depth+1, find_sub_key, find_key, check_subkeys)
                except Exception as e:
                    # print('\t'*depth, e, '>>', key_name , '<<')
                    pass


        # recursiveCall(reg_hkey_classes_root, '', 0)
        # recursiveCall(reg_hkey_current_user, '', 0)

        #

        if platform_name == 'Modo':
            recursiveCall(reg_hkey_current_user, path='', depth=0, find_sub_key='installDir', find_key='Foundry', check_subkeys=False)

        elif platform_name == 'Rhino':
            recursiveCall(reg_hkey_local_machine, path='', depth=0, find_sub_key='InstallPath', find_key='McNeel', check_subkeys=False)
            # recursiveCall(reg_hkey_local_machine, path='', depth=0, find_sub_key='Version', find_key='McNeel', check_subkeys=False)
            

        elif platform_name == 'Unreal':
            recursiveCall(reg_hkey_local_machine, path='', depth=0, find_sub_key = 'InstalledDirectory', find_key='EpicGames', check_subkeys=False)
       
        # recursiveCall(registry=reg_hkey_users, path='', depth=0, find_key='McNeel', check_subkeys=False)
        # recursiveCall(reg_hkey_current_config, '', 0)

        return output


    def getCGproductVer(self, productName='', platformName='', platformVersion=''):

        version = 'Not Installed'

        # print(productName, platformName, platformVersion)

        if productName == 'V-Ray':

            # RENAME PLATFORM NAME SINCE V-RAY FOR 3DSMAX REGISTRY VALUE USES OTHER FORMAT
            if platformName == '3ds Max':
                platformName = '3dsmax'

            #REMOVE RHINO VERSION, IT'S UNNEEDED AND BREAKS THE LOGIC
            elif platformName == 'Rhino':
                platformVersion = ''


            for k, v in self.data['chaosgroup'].items():
                if productName in k and platformName in k and platformVersion in k:
                    version = v['version']

        elif productName == 'Phoenix FD':
            for k, v in self.data['chaosgroup'].items():
                if productName in k and platformName in k and platformVersion in k:
                    version = v['version']

        elif productName == 'Lavina' or productName == 'Chaos Vantage' or productName == 'License Server' or productName == 'PDPlayer' or \
                productName == 'V-Ray AppSDK' or productName == 'V-Ray Swarm':

            if productName == 'PDPlayer':
                productName = 'Pdplayer'
            elif productName == 'V-Ray AppSDK':
                productName = 'V-Ray Application SDK'

            for k, v in self.data['chaosgroup'].items():
                if productName in k:
                    version = v['version']

        return version


    def getHostAppPath(self, platformName='', platformVersion='',  productVersion = ''):
        

        if platformName == 'Cinema 4D':

            if productVersion[0] == '3':
                try:
                    platformPath = str(self.data[platformName])
                    platformPath = platformPath.replace('{', '')
                    platformPath = platformPath.replace('}', '')
                    platformPath = platformPath.replace("'", '')
                    platformPath = platformPath.replace('\\\\', '\\')
                except:
                    platformPath = 'Not Installed'
            
            else:
                try:
                    platformPath = self.data[platformName][platformVersion]
                except:
                    platformPath = 'Not Installed'

        elif platformName == 'Revit':
            try:
                platformPath = str(self.data[platformName])
                platformPath = platformPath.replace('{', '')
                platformPath = platformPath.replace('}', '')
                platformPath = platformPath.replace("'", '')
                platformPath = platformPath.replace('\\\\', '\\')
            except:
                platformPath = 'Not Installed'
        

        elif platformName == 'SketchUp':
            platformPath = ''

            for k,v in self.data[platformName].items():
                if platformVersion in k:
                    platformPath += k + ': ' + v + ' '

            if platformPath == '':
                platformPath = 'Not Installed'


        elif platformName == 'Houdini':
            try:
                platformVersion = platformVersion.replace(' (Qt5)','') #REMOVE (Qt5) TEXT FROM HOUDINI VERSION
                platformPath = self.data[platformName][platformVersion]
            except:
                platformPath = 'Not Installed'

        else:
            try:
                platformPath = self.data[platformName][platformVersion]
            except:
                platformPath = 'Not Installed'

        return platformPath


    def getEnvVarsFromReg(self):
        #https://stackoverflow.com/questions/3974038/loop-through-values-or-registry-key-winreg-python
        # #  key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, r"System\CurrentControlSet\Control\Session Manager\Environment")
        env_vars_dict = {}

        hKey = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, "System\\CurrentControlSet\\Control\\Session Manager\\Environment")

        try:
            count = 0
            while 1:
                name, value, type = winreg.EnumValue(hKey, count)
                print (name, value),
                count = count + 1
                env_vars_dict[name] = value
        except WindowsError as err:
            print(err)
            pass
        
        # print(type(env_vars_dict))
        # print(env_vars_dict)

        for key,value in env_vars_dict.items():
            print(key, value)

        return env_vars_dict

       
    def getEnvVarsFromOS(self):
        env = os.environ.copy()
        for item in env:
            print(item, env[item])


#Computer\HKEY_CURRENT_USER\Software\Foundry\Modo13.2v1
#Computer\HKEY_LOCAL_MACHINE\SOFTWARE\McNeel\Rhinoceros\5.0x64\Install
#Computer\HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Houdini 18.0.391
#Computer\HKEY_LOCAL_MACHINE\SOFTWARE\Side Effects Software\Houdini
#Computer\HKEY_LOCAL_MACHINE\SOFTWARE\Side Effects Software\Houdini 18.0.391

registry = Registry()
#print(registry.data)
# output = registry.getAllRegistry('Rhino')
# output = registry.getAllRegistry('Modo')

# output = registry.getAllRegistry('Unreal')
# print(output)

# registry.getAllRegistry()

# print(registry.data)

# print(registry.data["chaosgroup"]['Chaos Vantage'])
# print(registry.data["chaosgroup"])


# v = registry.getHostAppPath('3ds Max', '2020')
# print(v)



