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
from modules.logger import Logger
from modules.navicli import NaviCLI
import datetime
from datetime import date
import shutil

var_cwd =  os.getcwd()

def ScriptGet(log,array,user,passwd,scope,options):
    scriptget_logger = Logger(log,logging.DEBUG,logging.INFO)
    scriptget_logger.debug('Starting def_ScriptGet module.')
    timenow =  datetime.datetime.now().hour + datetime.datetime.now().minute + datetime.datetime.now().second + datetime.datetime.now().microsecond

    for x in xrange(len(array)):
        cli = NaviCLI(log,array[x],user[x],passwd[x],scope[x])
        var_array = array[x]
        var_user=user[x]
        var_passwd = passwd[x]
        var_scope = scope[x]
        bool_32plus = False

        scriptget_logger.info('************************************************')
        scriptget_logger.info('Getting Serial Number for ' + var_array + ' ....')
        SerialNo, SNerror = cli._GetSerialNumber()
        if SNerror != '0':
            scriptget_logger.critical(SerialNo)
        else:
            scriptget_logger.info('Getting OE Version for ' + var_array + ' ....')
            Version, Verror = cli._GetVersion()
            scriptget_logger.info('     Running OE Version ' + Version)
            if '7.32.' in Version:
                bool_32plus = True
            if '7.33.' in Version:
                bool_32plus = True
            outPath = ''.join([var_cwd,'\\',SerialNo])

            if not os.path.exists(outPath):
                scriptget_logger.info('Creating Local Directory ' + outPath + ' ....')
                os.makedirs(outPath)
                if bool_32plus == True:
                    skew_outpath = outPath+'_SkewData'
                    scriptget_logger.info('Creating Directory for Skew Data ' + skew_outpath + ' ....')
                    os.makedirs(skew_outpath)
            else:

                if os.path.isdir(outPath):
                    scriptget_logger.info('Found Existing Folder: ' + outPath)
                    outPath = outPath +'_'+str(date.today())+'_'+str(timenow)

                    if not os.path.exists(outPath):
                        scriptget_logger.info('Creating Local Directory ' + outPath + ' ....')
                        os.makedirs(outPath)
                        if bool_32plus == True:
                            skew_outpath = outPath+'_SkewData'
                            scriptget_logger.info('Creating Directory for Skew Data ' + skew_outpath + ' ....')
                            os.makedirs(skew_outpath)
            scriptget_logger.info('Using ' + outPath + ' to save files for ' + SerialNo)
            scriptget_logger.info('Retrieving SPcollect for '+SerialNo +' ....')

            SPColStat = cli._GetSPCollectList(outPath)
            scriptget_logger.debug(SPColStat)

            l,narstring,oldnar,ol = cli._GetNARList2(SerialNo,options['--nnf'])
            scriptget_logger.info('Retrieving ' + str(l) + ' NAR/NAZ files from ' + SerialNo + ' ....')
            stat = cli._GetNarFiles(narstring,outPath)
            scriptget_logger.info(stat)
            if bool_32plus == True:
                scriptget_logger.info('Retrieving skew files from ' + SerialNo + ' ....')
                stat = cli._GetArrayconfigXML(skew_outpath)
                scriptget_logger.debug(stat)
                stat = cli._GetFASTData(skew_outpath)
                scriptget_logger.debug(stat)
                os.chdir(var_cwd)
            scriptget_logger.info('**** File Retrieval Complete for ' + SerialNo + ' ****')
            scriptget_logger.info('**** Creating zip of Data for ' + SerialNo + ' ****')
            shutil.make_archive(outPath, 'zip', outPath)
            if bool_32plus == True:
                shutil.make_archive(skew_outpath, 'zip', skew_outpath)
            scriptget_logger.info('**** Cleaning Up Local Directory ****')
            shutil.rmtree(outPath, ignore_errors=True)
            if bool_32plus == True:
                shutil.rmtree(skew_outpath, ignore_errors=True)
            if options['--c'] == True:
                scriptget_logger.info('**** Cleaning Up '+str(ol)+' NAR/NAZ files from '+SerialNo+' ****')
                cleanupstat = cli._CleanupOldNar(oldnar)
                scriptget_logger.debug(cleanupstat)

    scriptget_logger.debug('Exiting def_ScriptGet module.')
    scriptget_logger.debug('Script is finished retrieving files.')