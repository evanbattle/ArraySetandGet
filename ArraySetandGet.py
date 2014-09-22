#-------------------------------------------------------------------------------
# Name:         ArraySetandGet
# Purpose:      This is a multifunction tool to make NAR/NAZ management and
#               collection across multiple arrays easier.  Its main functions
#               are to set the NAR options in accordance with MiTrend guidance,
#               to ensure the data is useful; Retrieve NAR and SPCollect data
#               from the prior 7 days (assuming ~5 hours of data per NAR file
#               which equals 120 second interval); and to clean up old NAR data
#               if desired.
#
# Version:      3.1
#
# Author:       Evan R Battle
#               Sr. Systems Engineer
#               EMC Corporation
#               evan.battle@emc.com
#
# Created:     9/15/2014
# Copyright:   (c) Evan R. Battle 2014
# Licence:     This code is open and free to be modified.
#-------------------------------------------------------------------------------
##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
##  Load Modules
##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

import sys
import os
import logging
import inspect
import textwrap
import signal
import subprocess
from subprocess import check_output
from subprocess import CalledProcessError
from subprocess import Popen
import datetime
from datetime import date
import time
import argparse
import csv
import sys
import shutil

var_cwd =  os.getcwd()

##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
##   Parse CLI Arguments
##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

parser = argparse.ArgumentParser(
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description=textwrap.dedent('''\
        ------------------------------------------------------------------------
        EMC INTERNAL USE ONLY! NOT TO BE DISTRIBUTED EXTERNALLY
        \n
        Version 3.1
        \n
        Set Navisphere Analyzer options and retrieve NAR data for VNX OE and
        FLARE versions 30 and newer.
        \n
        This is a multifunction tool to make NAR/NAZ management and collection
        across multiple arrays easier.  Its main functions are to set the NAR
        options in accordance with MiTrend guidance, to ensure the data is useful;
        retrieve NAR and SPCollect data from the prior 7 days (assuming ~5 hours
        of data per NAR file which equals 120 second interval); and to clean up
        old NAR data if desired.
        \n
            The most common usage scenarios:

            -Set the proper Navi Analyzer options using an LDAP user:

                ArraySetandGet.exe -f c:\\EMC\\arraylist.csv -s -ldapu %Username% -ldapp %Password%

            -Ensure the Log Period is set to Non Stop logging (Logging will not stop after
             a certain period):

                ArraySetandGet.exe -f c:\\EMC\\arraylist.csv -s -ns -ldapu %Username% -ldapp %Password%

            -Change the Log Period to a non-default interval:

                ArraySetandGet.exe -f c:\\EMC\\arraylist.csv -s -ni 300 -ldapu %Username% -ldapp %Password%

            -Get the NAR and SPcollect data:

                ArraySetandGet.exe -f c:\\EMC\\arraylist.csv -g -ldapu %Username% -ldapp %Password%

            -Get the NAR and SPcollect data and cleanup old NAR data:

                ArraySetandGet.exe -f c:\\EMC\\arraylist.csv -g -c -ldapu %Username% -ldapp %Password%
        \n
        ------------------------------------------------------------------------
        '''),
        epilog='\nEMC INTERNAL USE ONLY! NOT TO BE DISTRIBUTED EXTERNALLY')
parser.add_argument(
    '-f','--file',
    dest='var_CSVFile',
    help='Path to the CSV file containing the array IP/DNS name, username, password, and scope.\
          If the -ldapu and -ldapp options are used, the program will disregard the user, password,\
           and scope info in the csv file',
    required=True
    )
parser.add_argument(
    '-r','--report',#<- I haven't decided what to do with this option yet, I'm open to suggestions
    action='store_true',
    default=False,
    dest='var_Report',
    help='** Not Implemented ** Queries the arrays and logs the current Navisphere Analyzer settings'
    )
parser.add_argument(
    '-s','--set',
    action='store_true',
    default=False,
    dest='var_Set',
    help='Set the proper Navisphere Analyzer properties and start logging on the array.  \
        The -ns or --nonstop option can be used with this option to change the current \
        NAR collection period to collect continuously without stopping.'
    )
parser.add_argument(
    '-g','--get',
    action='store_true',
    default=False,
    dest='var_Get',
    help='Get the last 7 days of NAR data and a current SPcollect'
    )
parser.add_argument(
    '-c','--cleanup',
    action='store_true',
    default=False,
    dest='var_Cleanup',
    help='Deletes NAR data on the array older than 7 days.  It actually deletes all \
        but the newest 33 files, it assumes you are running at 120 second collection intervals.  \
        ****DO NOT USE IF YOUR COLLECTION INTERVALS ARE SHORTER THAN 120 SECONDS****  Due to \
        limits in the Windows OS, only 100 files can be deleted at a time using this option.  If \
        you wish to remove all files at once, you will need to manually run the analyzer -archive \
        -all -delete -o naviseccli command.'
    )
parser.add_argument(
    '-ns','--nonstop',
    action='store_true',
    default=False,
    dest='var_NonStop',
    help='Overrides the current NAR logging period to be nonstop.'
    )
parser.add_argument(
    '-ni','--narinterval',
    dest='var_NIarg',
    help='Overrides the default NAR Interval setting of 120 seconds.'
    )
parser.add_argument(
    '-nnf','--numnarfiles',
    dest='var_NumNar',
    default=33,
    help='Overrides the default number of NAR files to retrieve which is 33.'
    )
parser.add_argument(
    '-ldapu','--ldapuser',
    dest='var_LDAPUser',
    help='LDAP Username, sets Scope = 2.  This will use the LDAP credentials specified, \
        rather than the credentials in the .CSV file.  This option must be used with the -ldapp option.'
    )
parser.add_argument(
    '-ldapp','--ldappasswd',
    dest='var_LDAPPass',
    help='LDAP Password.  Must be used with the -ldapu option. sets Scope = 2'
    )

parser.add_argument(
    '-l','--log',
    dest='var_Logfile',
    default= var_cwd + '\\ArraySetandGet.log',
    help='Path to the log file.  by default it will be '+var_cwd+'\\ArraySetandGet.log'
    )

if len(sys.argv)==1:
    parser.print_help()
    sys.exit(1)

args=parser.parse_args()


##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
##   MAIN FUNCTION
##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

def main():

    main_logger = def_FuncLogger(logging.DEBUG,logging.ERROR)
    var_hostmain, var_unamemain, var_passmain, var_scopemain = def_ReadCSV(args.var_CSVFile)

    if args.var_Report is True:
        main_logger.debug('Report argument is set')
        main_logger.info('The Report function is not implemented yet.')

    if args.var_Set is True:
        main_logger.debug('Set argument is set')
        def_ScriptSet(
            var_hostmain,
            var_unamemain,
            var_passmain,
            var_scopemain
            )

    if args.var_Get is True:
        main_logger.debug('Get argument is set')
        def_ScriptGet(
            var_hostmain,
            var_unamemain,
            var_passmain,
            var_scopemain
            )
    if args.var_Cleanup is True:
        main_logger.debug('Cleanup argument is set with the Get argument')
        if args.var_Get is False:
            main_logger.debug('Cleanup argument is set by itself')
            def_OnlyCleanupOldNar(
                var_hostmain,
                var_unamemain,
                var_passmain,
                var_scopemain
                )

    main_logger.debug('Exiting.')
    main_logger.info('Script Complete.')

    sys.exit(0)

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#   This section contains 'Utility Code', code that enables functions within the
#   program, but are not necesarilly critical to the logic (checking for files,
#   creating console and file log handles, skipping blank lines in output or
#   files.
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
##   def_FuncLogger
##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

def def_FuncLogger(file_level,console_level=None):

    function_name = inspect.stack()[1][3]
    logger = logging.getLogger(function_name)
    logger.setLevel(logging.DEBUG)

    if logger.handlers:
        logger.handlers = []

    if console_level != None:
        ch = logging.StreamHandler()
        ch.setLevel(console_level)
        ch_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        ch.setFormatter(ch_format)
        logger.addHandler(ch)

    fh = logging.FileHandler(args.var_Logfile.format(function_name))
    fh.setLevel(file_level)
    fh_format = logging.Formatter('%(asctime)s - %(lineno)d - %(levelname)8s - %(message)s')
    fh.setFormatter(fh_format)
    logger.addHandler(fh)

    return logger

##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
##   def_exit_gracefully
##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

def def_exit_gracefully(signum, frame):
    signal.signal(signal.SIGINT, original_sigint)

    try:
        if raw_input("\nDo you really want to quit? (y/n)> ").lower().startswith('y'):
            sys.exit(1)

    except KeyboardInterrupt:
        print("Ok, Exiting....")
        sys.exit(1)

    signal.signal(signal.SIGINT, def_exit_gracefully)

##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
##   def_skip_blank
##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

def def_skip_blank( rdr ):

    skipblank_logger = def_FuncLogger(logging.DEBUG,logging.ERROR)
    skipblank_logger.debug('Starting def_skip_blank module.')
    skipblank_logger.debug(rdr)

    for row in rdr:

        if len(row) == 0: continue

        if all(len(col)==0 for col in row): continue

        yield row

##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
##   def_FileCheck - Checks to see if the file exists
##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

def def_FileCheck(fn):

    filecheck_logger = def_FuncLogger(logging.DEBUG,logging.ERROR)
    filecheck_logger.debug('Starting def_FileCheck module.')
    filecheck_logger.debug(fn)

    try:
        open(fn,'r')
        filecheck_logger.debug('Exiting def_FileCheck module.')
        return 0
    except IOError:
        filecheck_logger.error('Error: ' + fn + ' not found.')
        print'Error: ' + fn + ' not found.'
        return 1

##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
## def_ReadCSV - reads the input csv
##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

def def_ReadCSV(csvfile):

    readcsv_logger = def_FuncLogger(logging.DEBUG,logging.ERROR)
    readcsv_logger.debug('Starting ReadCSV module.')
    readcsv_logger.debug(csvfile)

    arr_host = []
    arr_uname = []
    arr_passwd = []
    arr_scope = []

    result = def_FileCheck(csvfile)

    if result is 0:
        if args.var_LDAPUser != None:

            f = open(csvfile, 'r')
            r = csv.reader(f)
            arr_uname = None
            arr_passwd = None
            arr_scope = None
            for row in def_skip_blank(r):
                arr_host.append(row[0])
            readcsv_logger.debug('Exiting ReadCSV module.')
            return arr_host,arr_uname,arr_passwd,arr_scope
        else:

            f = open(csvfile, 'r')
            r = csv.reader(f)

            for row in def_skip_blank(r):
                arr_host.append(row[0])
                arr_uname.append(row[1])
                arr_passwd.append(row[2])
                arr_scope.append(row[3])

            readcsv_logger.debug('Exiting ReadCSV module.')
            return arr_host,arr_uname,arr_passwd,arr_scope
    else:
        exit(1)

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#   This section contains fost of the logic for the program.  Setting the Navi
#   Analyzer options, Getting NAR files and SPcollects, removing old NAR files.
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
##   def_ScriptSet
##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

def def_ScriptSet(array,user,passwd,scope):

    scriptset_logger = def_FuncLogger(logging.DEBUG,logging.INFO)
    scriptset_logger.debug('Starting def_ScriptSet module.')

    for x in xrange(len(array)):
        var_array = array[x]

        if args.var_LDAPUser != None:
            scriptset_logger.debug('Using LDAP user ID: ' +args.var_LDAPUser)
            var_user = args.var_LDAPUser
            var_passwd = args.var_LDAPPass
            var_scope = '2'
        else:
            scriptset_logger.debug('Using User ID from CSV file: ' + user[x])
            var_user=user[x]
            var_passwd = passwd[x]
            var_scope = scope[x]

        bol_Analyzer = True
        mod = 0
        scriptset_logger.info('************************************************')
        scriptset_logger.info('Getting Current Settings for '+var_array+' :')
        SerialNo,SNerrcode = def_GetSerialNumber(var_array,var_user,var_passwd,var_scope)

        if SNerrcode != '0':
            scriptset_logger.info(SerialNo)
        else:
            scriptset_logger.info('Serial Number:\t'+SerialNo)
            NARInterval,NIerrcode = def_GetNarInterval(var_array,var_user,var_passwd,var_scope)
            SPcollectstat,SPstaterrcode = def_GetSPCollectStatus(var_array,var_user,var_passwd,var_scope)
            scriptset_logger.info('SPCollect AutoExecution:\t'+SPcollectstat)

            if SPcollectstat != 'Enabled':
                SPcollectAEstat,SPcollectAEerrcode = def_SetSPcollectAE(var_array,var_user,var_passwd,var_scope)
                scriptset_logger.info('Enabling SPCollect AutoExecution....')


            scriptset_logger.info('Archive Interval:\t'+NARInterval)
            RTInterval,RTerrcode = def_GetRealtimeInterval(var_array,var_user,var_passwd,var_scope)

            if RTerrcode != '0':
                bol_Analyzer = False
                scriptset_logger.info('**** Analyzer is not installed ****')
            else:
                scriptset_logger.info('Real Time Interval:\t'+RTInterval)

            LogDays,LDerrcode = def_GetLogPeriod(var_array,var_user,var_passwd,var_scope)
            scriptset_logger.info('Current Logging Period:\t'+LogDays)


            if bol_Analyzer is False:
                scriptset_logger.info('**** Skipping Periodic Archive Setting, Analyzer is not installed ****')
            else:
                PeriodicArchive,PAerrcode = def_GetPeriodicArchive(var_array,var_user,var_passwd,var_scope)
                scriptset_logger.info('Periodic Archiving:\t'+PeriodicArchive)

            if args.var_NIarg != None:
                NARInterval = args.var_NIarg
                scriptset_logger.info('****Modifying the Archive Poll interval to:\t' + NARInterval)
                mod = mod + 1
            elif NARInterval != '120':
                NARInterval = '120'
                scriptset_logger.info('****Modifying the Archive Poll interval to:\t' + NARInterval)
                mod = mod + 1
            else:
                scriptset_logger.info('NAR Polling Interval is correctly set to:\t' + NARInterval)

            if LogDays != 'nonstop':
                if args.var_NonStop is True:
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

            NaviStat = def_GetAnalyzerStatus(var_array,var_user,var_passwd,var_scope)

            if 'Stopped' in NaviStat:
                scriptset_logger.debug('*****Analyzer Logging is NOT Running *****')
            else:
                StopLogStat,SLSerrcode = def_StopLogging(var_array,var_user,var_passwd,var_scope)
                time.sleep(10)

                if 'stopped' in StopLogStat:
                    scriptset_logger.info('*****Analyzer Logging is Already Stopped *****')

            if mod > 0:

                if bol_Analyzer is True:
                    SetLogsStat,SetLogserrcode = def_SetNaviAnalyzerOptionsLicensed(var_array,var_user,var_passwd,var_scope,NARInterval,LogDays)

                    if SetLogserrcode != '0':
                        scriptset_logger.debug('*****Error Setting Analyzer Logging and Archiving Options *****')

                else:
                    SetLogsStat,SetLogserrcode = def_SetNaviAnalyzerOptions(var_array,var_user,var_passwd,var_scope,NARInterval,LogDays)

                    if SetLogserrcode != '0':
                        scriptset_logger.debug('*****Error Setting Analyzer Logging and Archiving Options *****')

                StartLogStat,Starterrcode = def_StartLogging(var_array,var_user,var_passwd,var_scope)

                if Starterrcode != '0':
                    time.sleep(5)
                    scriptset_logger.debug('*****Error Starting Analyzer Logging *****')
                    NaviStat = def_GetAnalyzerStatus(var_array,var_user,var_passwd,var_scope)

                    if 'Stopped' in NaviStat:
                        scriptset_logger.debug('*****Analyzer Logging is NOT Running *****')
                        time.sleep(5)
                        StartLogStat,Starterrcode = def_StartLogging(var_array,var_user,var_passwd,var_scope)
                        if Starterrcode != '0':
                            scriptset_logger.info('*****Error Starting Analyzer Logging *****')

                NARInterval, NIerrcode = def_GetNarInterval(var_array,var_user,var_passwd,var_scope)

                if bol_Analyzer is True:
                    RTInterval,RTerrcode = def_GetRealtimeInterval(var_array,var_user,var_passwd,var_scope)
                    PeriodicArchive,PAerrcode = def_GetPeriodicArchive(var_array,var_user,var_passwd,var_scope)
                else:
                    RTInterval = ''
                    PeriodicArchive = ''

                LogDays, LDerrcode = def_GetLogPeriod(var_array,var_user,var_passwd,var_scope)
                scriptset_logger.info('\tSerial Number:\t' + SerialNo)
                scriptset_logger.info('\tNAR Interval:\t' + NARInterval)
                scriptset_logger.info('\tRealTime Interval:\t' + RTInterval)
                scriptset_logger.info('\tLog Days:\t' + LogDays)
                scriptset_logger.info('\tPeriodic Archive:\t' + PeriodicArchive)

            else:
                scriptset_logger.info('No Need to Change Analyzer Options. Skipping....')
                StartLogStat,Starterrcode = def_StartLogging(var_array,var_user,var_passwd,var_scope)

                if Starterrcode != '0':
                    time.sleep(5)
                    scriptset_logger.debug('*****Error Starting Analyzer Logging *****')
                    NaviStat = def_GetAnalyzerStatus(var_array,var_user,var_passwd,var_scope)

                    if 'Stopped' in NaviStat:
                        scriptset_logger.debug('*****Analyzer Logging is NOT Running *****')
                        time.sleep(5)
                        StartLogStat,Starterrcode = def_StartLogging(var_array,var_user,var_passwd,var_scope)

                        if Starterrcode != '0':
                            scriptset_logger.info('*****Error Starting Analyzer Logging *****')

                NaviStat = def_GetAnalyzerStatus(var_array,var_user,var_passwd,var_scope) #<-instance #2

                if 'Stopped' in NaviStat:
                    scriptset_logger.debug('*****Analyzer Logging is NOT Running *****')
                    StartLogStat,Starterrcode = def_StartLogging(var_array,var_user,var_passwd,var_scope)

                    if Starterrcode != '0':
                        scriptset_logger.info('*****Error Starting Analyzer Logging *****')
                    else:
                        NaviStat = def_GetAnalyzerStatus(var_array,var_user,var_passwd,var_scope)

            if 'Stopped' in NaviStat:
                scriptset_logger.debug('*****Analyzer Logging is NOT Running *****')
                StartLogStat,Starterrcode = def_StartLogging(var_array,var_user,var_passwd,var_scope)

                if Starterrcode != '0':
                    scriptset_logger.debug('*****Error Starting Analyzer Logging *****')
                    time.sleep(5)
                    NaviStat = def_GetAnalyzerStatus(var_array,var_user,var_passwd,var_scope)

                    if 'Stopped' in NaviStat:
                        scriptset_logger.debug('*****Analyzer Logging is NOT Running *****')
                        time.sleep(5)
                        StartLogStat,Starterrcode = def_StartLogging(var_array,var_user,var_passwd,var_scope)

                        if Starterrcode != '0':
                            scriptset_logger.info('*****Error Starting Analyzer Logging *****')

            NaviStat = def_GetAnalyzerStatus(var_array,var_user,var_passwd,var_scope)
            scriptset_logger.info(var_array + ' Analyzer Status = ' + NaviStat)
            if 'Stopped' in NaviStat:
                scriptset_logger.info('*****Analyzer Logging is NOT Running *****')

    scriptset_logger.debug('Exiting def_ScriptSet module.')
    scriptset_logger.info('Script is finished setting options.')

##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
##   def_ScriptGet
##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

def def_ScriptGet(array,user,passwd,scope):
    scriptget_logger = def_FuncLogger(logging.DEBUG,logging.INFO)
    scriptget_logger.debug('Starting def_ScriptGet module.')
    timenow =  datetime.datetime.now().hour + datetime.datetime.now().minute + datetime.datetime.now().second + datetime.datetime.now().microsecond

    for x in xrange(len(array)):
        var_array = array[x]

        if args.var_LDAPUser != None:
            scriptget_logger.debug('Using LDAP user ID: ' +args.var_LDAPUser)
            var_user = args.var_LDAPUser
            var_passwd = args.var_LDAPPass
            var_scope = '2'
        else:
            scriptget_logger.debug('Using User ID from CSV file: ' + user[x])
            var_user=user[x]
            var_passwd = passwd[x]
            var_scope = scope[x]

        scriptget_logger.info('************************************************')
        scriptget_logger.info('Getting Serial Number for ' + var_array + ' ....')
        SerialNo,SNerror = def_GetSerialNumber(var_array,var_user,var_passwd,var_scope)

        if SNerror != '0':
            scriptget_logger.info(SerialNo)
        else:
            outPath = ''.join([var_cwd,'\\',SerialNo])

            if not os.path.exists(outPath):
                scriptget_logger.info('Creating Local Directory ' + outPath + ' ....')
                os.makedirs(outPath)
            else:

                if os.path.isdir(outPath):
                    scriptget_logger.info('Found Existing Folder: ' + outPath)
                    outPath = outPath +'_'+str(date.today())+'_'+str(timenow)

                    if not os.path.exists(outPath):
                        scriptget_logger.info('Creating Local Directory ' + outPath + ' ....')
                        os.makedirs(outPath)

            scriptget_logger.info('Using ' + outPath + ' to save files for ' + SerialNo)
            scriptget_logger.info('Retrieving SPcollect for '+SerialNo +' ....')

            SPColStat=def_GetSPCollectList(var_array,var_user,var_passwd,var_scope,outPath)
            scriptget_logger.info(SPColStat)

            l,narstring,oldnar,ol = def_GetNARList2(SerialNo,var_array,var_user,var_passwd,var_scope)
            scriptget_logger.info('Retrieving ' + str(l) + ' NAR/NAZ files from ' + SerialNo + ' ....')
            stat = def_GetNarFiles(var_array,var_user,var_passwd,var_scope,narstring,outPath)
            scriptget_logger.info(stat)
            scriptget_logger.info('**** File Retrieval Complete for ' + SerialNo + ' ****')
            scriptget_logger.info('**** Creating zip of Data for ' + SerialNo + ' ****')
            shutil.make_archive(outPath, 'zip', outPath)
            scriptget_logger.info('**** Cleaning Up Local Directory ****')
            shutil.rmtree(outPath, ignore_errors=True)
            if args.var_Cleanup is True:
                scriptget_logger.info('**** Cleaning Up '+str(ol)+' NAR/NAZ files from '+SerialNo+' ****')
                cleanupstat = def_CleanupOldNar(var_array,var_user,var_passwd,var_scope,oldnar)
                scriptget_logger.debug(cleanupstat)

    scriptget_logger.debug('Exiting def_ScriptGet module.')
    scriptget_logger.debug('Script is finished retrieving files.')

##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
##   def_CleanupOldNar
##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

def def_CleanupOldNar(array,user,password,scope,oldnar):

    cleannarfiles_logger = def_FuncLogger(logging.DEBUG,logging.INFO)
    cleannarfiles_logger.debug('Staring def_CleanupOldNar module.')
    cmd = 'analyzer -archive -file ' +oldnar+' -delete -o'
    status,errcode = def_RunNaviCMD(array,user,password,cmd,scope)

    cleannarfiles_logger.debug('Exiting def_CleanupOldNar module.')

    return status

##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
##   def_OnlyCleanupOldNar
##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

def def_OnlyCleanupOldNar(array,user,password,scope):
    onlycleannarfiles_logger = def_FuncLogger(logging.DEBUG,logging.INFO)
    onlycleannarfiles_logger.debug('Staring def_OnlyCleanupOldNar module.')

    for x in xrange(len(array)):
        var_array = array[x]

        if args.var_LDAPUser != None:
            onlycleannarfiles_logger.debug('Using LDAP user ID: ' +args.var_LDAPUser)
            var_user = args.var_LDAPUser
            var_passwd = args.var_LDAPPass
            var_scope = '2'
        else:
            onlycleannarfiles_logger.debug('Using User ID from CSV file: ' + user[x])
            var_user=user[x]
            var_passwd = passwd[x]
            var_scope = scope[x]

        onlycleannarfiles_logger.info('************************************************')
        onlycleannarfiles_logger.info('Getting Serial Number for ' + var_array + ' ....')
        SerialNo,SNerror = def_GetSerialNumber(var_array,var_user,var_passwd,var_scope)

        if SNerror != '0':
            onlycleannarfiles_logger.info(SerialNo)
        else:
            l,narstring,oldnar,ol = def_GetNARList2(SerialNo,var_array,var_user,var_passwd,var_scope)
            onlycleannarfiles_logger.info('**** Cleaning Up '+str(ol)+' NAR/NAZ files, older than 7 days, from '+SerialNo+' ****')
            def_CleanupOldNar(var_array,var_user,var_passwd,var_scope,oldnar)

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#   This section generates the commands to get information from each array
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
##   def_GetSerialNumber
##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

def def_GetSerialNumber(array,user,password,scope):

    getserial_logger = def_FuncLogger(logging.DEBUG,logging.INFO)
    getserial_logger.debug('Starting def_GetSerialNumber module.')
    cmd = 'getagent -serial'
    rawstatus,errcode = def_RunNaviCMD(array,user,password,cmd,scope)
    midstatus = rawstatus.replace('Serial No:','')
    status = midstatus.replace('\n', ' ').replace('\r', '').replace(' ','')

    getserial_logger.debug('Exiting def_GetSerialNumber module.')

    return status, errcode

##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
##   def_GetNarInterval
##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

def def_GetNarInterval(array,user,password,scope):

    getnarinterval_logger = def_FuncLogger(logging.DEBUG,logging.INFO)
    getnarinterval_logger.debug('Starting def_GetNarInterval module.')
    cmd = 'analyzer -get -narinterval'
    rawstatus,errcode = def_RunNaviCMD(array,user,password,cmd,scope)
    midstatus = rawstatus.replace('Archive Poll Interval (sec):','')
    status = midstatus.replace('\n', ' ').replace('\r', '').replace(' ','')

    getnarinterval_logger.debug('Exiting def_GetNarInterval module.')

    return status, errcode

##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
##   def_GetRealtimeInterval
##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

def def_GetRealtimeInterval(array,user,password,scope):

    realtime_logger = def_FuncLogger(logging.DEBUG,logging.INFO)
    realtime_logger.debug('Starting def_GetRealtimeInterval module.')
    cmd = 'analyzer -get -rtinterval'
    rawstatus,errcode = def_RunNaviCMD(array,user,password,cmd,scope)

    if errcode != '0':
        status = rawstatus
    else:
        midstatus = rawstatus.replace('Real Time Poll Interval (sec):','')
        status = midstatus.replace('\n', ' ').replace('\r', '').replace(' ','')

    realtime_logger.debug('Exiting def_GetRealtimeInterval module.')

    return status,errcode

##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
##   def_GetLogPeriod
##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

def def_GetLogPeriod(array,user,password,scope):

    getlogperiod_logger = def_FuncLogger(logging.DEBUG,logging.INFO)
    getlogperiod_logger.debug('Starting def_GetLogPeriod module.')
    cmd = 'analyzer -get -logperiod'
    rawstatus,errcode = def_RunNaviCMD(array,user,password,cmd,scope)
    midstatus = rawstatus.replace('Current Logging Period (day):','')
    status = midstatus.replace('\n', ' ').replace('\r', '').replace(' ','')

    getlogperiod_logger.debug('Exiting def_GetLogPeriod module.')

    return status,errcode

##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
##   def_GetPeriodicArchive
##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

def def_GetPeriodicArchive(array,user,password,scope):

    periodicarch_logger = def_FuncLogger(logging.DEBUG,logging.INFO)
    periodicarch_logger.debug('Starting def_GetPeriodicArchive')
    cmd = 'analyzer -get -periodicarchiving'
    rawstatus,errcode = def_RunNaviCMD(array,user,password,cmd,scope)
    midstatus = rawstatus.replace('Periodic Archiving:','')
    status = midstatus.replace('\n', ' ').replace('\r', '').replace(' ','')

    periodicarch_logger.debug('Exiting def_GetPeriodicArchive')

    return status,errcode

##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
##   def_GetAnalyzerStatus
##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

def def_GetAnalyzerStatus(array,user,password,scope):

    analyzerstatus_logger = def_FuncLogger(logging.DEBUG,logging.INFO)
    analyzerstatus_logger.debug('Starting def_GetAnalyzerStatus module.')
    cmd = 'analyzer -status'
    status,errcode = def_RunNaviCMD(array,user,password,cmd,scope)

    analyzerstatus_logger.debug('Exiting def_GetAnalyzerStatus module.')

    return status

##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
##   def_GetSPcollectStatus
##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

def def_GetSPCollectStatus(array,user,password,scope):

    spcollectstatus_logger = def_FuncLogger(logging.DEBUG,logging.INFO)
    spcollectstatus_logger.debug('Starting def_GetSPCollectStatus module.')
    cmd = 'spcollect -info'
    rawstatus,errcode = def_RunNaviCMD(array,user,password,cmd,scope)
    midstatus = rawstatus.replace('AutoExecution:','')
    status = midstatus.replace('\n', ' ').replace('\r', '').replace(' ','')
    spcollectstatus_logger.debug('Exiting def_GetSPCollectStatus module.')

    return status,errcode

##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
##   def_GetNARList
##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

def def_GetNARList(Serial,array,user,password,scope):

    getnarlist_logger = def_FuncLogger(logging.DEBUG,logging.INFO)
    getnarlist_logger.debug('Starting def_GetNARList module.')
    cmd = 'analyzer -archive -list'
    cmdStat,pipeerror = def_RunNaviCMD_Pipe(array,user,password,cmd,scope)
    NarLineArray = []
    getnarlist_logger.debug('Stripping apart -archive -list output.')

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
        getnarlist_logger.debug('Done reading -archive -list output.')
        break

    getnarlist_logger.debug('Exiting def_GetNARList module.')

    return NarLineArray

##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
##  def_GetNARList2
##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

def def_GetNARList2(SerialNo,host,uname,upass,scope):

    getnarlist2_logger = def_FuncLogger(logging.DEBUG,logging.INFO)
    getnarlist2_logger.debug('Staring def_GetNARList2 module.')
    getnarlist2_logger.info('Retrieving a List of NAR Files from '+SerialNo+' ....')
    narfilesarray = []
    narfilesarray = def_GetNARList(SerialNo,host,uname,upass,scope)
    i=0
    l=0
    countdl = 0
    countcl = 0
    arraylen = len(narfilesarray)
    getnarlist2_logger.info('There are '+str(arraylen)+' NAR files on '+SerialNo+'.')
    narstring =''
    oldnar = ''
    narlimit = args.var_NumNar
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

    getnarlist2_logger.debug('Exiting def_GetNARList2 module.')

    return countdl,narstring,oldnar,countcl

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#   This section provides the functionality for starting and stopping Navi
#   Analyzer, and setting the options for Navi Analyzer.
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
##   def_SetSPcollectAE
##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

def def_SetSPcollectAE(array,user,password,scope):

    spaestatus_logger = def_FuncLogger(logging.DEBUG,logging.INFO)
    spaestatus_logger.debug('Starting def_SetSPcollectAE module.')
    cmd = 'spcollect -set -auto on -o'
    status,errcode = def_RunNaviCMD(array,user,password,cmd,scope)
    spaestatus_logger.debug('Exiting def_SetSPcollectAE module.')

    return status,errcode
##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
##   def_StopLogging
##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

def def_StopLogging(array,user,password,scope):

    stoplogging_logger = def_FuncLogger(logging.DEBUG,logging.INFO)
    stoplogging_logger.debug('Starting def_StopLogging module.')
    cmd = 'analyzer -stop'
    stoplogging_logger.info('Stopping Navisphere Analyzer Logging on ' + array + ': ')
    status,errcode = def_RunNaviCMD(array,user,password,cmd,scope)

    stoplogging_logger.debug('Exiting def_StopLogging module.')

    return status, errcode

##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
##   def_StartLogging
##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

def def_StartLogging(array,user,password,scope):

    startlog_logger = def_FuncLogger(logging.DEBUG,logging.INFO)
    startlog_logger.debug('Starting def_StartLogging module')
    cmd = 'analyzer -start'
    startlog_logger.info('Starting Navisphere Analyzer Logging on '+array+'..... ')
    status,errcode = def_RunNaviCMD(array,user,password,cmd,scope)

    startlog_logger.debug('Exiting def_StartLogging module')

    return status,errcode

##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
##   def_SetNaviAnalyzerOptionsLicensed
##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

def def_SetNaviAnalyzerOptionsLicensed(array,user,password,scope,interval,logperiod):

    nal_logger = def_FuncLogger(logging.DEBUG,logging.INFO)
    nal_logger.debug('Starting def_SetNaviAnalyzerOptionsLicensed module.')

    if logperiod != 'nonstop':
        nal_logger.debug('Logperiod is being set to: ' + logperiod)
        cmd = 'analyzer -set -narinterval '+interval+' -logperiod '+logperiod+' -periodicarchiving 1'
    else:
        nal_logger.debug('Logperiod is being set to: ' + logperiod)
        cmd = 'analyzer -set -narinterval '+interval+' -'+logperiod+' -periodicarchiving 1'

    nal_logger.info('Setting Navisphere Analyzer Logging and Archiving Options on '+array+'..... ')
    status,errcode = def_RunNaviCMD(array,user,password,cmd,scope)

    nal_logger.debug('Exiting def_SetNaviAnalyzerOptionsLicensed module.')

    return status,errcode

##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
##   def_SetNaviAnalyzerOptions
##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

def def_SetNaviAnalyzerOptions(array,user,password,scope,interval,logperiod):

    na_logger = def_FuncLogger(logging.DEBUG,logging.INFO)
    na_logger.debug('Starting def_SetNaviAnalyzerOptions module.')

    if logperiod != 'nonstop':
        na_logger.debug('Logperiod is being set to: ' + logperiod)
        cmd = 'analyzer -set -narinterval ' + interval + ' -logperiod ' + logperiod
    else:
        na_logger.debug('Logperiod is being set to: ' + logperiod)
        cmd = 'analyzer -set -narinterval ' + interval + ' -' + logperiod

    na_logger.info('Setting Navisphere Analyzer Logging and Archiving Options on '+array+'..... ')
    status,errcode = def_RunNaviCMD(array,user,password,cmd,scope)

    na_logger.debug('Exiting def_SetNaviAnalyzerOptions module.')

    return status,errcode

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#   This section provides the logic for retrieving the NAR/NAZ files and the
#   SPcollect files.
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
##   def_GetSPCollectXML
##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

def def_GetSPcollectXML(array,user,password,scope,path):

    getspcollect_logger = def_FuncLogger(logging.DEBUG,logging.INFO)
    getspcollect_logger.debug('Starting def_GetSPCollectXML module.')
    cmd = 'arrayconfig -capture -format xml -output '+path+'\\SP_Arrayconfig.xml'
    status,errcode = def_RunNaviCMD(array,user,password,cmd,scope)

    getspcollect_logger.debug('Exiting def_GetSPCollectXML module.')

    return status


##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
##   def_GetNarFiles
##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

def def_GetNarFiles(array,user,password,scope,filename,path):

    getnarfiles_logger = def_FuncLogger(logging.DEBUG,logging.INFO)
    getnarfiles_logger.debug('Staring def_GetNarFiles module.')
    cmd = 'analyzer -archive -path ' + path +' -file ' +filename+' -o'
    status,errcode = def_RunNaviCMD(array,user,password,cmd,scope)
    getnarfiles_logger.debug('Exiting def_GetNarFiles module.')

    return status


##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
##   def_GetSPCollectList
##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

def def_GetSPCollectList(array,user,password,scope,path):

    getspcollect_logger = def_FuncLogger(logging.DEBUG,logging.INFO)
    getspcollect_logger.debug('Starting def_GetSPCollectList module.')
    cmd = 'managefiles -list'
    cmdStat,pipeerror = def_RunNaviCMD_Pipe(array,user,password,cmd,scope)
    SPColLineArray = []
    getspcollect_logger.debug('Stripping apart -managefiles -list output.')

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
        getspcollect_logger.debug('Done reading -managefiles -list output.')
        break
    cmd2= 'managefiles -retrieve -path '+path+' -file '+SPColLineArray[-1]+' -o'
    status,errcode = def_RunNaviCMD(array,user,password,cmd2,scope)

    getspcollect_logger.debug('Exiting def_GetSPCollectList module.')

    return status

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#   This section executes all of the naviseccli commands
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
##   cmd_RunNaviCMD
##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

def def_RunNaviCMD(array,user,password,cmd,scope):

    RunNaviCMD_logger = def_FuncLogger(logging.DEBUG,logging.ERROR)
    RunNaviCMD_logger.debug('Starting def_RunNaviCMD module.')
    navicmd = 'naviseccli -h '+array+' -User '+user+' -Password '+password+' -Scope '+scope+' '+cmd
    RunNaviCMD_logger.debug(navicmd)

    try:
        cmdStat = check_output(navicmd, shell = True,stderr=subprocess.STDOUT)
        errcode = '0'
    except CalledProcessError as e:
        cmdStat = e.output
        errcode = e.returncode

    RunNaviCMD_logger.info(cmdStat)
    RunNaviCMD_logger.debug(errcode)

    RunNaviCMD_logger.debug('Exiting def_RunNaviCMD module.')

    return cmdStat, errcode

##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
##   cmd_RunNaviCMD_Pipe - Right now only used for the NAR listing so I can parse
##       the output in-line.
##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

def def_RunNaviCMD_Pipe(array,user,password,cmd,scope):

    RunNaviCMDPipe_logger = def_FuncLogger(logging.DEBUG,logging.ERROR)
    RunNaviCMDPipe_logger.debug('Starting def_RunNaviCMD_Pipe module.')
    navicmd = 'naviseccli -h '+array+' -User '+user+' -Password '+password+' -Scope '+scope+' '+cmd
    RunNaviCMDPipe_logger.debug(navicmd)

    try:
        cmdStat = Popen(navicmd, shell = True,stdout=subprocess.PIPE)
        errcode = '0'
    except CalledProcessError as e:
        cmdStat = e.output
        errcode = e.returncode

    RunNaviCMDPipe_logger.info(cmdStat)
    RunNaviCMDPipe_logger.debug(errcode)

    RunNaviCMDPipe_logger.debug('Exiting def_RunNaviCMD_Pipe module.')

    return cmdStat, errcode

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

if __name__ == '__main__':
    original_sigint = signal.getsignal(signal.SIGINT)
    signal.signal(signal.SIGINT, def_exit_gracefully)
    main()