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
import sys
import os
import time
from modules.logger import Logger
from modules.navicli import NaviCLI

def ScriptSet(log,array,user,passwd,scope,options):

    scriptset_logger = Logger(log,logging.DEBUG,logging.INFO)
    scriptset_logger.debug('Starting ScriptSet module.')

    for x in xrange(len(array)):
        cli = NaviCLI(log,array[x],user[x],passwd[x],scope[x])
        var_array = array[x]
        var_user=user[x]
        var_passwd = passwd[x]
        var_scope = scope[x]
        bol_Analyzer = True
        mod = 0
        scriptset_logger.info('************************************************')
        scriptset_logger.info('Getting Current Settings for '+var_array+' :')
        SerialNo,SNerrcode = cli._GetSerialNumber()
        if SNerrcode != '0':
            scriptset_logger.critical(SerialNo)
        else:
            scriptset_logger.info('Serial Number:\t'+SerialNo)
            NARInterval,NIerrcode = cli._GetNarInterval()
            SPcollectstat,SPstaterrcode = cli._GetSPCollectStatus()
            scriptset_logger.info('SPCollect AutoExecution:\t'+SPcollectstat)
            if SPcollectstat != 'Enabled':
                SPcollectAEstat,SPcollectAEerrcode = cli._SetSPcollectAE()
                scriptset_logger.info('Enabling SPCollect AutoExecution....')
            scriptset_logger.info('Archive Interval:\t'+NARInterval)
            RTInterval,RTerrcode = cli._GetRealtimeInterval()
            if RTerrcode != '0':
                bol_Analyzer = False
                scriptset_logger.info('**** Analyzer is not installed ****')
            else:
                scriptset_logger.info('Real Time Interval:\t'+RTInterval)
            LogDays,LDerrcode = cli._GetLogPeriod()
            scriptset_logger.info('Current Logging Period:\t'+LogDays)
            if bol_Analyzer is False:
                scriptset_logger.info('**** Skipping Periodic Archive Setting, Analyzer is not installed ****')
            else:
                PeriodicArchive,PAerrcode = cli._GetPeriodicArchive()
                scriptset_logger.info('Periodic Archiving:\t'+PeriodicArchive)

            if options['--ni'] != None:
                if NARInterval == options['--ni']:
                    scriptset_logger.info('NAR Polling Interval is correctly set to:\t' + NARInterval)
                else:
                    NARInterval = options['--ni']
                    scriptset_logger.info('****Modifying the Archive Poll interval to:\t' + NARInterval)
                    mod = mod + 1
            if LogDays != 'nonstop':
                if options['--ns'] == True:
                    LogDays = 'nonstop'
                    scriptset_logger.info('****Logging Period is being modified to:\t' + LogDays)
                    mod = mod + 1
                elif LogDays != '7':
                    LogDays = '7'
                    scriptset_logger.info('****Logging Period is being modified to:\t' + LogDays)
                    mod = mod + 1
                else:
                    scriptset_logger.info('Logging Period is correctly set to:\t' + LogDays)
            else:
                scriptset_logger.info('Logging Period is correctly set to:\t' + LogDays)

            if bol_Analyzer is True:

                if PeriodicArchive != 'Yes':
                    PeriodicArchive = 'Yes'
                    scriptset_logger.info('****Periodic Archiving is Being Enabled')
                    mod = mod + 1
                else:
                    scriptset_logger.info('Periodic Archiving is correctly set to:\t' +PeriodicArchive)
            else:
                scriptset_logger.info('Skipping Periodic Archiving Modification - No Analyzer')

            NaviStat = cli._GetAnalyzerStatus()

            if mod > 0:
                if 'Stopped' in NaviStat:
                    scriptset_logger.debug('*****Analyzer Logging is NOT Running *****')
                else:
                    StopLogStat,SLSerrcode = cli._StopLogging()
                    time.sleep(10)

                    if 'stopped' in StopLogStat:
                        scriptset_logger.info('*****Analyzer Logging is Already Stopped *****')
                if bol_Analyzer is True:
                    SetLogsStat,SetLogserrcode = cli._SetNaviAnalyzerOptionsLicensed(NARInterval,LogDays)

                    if SetLogserrcode != '0':
                        scriptset_logger.debug('*****Error Setting Analyzer Logging and Archiving Options *****')

                else:
                    SetLogsStat,SetLogserrcode = cli._SetNaviAnalyzerOptions(NARInterval,LogDays)
                    if SetLogserrcode != '0':
                        scriptset_logger.debug('*****Error Setting Analyzer Logging and Archiving Options *****')
                StartLogStat,Starterrcode = cli._StartLogging()
                if Starterrcode != '0':
                    time.sleep(5)
                    scriptset_logger.debug('*****Error Starting Analyzer Logging *****')
                    NaviStat = cli._GetAnalyzerStatus()
                    if 'Stopped' in NaviStat:
                        scriptset_logger.debug('*****Analyzer Logging is NOT Running *****')
                        time.sleep(5)
                        StartLogStat,Starterrcode = cli._StartLogging()
                        if Starterrcode != '0':
                            scriptset_logger.info('*****Error Starting Analyzer Logging *****')
                NARInterval, NIerrcode = cli._GetNarInterval()

                if bol_Analyzer is True:
                    RTInterval,RTerrcode = cli._GetRealtimeInterval()
                    PeriodicArchive,PAerrcode = cli._GetPeriodicArchive()
                else:
                    RTInterval = ''
                    PeriodicArchive = ''
                LogDays, LDerrcode = cli._GetLogPeriod()
                scriptset_logger.info('\tSerial Number:\t' + SerialNo)
                scriptset_logger.info('\tNAR Interval:\t' + NARInterval)
                scriptset_logger.info('\tRealTime Interval:\t' + RTInterval)
                scriptset_logger.info('\tLog Days:\t' + LogDays)
                scriptset_logger.info('\tPeriodic Archive:\t' + PeriodicArchive)

            else:
                scriptset_logger.info('No Need to Change Analyzer Options. Skipping....')
                NaviStat = cli._GetAnalyzerStatus()

            if 'Stopped' in NaviStat:
                scriptset_logger.debug('*****Analyzer Logging is NOT Running *****')
                StartLogStat,Starterrcode = cli._StartLogging()
                if Starterrcode != '0':
                    scriptset_logger.debug('*****Error Starting Analyzer Logging *****')
                    time.sleep(5)
                    NaviStat = cli._GetAnalyzerStatus()
                    if 'Stopped' in NaviStat:
                        scriptset_logger.debug('*****Analyzer Logging is NOT Running *****')
                        time.sleep(5)
                        StartLogStat,Starterrcode = cli._StartLogging()
                        if Starterrcode != '0':
                            scriptset_logger.info('*****Error Starting Analyzer Logging *****')
                time.sleep(5)
                NaviStat = cli._GetAnalyzerStatus()
            scriptset_logger.info(var_array + ' Analyzer Status = ' + NaviStat)
            if 'Stopped' in NaviStat:
                scriptset_logger.info('*****Analyzer Logging is NOT Running *****')

    scriptset_logger.debug('Exiting def_ScriptSet module.')
    scriptset_logger.info('Script is finished setting options.')
