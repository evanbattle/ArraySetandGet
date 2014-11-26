#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      battle
#
# Created:     22/11/2014
# Copyright:   (c) battle 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import logging
import os
import subprocess
from modules.logger import Logger
from subprocess import check_output
from subprocess import CalledProcessError
from subprocess import Popen

class NaviCLI:
    def __init__(self,logfile,srcarray,srcuser,srcpasswd,srcscope):
        global navi_logger
        global array
        global user
        global password
        global scope
        navi_logger = Logger(
            logfile,
            logging.DEBUG,
            logging.INFO
            )
        navi_logger.debug(
            'Loading NaviCLI Module'
            )
        array = srcarray
        user = srcuser
        password = srcpasswd
        scope = srcscope

    def _GetSerialNumber(self):
        navi_logger.debug(
            'Starting def_GetSerialNumber module.'
            )
        cmd = 'getagent -serial'
        rawstatus,errcode = self._RunNaviCMD(cmd)
        midstatus = rawstatus.replace('Serial No:','')
        status = midstatus.replace('\n', ' ').replace('\r', '').replace(' ','')
        navi_logger.debug(
            'Exiting def_GetSerialNumber module.'
            )

        return status, errcode

    def _GetVersion(self):
        navi_logger.debug('Starting _GetVersion module.')
        cmd = 'getagent -ver'
        rawstatus,errcode = self._RunNaviCMD(cmd)
        midstatus = rawstatus.replace('Agent Rev:','')
        status = midstatus.replace('\n', ' ').replace('\r', '').replace(' ','')

        navi_logger.debug('Exiting def_GetSerialNumber module.')

        return status, errcode

    def _GetArrayconfigXML(self,path):
        navi_logger.debug('Starting _GetArrayconfigXML module.')
        cmd = 'arrayconfig -capture -output '+path+'\\arrayconfig.xml'
        status,errcode = self._RunNaviCMD(cmd)
        navi_logger.debug('Exiting _GetArrayconfigXML module.')
        return status

    def _GetFASTData(self,path):
        navi_logger.debug('Starting _GetFASTData module.')
        os.chdir(path)
        cmd = 'analyzer -archive -fastdata'
        status,errcode = self._RunNaviCMD(cmd)
        navi_logger.debug('Exiting _GetFASTData module.')
        return status

    def _GetSPCollectList(self,path):
        navi_logger.debug('Starting def_GetSPCollectList module.')
        cmd = 'managefiles -list'
        cmdStat,pipeerror = self._RunNaviCMD_Pipe(cmd)
        SPColLineArray = []
        navi_logger.debug('Stripping apart -managefiles -list output.')
        while True:
          line = cmdStat.stdout.readline()
          if line != '':
            if '_data.zip' in line:
                newline = line.replace('  ',' ')
                newline = newline.replace('  ',' ')
                newline = newline.replace('  ',' ')
                newline = newline.replace('  ',' ')
                newline = newline.replace('  ',' ')
                a,b,c,d,SPLine = newline.split(' ')
                SPLine = SPLine.strip('\n')
                SPColLineArray.append(SPLine)
          else:
            navi_logger.debug('Done reading -managefiles -list output.')
            break
        cmd2= 'managefiles -retrieve -path '+path+' -file '+SPColLineArray[-1]+' -o'
        status,errcode = self._RunNaviCMD(cmd2)
        navi_logger.debug('Exiting def_GetSPCollectList module.')
        return status

    def _GetNarInterval(self):
        navi_logger.debug('Starting _GetNarInterval module.')
        cmd = 'analyzer -get -narinterval'
##        rawstatus,errcode = def_RunNaviCMD(array,user,password,cmd,scope)
        rawstatus,errcode = self._RunNaviCMD(cmd)
        midstatus = rawstatus.replace('Archive Poll Interval (sec):','')
        status = midstatus.replace('\n', ' ').replace('\r', '').replace(' ','')
        navi_logger.debug('Exiting _GetNarInterval module.')
        return status, errcode

    def _GetSPCollectStatus(self):
        navi_logger.debug('Starting _GetSPCollectStatus module.')
        cmd = 'spcollect -info'
##        rawstatus,errcode = def_RunNaviCMD(array,user,password,cmd,scope)
        rawstatus,errcode = self._RunNaviCMD(cmd)
        midstatus = rawstatus.replace('AutoExecution:','')
        status = midstatus.replace('\n', ' ').replace('\r', '').replace(' ','')
        navi_logger.debug('Exiting _GetSPCollectStatus module.')
        return status,errcode

    def _SetSPcollectAE(self):
        navi_logger.debug('Starting _SetSPcollectAE module.')
        cmd = 'spcollect -set -auto on -o'
##        status,errcode = def_RunNaviCMD(array,user,password,cmd,scope)
        status,errcode = self._RunNaviCMD(cmd)
        navi_logger.debug('Exiting _SetSPcollectAE module.')

        return status,errcode

    def _GetRealtimeInterval(self):
        navi_logger.debug('Starting _GetRealtimeInterval module.')
        cmd = 'analyzer -get -rtinterval'
##        rawstatus,errcode = def_RunNaviCMD(array,user,password,cmd,scope)
        rawstatus,errcode = self._RunNaviCMD(cmd)
        if errcode != '0':
            status = rawstatus
        else:
            midstatus = rawstatus.replace('Real Time Poll Interval (sec):','')
            status = midstatus.replace('\n', ' ').replace('\r', '').replace(' ','')
        navi_logger.debug('Exiting _GetRealtimeInterval module.')
        return status,errcode

    def _GetPeriodicArchive(self):
        navi_logger.debug('Starting _GetPeriodicArchive')
        cmd = 'analyzer -get -periodicarchiving'
##        rawstatus,errcode = def_RunNaviCMD(array,user,password,cmd,scope)
        rawstatus,errcode = self._RunNaviCMD(cmd)
        midstatus = rawstatus.replace('Periodic Archiving:','')
        status = midstatus.replace('\n', ' ').replace('\r', '').replace(' ','')
        navi_logger.debug('Exiting _GetPeriodicArchive')
        return status,errcode

    def _GetLogPeriod(self):
        navi_logger.debug('Starting def_GetLogPeriod module.')
        cmd = 'analyzer -get -logperiod'
##        rawstatus,errcode = def_RunNaviCMD(array,user,password,cmd,scope)
        rawstatus,errcode = self._RunNaviCMD(cmd)
        midstatus = rawstatus.replace('Current Logging Period (day):','')
        status = midstatus.replace('\n', ' ').replace('\r', '').replace(' ','')
        navi_logger.debug('Exiting def_GetLogPeriod module.')
        return status,errcode

    def _GetAnalyzerStatus(self):
        navi_logger.debug('Starting def_GetAnalyzerStatus module.')
        cmd = 'analyzer -status'
##        status,errcode = def_RunNaviCMD(array,user,password,cmd,scope)
        status,errcode = self._RunNaviCMD(cmd)
        navi_logger.debug('Exiting def_GetAnalyzerStatus module.')
        return status

    def _StopLogging(self):
        navi_logger.debug('Starting def_StopLogging module.')
        cmd = 'analyzer -stop'
        navi_logger.info('Stopping Navisphere Analyzer Logging on ' + array + ': ')
##        status,errcode = def_RunNaviCMD(array,user,password,cmd,scope)
        status,errcode = self._RunNaviCMD(cmd)
        navi_logger.debug('Exiting def_StopLogging module.')
        return status, errcode

    def _SetNaviAnalyzerOptionsLicensed(self,interval,logperiod):
        navi_logger.debug('Starting def_SetNaviAnalyzerOptionsLicensed module.')
        if logperiod != 'nonstop':
            navi_logger.debug('Logperiod is being set to: ' + logperiod)
            cmd = 'analyzer -set -narinterval '+interval+' -logperiod '+logperiod+' -periodicarchiving 1'
        else:
            navi_logger.debug('Logperiod is being set to: ' + logperiod)
            cmd = 'analyzer -set -narinterval '+interval+' -'+logperiod+' -periodicarchiving 1'
        navi_logger.info('Setting Navisphere Analyzer Logging and Archiving Options on '+array+'..... ')
##        status,errcode = def_RunNaviCMD(array,user,password,cmd,scope)
        status,errcode = self._RunNaviCMD(cmd)
        navi_logger.debug('Exiting def_SetNaviAnalyzerOptionsLicensed module.')
        return status,errcode

    def _SetNaviAnalyzerOptions(self,interval,logperiod):
        navi_logger.debug('Starting def_SetNaviAnalyzerOptions module.')
        if logperiod != 'nonstop':
            navi_logger.debug('Logperiod is being set to: ' + logperiod)
            cmd = 'analyzer -set -narinterval ' + interval + ' -logperiod ' + logperiod
        else:
            navi_logger.debug('Logperiod is being set to: ' + logperiod)
            cmd = 'analyzer -set -narinterval ' + interval + ' -' + logperiod
        navi_logger.info('Setting Navisphere Analyzer Logging and Archiving Options on '+array+'..... ')
##        status,errcode = def_RunNaviCMD(array,user,password,cmd,scope)
        status,errcode = self._RunNaviCMD(cmd)
        navi_logger.debug('Exiting def_SetNaviAnalyzerOptions module.')
        return status,errcode

    def _StartLogging(self):
        navi_logger.debug('Starting def_StartLogging module')
        cmd = 'analyzer -start'
        navi_logger.info('Starting Navisphere Analyzer Logging on '+array+'..... ')
##        status,errcode = def_RunNaviCMD(array,user,password,cmd,scope)
        status,errcode = self._RunNaviCMD(cmd)
        navi_logger.debug('Exiting def_StartLogging module')
        return status,errcode

    def _GetNARList(self,Serial):
        navi_logger.debug('Starting def_GetNARList module.')
        cmd = 'analyzer -archive -list'
        cmdStat,pipeerror = self._RunNaviCMD_Pipe(cmd)
##        cmdStat,pipeerror = def_RunNaviCMD_Pipe(array,user,password,cmd,scope)
        NarLineArray = []
        navi_logger.debug('Stripping apart -archive -list output.')

        while True:
          line = cmdStat.stdout.readline()

          if line != '':

            if Serial in line:
                newline = line.replace('  ',' ')
                newline = newline.replace('  ',' ')
                newline = newline.replace('  ',' ')
                newline = newline.replace('  ',' ')
                newline = newline.replace('  ',' ')
                a,b,c,d,NARLine = newline.split(' ')
                NARLine = NARLine.strip('\n')
                NarLineArray.append(NARLine)

          else:
            navi_logger.debug('Done reading -archive -list output.')
            break

        navi_logger.debug('Exiting def_GetNARList module.')

        return NarLineArray

    def _GetNARList2(self,SerialNo,narlimit):
        navi_logger.debug('Staring def_GetNARList2 module.')
        navi_logger.info('Retrieving a List of NAR Files from '+SerialNo+' ....')
        narfilesarray = []
        narfilesarray = self._GetNARList(SerialNo)
        i=0
        l=0
        countdl = 0
        countcl = 0
        arraylen = len(narfilesarray)
        navi_logger.info('There are '+str(arraylen)+' NAR files on '+SerialNo+'.')
        narstring =''
        oldnar = ''
        narlimit = int(narlimit)

        if (narlimit+101)>arraylen:
            upperlimit = arraylen
        else:
            upperlimit = narlimit + 101

        y=-1

        if arraylen > narlimit:

            for i in range(0,narlimit):
                narstring = narstring + ' ' + narfilesarray[y]
                y = y-1
                countdl = countdl + 1
                i=i+1
            for i in range ((narlimit+1),(upperlimit)):
                oldnar = oldnar + ' ' + narfilesarray[y]
                y = y-1
                countcl = countcl + 1
                i=i+1
        else:

            while i < arraylen:
                narstring = narstring + ' ' + narfilesarray[y]
                y = y-1
                i=i+1

        navi_logger.debug('Exiting def_GetNARList2 module.')

        return countdl,narstring,oldnar,countcl

    def _GetNarFiles(self,filename,path):
        navi_logger.debug('Staring def_GetNarFiles module.')
        cmd = 'analyzer -archive -path ' + path +' -file ' +filename+' -o'
        status,errcode = self._RunNaviCMD(cmd)
        navi_logger.debug('Exiting def_GetNarFiles module.')
        return status

    def _CleanupOldNar(self,oldnar):
        navi_logger.debug('Staring def_CleanupOldNar module.')
        cmd = 'analyzer -archive -file ' +oldnar+' -delete -o'
        status,errcode = self._RunNaviCMD(cmd)
        navi_logger.debug('Exiting def_CleanupOldNar module.')
        return status


    def _RunNaviCMD(self,cmd):
        navi_logger.debug('Starting def_RunNaviCMD module.')
        navicmd = 'naviseccli -h '+array+' -User '+user+' -Password '+password+' -Scope '+scope+' '+cmd
        navi_logger.debug(navicmd)

        try:
            cmdStat = check_output(navicmd, shell = True,stderr=subprocess.STDOUT)
            errcode = '0'
        except CalledProcessError as e:
            cmdStat = e.output
            errcode = e.returncode

        navi_logger.debug(cmdStat)
        navi_logger.debug(errcode)

        navi_logger.debug('Exiting def_RunNaviCMD module.')

        return cmdStat, errcode

    def _RunNaviCMD_Pipe(self,cmd):
        navi_logger.debug('Starting def_RunNaviCMD_Pipe module.')
        navicmd = 'naviseccli -h '+array+' -User '+user+' -Password '+password+' -Scope '+scope+' '+cmd
        navi_logger.debug(navicmd)

        try:
            cmdStat = Popen(navicmd, shell = True,stdout=subprocess.PIPE)
            errcode = '0'
        except CalledProcessError as e:
            cmdStat = e.output
            errcode = e.returncode

        navi_logger.debug(cmdStat)
        navi_logger.debug(errcode)

        navi_logger.debug('Exiting def_RunNaviCMD_Pipe module.')

        return cmdStat, errcode
