from urllib.request import urlopen
# import os
import json
# import time
# import datetime
# import sys 
# import platform
# from subprocess import call
from operator import itemgetter #needed for sorting licenses
import logging
logging.basicConfig(level=logging.INFO)

#GLOBAL VARIABLES


class CG_License_Listener():

    global license_status
    global license_status_json

    global active_offline_sessions
    global active_offline_licenses
    global active_online_licenses

    def __init__(self, license_server_address, license_server_port):

        #TODO: there is no option for checking if license server is started or not!!!
        # self.server = r'http://localhost:30304/'
        # self.server = r'http://10.0.0.24:30304/'
        self.server = r'http://' + license_server_address + ':' + str(license_server_port) + r'/'

        try:
            self.license_status = urlopen(self.server + 'status')
            license_status_json = json.loads(self.license_status.read())
            self.license_server_version = license_status_json['version']
        except:
            logging.info('Local Chaos License Server is not started')
            self.license_status = 'offline'

        
    #GET OFFLINE LICENSES
    def getOfflineLicenses(self):
        self.license_status = urlopen(self.server + 'status')
        license_status_json = json.loads(self.license_status.read())
        active_offline_sessions = []
        active_offline_licenses = []
        try:
            #COLLECT OFFLINE SESSIONS
            for ses in license_status_json['offline']['sessions']:
                # print ses
                ses_dict = {}
                # print license_status_json['offline']['sessions'][ses]["productId"]

                ses_dict['Interface'] = license_status_json['offline']['sessions'][ses]["1"]
                ses_dict['Render'] = license_status_json['offline']['sessions'][ses]["2"]
                ses_dict['Product_ID'] = license_status_json['offline']['sessions'][ses]["productId"]
                ses_dict['IP'] = str(license_status_json['offline']['sessions'][ses]["ip"])


                #COLLECT ONLY SESSIONS WITH ENGAGED LICENSES
                if ses_dict['Interface'] !=0 or ses_dict['Render'] !=0:
                    active_offline_sessions.append(ses_dict)


            #COLLECT OFFLINE LICENSES - NEEDED TO GET PRODUCTLABEL CAUSE IT'S MISSING FROM SESSIONS
            for lic in license_status_json['offline']['licenses']:
                # print lic
                lic_dict = {}
                lic_dict["Product_ID"] = lic["productId"]
                lic_dict["Product_Label"] = str(lic["productLabel"])
                active_offline_licenses.append(lic_dict)

            # print "Active Offline Licenses"
            # for i in active_offline_licenses:   
            #     print i


            #MATCH PRODUCTID FROM SESSIONS TO LICENSES
            for ses in active_offline_sessions:
                # print ses["Product_ID"]

                for lic in active_offline_licenses:
                    if lic["Product_ID"] == ses["Product_ID"]:
                        # print lic["Product_Label"]
                        ses["Product_Label"] = lic["Product_Label"]
                        break


            #PRINTING ACTIVE OFFLINE SESSIONS
            # for i in active_offline_sessions:   
            #     # print i
            #     if i['Interface'] != 0:
                    
            #         print("OFFLINE|INTERFACE: %s %s" % (i['Interface'] , i['Product_Label']))
            #     elif i['Render'] != 0:
            #         print("OFFLINE|RENDER: %s %s" % (i['Render'] , i['Product_Label']))


            return active_offline_sessions
        except:
            pass


    def getOnlineLicenses(self):
        license_online = urlopen(self.server + 'sessions/online')
        online_json = json.loads(license_online.read())
        active_online_licenses = []
        

        if online_json !=[]:
            noLicense = True

            for product in online_json:
                ses_dict = {}

                if '1' in product['product']:
                    # print("(ONLINE|INTERFACE: %s %s" % (product['product']['1'] , product['product']['productLabel']))
                    ses_dict['Interface'] = product['product']['1']
                    ses_dict['Render'] = 0 #ADDING THIS VALUE CAUSE PRINT FUNCTION AT THE END NEEDS IT
                    ses_dict['Product_Label'] = product['product']['productLabel']
                    active_online_licenses.append(ses_dict)

                if '2' in product['product']:
                    # print("ONLINE|RENDER: %s %s" % (product['product']['2'] , product['product']['productLabel']))
                    ses_dict['Render'] = product['product']['2']
                    ses_dict['Interface'] = 0 #ADDING THIS VALUE CAUSE PRINT FUNCTION AT THE END NEEDS IT
                    ses_dict['Product_Label'] = product['product']['productLabel']
                    active_online_licenses.append(ses_dict)
                

        return active_online_licenses

    def getAvailableOnlineLicenses(self):
        status = urlopen(self.server + 'status')
        status_json = json.loads(status.read())
        licenses = []
        for i in status_json['online']['licenses']:
            item = {}

            item['productLabel'] = i['product']['productLabel']
            try:
                item['Interface'] = i['product']['1']
            except:
                item['Interface'] = '-'
            try:
                item['Render'] = i['product']['2']
            except:
                item['Render'] = '-'
            try:
                item['Network'] = i['product']['4']
            except:
                item['Network'] = '-'

            licenses.append(item)


        sorted_licenses = sorted(licenses, key=itemgetter('productLabel'))


        #CONVERT LIST OF DICTIONARIES TO REGULAR MULTILINE TEXT
        # output = ''
        # for i in licenses:
        #     output = output + i.get('productLabel')
        #
        #     if i.get('Interface', None) is not None:
        #         output = output + ' | ' + 'Interface ' + str(i['Interface'])
        #
        #     if i.get('Render', None) is not None:
        #         output = output  + ' | ' + 'Render ' + str(i['Render'])
        #
        #     if i.get('Network', None) is not None:
        #         output = output  + ' | ' + 'Network ' + str(i['Network'])
        #
        #     output = output + '\n'

        return sorted_licenses

    # print(getAvailableOnlineLicenses())

    def getLicenses(self):
        licenseList = []
        online = self.getOnlineLicenses()
        offline = self.getOfflineLicenses()

        if online is not None:
            for i in online:
                lic = {'ServerType':'ONLINE'}
                if i['Interface'] != 0:
                    lic['LicenseType'] = 'INTERFACE'
                    lic['EngagedLicenses'] = i['Interface']
                    lic['ProductType'] = i['Product_Label']
                elif i['Render'] != 0:
                    lic['LicenseType'] = 'RENDER'
                    lic['EngagedLicenses'] = i['Render']
                    lic['ProductType'] = i['Product_Label']
                licenseList.append(lic)

        if offline is not None:
            for i in offline:
                lic = {'ServerType': 'OFFLINE'}
                if i['Interface'] != 0:
                    lic['LicenseType'] = 'INTERFACE'
                    lic['EngagedLicenses'] = i['Interface']
                    lic['ProductType'] = i['Product_Label']
                elif i['Render'] != 0:
                    lic['LicenseType'] = 'RENDER'
                    lic['EngagedLicenses'] = i['Render']
                    lic['ProductType'] = i['Product_Label']
                licenseList.append(lic)

        #CONVERT LIST TO TEXT WITH SEPARATE LINES IN ORDER TO DISPLAY THEM IN PYQT-LABEL
        output = '\n'.join(item['ServerType'] + '|' + item['LicenseType'] + ' ' + str(item['EngagedLicenses']) + 'x ' + item['ProductType'] for item in licenseList)

        if output != '':
            return output
        else:
            return "NO LICENSES BEING ENGAGED"

    # print(getLicenses())

# instance = CG_License_Listener()
# print(instance.getLicenses())