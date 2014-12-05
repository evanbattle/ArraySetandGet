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
import csv
import logging
import sys
from modules.logger import Logger

class ReadCSV:

    def __init__(self,logfile,options):
        global csv_logger
        csvfile = options['--csv']
        csv_logger = Logger(logfile,logging.DEBUG,logging.INFO)
        csv_logger.debug('Loading ReadCSV Module')
        csv_logger.debug(csvfile)
        arr_host = []
        arr_uname = []
        arr_passwd = []
        arr_scope = []

        result = _FileCheck(csvfile)

        if result is 0:
            if options['LDAP_USER'] != None:
                f = open(csvfile, 'r')
                r = csv.reader(f)
                for row in _skip_blank(r):
                    arr_host.append(row[0])
                    arr_uname.append(options['LDAP_USER'])
                    arr_passwd.append(options['LDAP_PASS'])
                    arr_scope.append('2')
            else:
                try:
                    f = open(csvfile, 'r')
                    r = csv.reader(f)
                    for row in _skip_blank(r):
                        arr_host.append(row[0])
                        arr_uname.append(row[1])
                        arr_passwd.append(row[2])
                        arr_scope.append(row[3])
                except:
                    csv_logger.critical('There was an error reading the username and/or password info, is it specified in the csv?')
                    csv_logger.critical('exiting...')
                    sys.exit(1)
            self.uname = arr_uname
            self.passwd = arr_passwd
            self.host = arr_host
            self.scope = arr_scope
            csv_logger.debug('Exiting ReadCSV module.')
        else:
            sys.exit(1)

def _FileCheck(fn):
    csv_logger.debug('Starting _FileCheck module.')
    csv_logger.debug(fn)

    try:
        open(fn,'r')
        csv_logger.debug('Exiting def_FileCheck module.')
        return 0
    except IOError:
        csv_logger.error('Error: ' + fn + ' not found.')
        print'Error: ' + fn + ' not found.'
        return 1

def _skip_blank(rdr):
    csv_logger.debug('Starting _skip_blank module.')
    csv_logger.debug(rdr)

    for row in rdr:

        if len(row) == 0: continue

        if all(len(col)==0 for col in row): continue

        yield row
