from PyQt5.Qt import QRunnable, pyqtSlot, QObject, pyqtSignal

from ftplib import FTP
import re
import sys
import os
import json

import logging
logging.basicConfig(level=logging.DEBUG)

#import _macos_CG_Utilities as CG_Utilities


class Nightlies():

    #NIGHTLY BUILD DIRECTORY PARAMS
    productsNames = {'V-Ray': {}, 'Phoenix FD': {}}
    productsNames['V-Ray'] = {'3ds Max': {}, 'Maya': {}, 'SketchUp':{}, 'Rhino':{}, 'Houdini':{}, 'Cinema 4D': {},'Revit':{}, 'Nuke':{}, 'Modo':{}, 'Unreal':{}, 'Blender':{}, 'Standalone':{}, 'AppSDK':{}}

    productsNames['V-Ray']['3ds Max'] = {'6': '/vraymax6/', '5': '/vraymax5/', '4': '/vraymax4/'}
    productsNames['V-Ray']['Maya'] = {'6': '/merlin/', '5': '/corwin/', '4': '/oberon/'}
    productsNames['V-Ray']['SketchUp'] = {'6':'/vray6sketchup/', '5': '/vray5sketchup/', '4': '/vray4sketchup4/'}
    productsNames['V-Ray']['Rhino'] = { '6':'/vray6rhino/', '5': '/vray5rhino/', '4': '/vray4rhino4/'}
    productsNames['V-Ray']['Houdini'] = {'6':'/vray6houdini/', '5': '/vray5houdini/', '4': '/vray4houdini/'}
    productsNames['V-Ray']['Cinema 4D'] = {'6': '/vray6c4d/', '5': '/vray5c4d/', '3': '/vray3cinema4d/'}
    productsNames['V-Ray']['Revit'] = {'6':'/vray6revit/', '5': '/vray4revit5/', '4': '/vray4revit4/'}
    productsNames['V-Ray']['Nuke'] = {'6': '/vraynuke6/', '5': '/vraynuke5/', '4': '/vraynuke4/'}
    productsNames['V-Ray']['Modo'] = {'5': '/vraymodo5/', '4': '/vray4modo/'}
    productsNames['V-Ray']['Unreal'] = {'6':'/vray5unreal/','4': '/vrayunreal4/'}
    productsNames['V-Ray']['Blender'] = {'4': '/vray4blender/', '3': '/blender/'}
    productsNames['V-Ray']['Standalone'] = {'6': '/vraystd6/', '5': '/vraystd5/', '4': '/vraystd4/'}
    productsNames['V-Ray']['AppSDK'] = {'6': '/vrayappsdk6/', '5': '/vrayappsdk5/', '4': '/vrayappsdk4/'}


    productsNames['Chaos Vantage'] = {'Standalone':{}}
    productsNames['Chaos Vantage']['Standalone'] = {'1': '/vantage/'}


    productsNames['Phoenix FD'] = {'3ds Max': {}, 'Maya': {}}
    productsNames['Phoenix FD']['3ds Max'] = {'5': '/phoenix5max/', '4': '/phoenix4max/', '3': '/phoenix3max/'}
    productsNames['Phoenix FD']['Maya'] = {'5': '/phoenix5maya/', '4': '/phoenix4maya/', '3': '/phoenix3maya/'}

   

    def __init__(self):
        # log to the FTP server
    
        try:
            self.ftp = FTP('ftp.address.com', timeout=3)
            self.ftp.login('user', 'pass')
            self.ftp_status = True
            
        except:
            self.ftp_status = False
            logging.critical('Cannot connect to Chaos Nightlies Server!')
            logging.critical('Make sure you are in Chaos Network or use VPN connection to join it.')
            # CG_Utilities.instance.PyQTerrorMSG(error_msg = 'Cannot connect to Chaos Nightlies Server!', 
            #         more_information='Make sure you are in Chaos Network or use VPN connection to join it.')

        logging.info('re-connect to nightlies-ftp')
        
     
    #GET FTP CURRENT WORKING DIRECTORY
    def get_FTP_cwd(self):
        print("ftp.pwd()=", self.ftp.pwd())


    #DOWNLOAD FILE FROM FTP
    def download_file(self, download_path, build):

        filename = download_path + build
        with open( filename, 'wb' ) as file :
            self.ftp.retrbinary('RETR %s' % build, file.write)
        
        print('download completed!')


class DownloadSignals(QObject):
    finished = pyqtSignal()
    progress_signal = pyqtSignal(int)
    total_mb_signal = pyqtSignal(int)
    downloaded_mb_signal = pyqtSignal(int)
    progress_data_signal = pyqtSignal(object)

    #https://www.thepythoncode.com/article/download-files-python
    #CG VARIABLE ACCEPTS INSTALLATION CLASS FROM CG_INSTALLER WHICH IS NEEDED IN ORDER TO UPDATE THE PROGRESS BAR


class NightlyDownload(QRunnable):

    def __init__(self, download_path, build, ftp_path):
        super(NightlyDownload, self).__init__()

        self.download_path = download_path
        self.build = build
        self.ftp_path = ftp_path

        # log to the FTP server
        self.ftp = FTP('ftp.address.com')
        self.ftp.login('user', 'address')
        
        self.signals = DownloadSignals()

        # self.run()

    @pyqtSlot()
    def run(self):

        filename = self.download_path + self.build

        if os.path.exists(filename):
            logging.info('{} already exists in the cache-folder!'.format(self.build))
            
        else:
            logging.info('Stard downloading {}'.format(self.build))
            self.ftp.voidcmd('TYPE I')
            self.totalSize = self.ftp.size(self.ftp_path)
            self.downloaded = 0
            with open( filename, 'wb' ) as self.file :
                # self.ftp.retrbinary('RETR %s' % self.ftp_path, file.write)
                self.ftp.retrbinary('RETR %s' % self.ftp_path, blocksize=8192, callback=self.download_progress)
            

            logging.info('Downloading {} completed!'.format(self.build))

        self.signals.finished.emit()

    #http://postneo.com/stories/2003/01/01/beyondTheBasicPythonFtplibExample.html
    def download_progress(self, block):
        self.file.write(block)

        self.downloaded += len(block)
        self.download_mb = int(self.downloaded / (1024 * 1024))
        self.total_mb = int(self.totalSize / (1024 * 1024))
        self.done = int(100 * self.downloaded / self.totalSize)

        #sys.stdout.write('\r[{}{}]{}% {}MB/{}MB'.format('█' * self.done, '-' * (100 - self.done),
        #                self.done, self.download_mb, self.total_mb ))
        #sys.stdout.flush()

        self.signals.progress_data_signal.emit({'downloaded_mb': self.download_mb, 'total_mb': self.total_mb, 'progress_done': self.done})

        # print(NightlyDownload.sizeWritten, "= size written", self.totalSize, "= total size")
        # percentComplete = NightlyDownload.sizeWritten / self.totalSize
        # print (percentComplete, "percent complete")
        



if __name__ == "__main__":
    pass


