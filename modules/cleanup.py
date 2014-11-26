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
import signal
from modules.logger import Logger
from modules.navicli import NaviCLI

def OnlyCleanupOldNar(log,array,user,password,scope,options):
    onlycleannarfiles_logger = Logger(log,logging.DEBUG,logging.INFO)
    onlycleannarfiles_logger.debug('Staring def_OnlyCleanupOldNar module.')

    for x in xrange(len(array)):
        cli = NaviCLI(log,array[x],user[x],passwd[x],scope[x])
        var_array = array[x]
        var_user=user[x]
        var_passwd = passwd[x]
        var_scope = scope[x]

        onlycleannarfiles_logger.info('************************************************')
        onlycleannarfiles_logger.info('Getting Serial Number for ' + var_array + ' ....')
##        SerialNo,SNerror = def_GetSerialNumber(var_array,var_user,var_passwd,var_scope)
        SerialNo,SNerror = cli._GetSerialNumber()

        if SNerror != '0':
            onlycleannarfiles_logger.info(SerialNo)
        else:
##            l,narstring,oldnar,ol = def_GetNARList2(SerialNo,var_array,var_user,var_passwd,var_scope)
            l,narstring,oldnar,ol = cli._GetNARList2(SerialNo,options['--nnf'])
            onlycleannarfiles_logger.info('**** Cleaning Up '+str(ol)+' NAR/NAZ files, older than 7 days, from '+SerialNo+' ****')
##            def_CleanupOldNar(var_array,var_user,var_passwd,var_scope,oldnar)
            cli._CleanupOldNar(oldnar)

