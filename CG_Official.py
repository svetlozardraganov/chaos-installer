import requests
import json
import os
from operator import itemgetter #needed for sorting array of dictionary by key
import logging
import sys
import platform


from PyQt5.Qt import QRunnable, pyqtSlot, QObject, pyqtSignal

#import CG_Utilities

logging.basicConfig(level=logging.DEBUG)

        
class LogInChaosGroup():

    def __init__(self, username, password):

        self.url = 'download.chaosgroup.com'

        logging.debug('url = %s', self.url)

        self.session = requests.Session()
        logging.debug('session = %s', self.session)

        #CONNECT TO SSO TO GET X-CSRF-TOKEN VALUE
        self.response = self.session.get(self.url + "/session")
        # print(self.response.status_code)

        self.headers = self.response.headers
        self.cookies = self.response.cookies


        logging.debug('response.text = %s', self.response.text)
        logging.debug('headers = %s', self.headers)
        logging.debug('cookies = %s', self.cookies)
        logging.debug("cookies['session_id'] = %s", self.cookies['session_id'])


        logging.debug('---------------------HEADERS KEY/VALUE---------------------')
        for k, v in self.headers.items():
            logging.debug('key = %s, value = %s', k, v)

        logging.debug("headers['X-Csrf-Token']' = %s", self.headers['X-Csrf-Token'])

        #SUBMIT POST REQUEST TO LOGIN PAGE
        logging.info("Connecting to https://download.chaosgroup.com/")
        self.data = {'email': username, 'password': password, 'responseType': 'session'}
        self.response = self.session.post(self.url + "/account/login", headers={'X-Csrf-Token':self.headers['X-Csrf-Token']}, data=json.dumps(self.data))

        #CHECK IF LOGIN IS SUCCESFULL AND RAISE AND ERROR IF NOT
        # if self.response.status_code == 200:
        #     logging.debug('response = %s', self.response)
        # else:
        #     logging.critical('Cannot connect to Chaos Download page!')
        #     logging.critical('Check if you can open: https://download.chaosgroup.com/ in a web-browser.')
        #     CG_Utilities.instance.PyQTerrorMSG(error_msg='Cannot connect to Chaos Download page!',
        #                 more_information='Check if you can open: \n https://download.chaosgroup.com/ \n in a web-browser.')

        logging.debug('response.text = %s', self.response.text)
        logging.info('status-code={}'.format(self.response.status_code))


        #DOWNLOAD JSON FILE WHICH CONTAINS INFORMATION ABOUT ALL BUILDS AVAILABLE ON THE WEBSITE
        logging.debug('---------------------RESPONSE.TEXT.DOWNLOAD---------------------')
        self.response = self.session.get("download.chaosgroup.com")
        logging.info('response = %s', self.response)

    

#CONNECT to https://download.chaosgroup.com/ TO DOWNLOAD BUILDS LIST
class GetBuildsList():

    def __init__(self, username, password):
        
        log_in_chaosgroup = LogInChaosGroup(username=username, password=password)
        
        #WRITE OUTPUT FROM SERVER TO FILE
        # with open ('data.json', 'w') as f:
        #     json.dump(log_in_chaosgroup.response.text,f)


        self.data = log_in_chaosgroup.response.json()
        self.status_code = log_in_chaosgroup.response.status_code

        if self.status_code == 200:

            logging.debug('Sample Data = %s', self.data['Builds'][0])

            logging.debug("Convert JSON data to simple list for easier sorting")
            self.builds_list = []

            #ADD ITMS FROM JSON FILE TO A LIST BY FILTERING SOME ITEMS LIKE OS, LICENSE TYPE, HOST PLATFORM AND ETC
            for item in self.data['Builds']:
                

                #DETERMINE OS PLATFORM
                if platform.system() == 'Windows':
                    os_platform = 'Windows'
                elif platform.system() == 'Darwin':
                    os_platform = 'Mac OS'
                elif platform.system() == 'Linux':
                    os_platform = 'Linux'

                #FILTER BY OS:				
                if item['os']['name'] == os_platform:
                    #print(item)

                    #FILTER BY LICENSE TYPE
                    if item['licenseType']['name'] == 'adv' or item['licenseType']['name'] == 'free':
                        
                        #FILTER BY HOST PLATFORM
                        if item['platform']['name'] != ('Softimage') and item['platform']['name'] != ('Katana'):
                            
                            #REMOVE V-RAY BECHMARK CLI-VERSION
                            if item['product']['name'] == 'V-Ray Benchmark' and 'CLI' in item['name']:
                                continue
                            
                            #REMOVE CINEMA 4D .ZIP FILES
                            if item['platform']['name'] == 'Cinema 4D' and '.zip' in item['buildFile']:
                                continue

                            #REMOVE HOUDINI .ZIP FILES
                            if item['platform']['name'] == 'Houdini' and '.zip' in item['buildFile']:
                                continue

                            #REMOVE NUKE .ZIP FILES
                            if item['platform']['name'] == 'Nuke' and '.zip' in item['buildFile']:
                                continue
                            
                            #REMOVE V-RAY FOR MAYA .ZIP FILES FOR VERSION 4 AND ABOVE
                            if item['product']['name'] == 'V-Ray' and item['platform']['name'] == 'Maya' and \
                                int(item['version'][0]) >= 4 and '.zip' in item['buildFile']:
                                continue
                            
                            #REMOVE COSMOS BUILDS
                            if 'Cosmos' in item['product']['name']:
                                continue

                            #REMOVE PHOENIX ZIP BUILDS
                            if 'Phoenix' in item['product']['name'] and '.zip' in item['buildFile']:
                                continue
                            
                            #REMOVE ENTERPRICE LICENSE SERVER BUILDS
                            if 'Enterprise' in item['product']['name']:
                                continue
                            
                            #REMOVE APPSDK .ZIP NOGUI DOTNETCORE BUILDS
                            if 'AppSDK' in item['product']['name']:
                                if '.zip' in item['buildFile'] or 'nogui' in item['buildFile'] or 'dotnetcore' in item['buildFile']:
                                    continue
                            
                            #REMOVE STANDALONE .ZIP BUILDS.
                            if item['product']['name'] == 'V-Ray' and item['platform']['name'] == 'Standalone':
                                if '.zip' in item['buildFile']:
                                    continue

                            self.platformName = item['platform']['name']                         #3ds Max

                            try:
                                self.platformVersion = item['platformVersion']['name']
                            except:
                                try:
                                    self.platformVersion = item['platformVersions'][0]['name']
                                except:
                                    self.platformVersion = ''                                    #2019


                            self.productName = item['product']['name']                           # V-Ray
                            self.version = item['version']                                       #4.30.01
                            self.productNameExtended = item['name']                              #V-Ray 4.30.21 ADV
                            self.id = item['id']                                                 #13881
                            self.buildFile = item['buildFile']                                   #vray_adv_41203_houdini17.0.416_linux.tar.bz2
                            self.releaseDate = item['releaseDate'][:10]                          #2019-07-29


                            #RENAME CINEMA 4D S22 VERSION TO R22
                            if self.platformName == 'Cinema 4D' and self.platformVersion =='S22':
                                self.platformVersion = 'R22'


                            self.builds_list.append({'platformName':self.platformName, 'platformVersion': self.platformVersion,
                                            'productName': self.productName, 'version':self.version, 'productNameExtended':self.productNameExtended,
                                            'id': self.id, 'buildFile':self.buildFile, 'releaseDate':self.releaseDate})




            logging.debug("Sort build list")
            # self.builds_list = sorted(self.builds_list, key=itemgetter('version'), reverse=True)
            self.builds_list = sorted(self.builds_list, key=itemgetter('platformName', 'platformVersion', 'version'), reverse=True)


        #self.printBuildList()


    def printBuildList(self):
        # for item in self.builds_list:
        #     logging.debug('{:<15}{:<27}{:<18}{:<12}{:<40}{:<10}{:<55} {}'.format
        #             (item['platformName'], item['platformVersion'], item['productName'],
        #             item['version'], item['productNameExtended'], item['id'],
        #             item['buildFile'], item['releaseDate']))

        # for item in self.builds_list:
        #     if 'pdp' in item ['buildFile']:
        #         print(item['buildFile'])

        for item in self.builds_list:  #self.data['Builds']:
            if 'cinema' in item['buildFile']:
                print(item)
                # print('{:<15}{:<27}{:<18}{:<12}{:<40}{:<10}{:<55} {}'.format
                #     (item['platformName'], item['platformVersion'], item['productName'],
                #     item['version'], item['productNameExtended'], item['id'],
                #     item['buildFile'], item['releaseDate']))

#THIS CLASS PROVIDES THE SIGNALS NEEDED FOR THE DOWNLOADBUILD CLASS
class DownloadSignals(QObject):
    finished = pyqtSignal()
    progress_signal = pyqtSignal(int)
    total_mb_signal = pyqtSignal(int)
    downloaded_mb_signal = pyqtSignal(int)
    progress_data_signal = pyqtSignal(object)


    #https://www.thepythoncode.com/article/download-files-python
    #CG VARIABLE ACCEPTS INSTALLATION CLASS FROM CG_INSTALLER WHICH IS NEEDED IN ORDER TO UPDATE THE PROGRESS BAR

    
class DownloadBuild(QRunnable):
    # DOWNLOADING THE FILE: THE URL CONVETION IS: http://download.chaosgroup.com/api/v1/builds/your_build_id/serve -
    #     #  your_build should be replaced by the build_ID from the JSON file


    def __init__(self, build_id, build_name, download_path, username, password):
        super(DownloadBuild, self).__init__()
        self.build_id = build_id
        self.build_name = build_name
        self.download_path = download_path
        
        log_in_chaosgroup = LogInChaosGroup(username=username, password=password)
        self.session = log_in_chaosgroup.session

        self.filename = self.download_path + self.build_name
        self.signals = DownloadSignals()



    @pyqtSlot()
    def run(self):

        # IF FILE DOESN'T EXISTS PROCEED WITH THE DOWNLOAD
        if os.path.isfile(self.filename) == False:
            print("Start Downloading to:", self.filename)

            # response=session.get("download.chaosgroup.com" + str(data['Builds'][0]['id']) + "/serve")
            # download the body of response by chunk, not immediately
            self.url = "download.chaosgroup.com" + str(self.build_id) + "/serve"
            self.response = self.session.get(self.url, stream=True)

            with open(self.filename, 'wb') as f:

                # get the total file size
                self.total = self.response.headers.get('content-length')

                if self.total is None:
                    f.write(self.response.content)
                else:
                    self.downloaded = 0
                    self.total = int(self.total)
                    for data in self.response.iter_content(chunk_size=max(int(self.total / 1000), 1024 * 1024)):
                        self.downloaded += len(data)
                        self.download_mb = int(self.downloaded / (1024 * 1024))
                        self.total_mb = int(self.total / (1024 * 1024))
                        f.write(data)
                        self.done = int(100 * self.downloaded / self.total)

                        # sys.stdout.write('\r[{}{}]{}% {}MB/{}MB'.format('█' * self.done, '-' * (100 - self.done),
                        #                                                 self.done, self.download_mb, self.total_mb ))
                        # sys.stdout.flush()

                        #UPDATE PROGRESS BAR IN CG_INSTALLER
                        self.signals.progress_signal.emit(self.done)
                        self.signals.total_mb_signal.emit(self.total_mb)
                        self.signals.downloaded_mb_signal.emit(self.download_mb)
                        self.signals.progress_data_signal.emit({'downloaded_mb': self.download_mb, 'total_mb': self.total_mb, 'progress_done': self.done})


            sys.stdout.write('\n')

            logging.info("Download Complete")
        else:
            logging.info("File %s is already in the cache folder!" % self.build_name)

        self.signals.finished.emit()


# download_builds_list = DownloadBuildsList()

if __name__ == "__main__":
    pass
