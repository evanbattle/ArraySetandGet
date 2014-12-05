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
# Version:      4.0.1
#
# Author:       Evan R Battle
#               Sr. Systems Engineer
#               EMC Corporation
#               evan.battle@emc.com
#
# Created:     12/5/2014
# Copyright:   (c) Evan R. Battle 2014
# Licence:     This code is open and free to be modified.
#-------------------------------------------------------------------------------
##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
##  Load Modules
##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

import sys
import os
import logging
import signal
from modules.logger import Logger
from modules.readcsv import ReadCSV
from modules.get import ScriptGet
from modules.set import ScriptSet
from modules.cleanup import OnlyCleanupOldNar
from docopt import docopt

var_cwd =  os.getcwd()

##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
##   Parse CLI Arguments
##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

__doc__ = """
ArraySetAndGet

Version 4.0

Usage:
    ArraySetandGet -h | --help
    ArraySetandGet (--csv=<array_list_csv>) [(LDAP_USER LDAP_PASS)] (--set | --get) [--c] [--ns] [--ni=<NAR_Interval>] [--nnf=<Num_NAR_to_retrieve>] [--l=<log_path>] [--debug]

Arguments:
    LDAP_USER               LDAP Username
    LDAP_PASS               LDAP Password

Options:
    -h --help               Show this help screen

    --csv=<array_list_csv>  CSV file containing a list of arrays and optionally
                            username, password, and scope.  In the format:
                            IPAddress/Hostname, username, password, scope
                            If the LDAP_USER and LDAP_PASS options are specified,
                            the username, password, and scope entries in the csv
                            will be ignored.

    --set                   Set the proper Navisphere Analyzer properties and
                            start logging on the array.  The -ns option can be
                            used with this option to change the current NAR
                            collection period to collect continuously without
                            stopping.

    --get                   Get the last 7 days of NAR data and a current
                            SPcollect.

    --c                     Deletes NAR data on the array older than 7 days.  It
                            actually deletes all but the newest 33 files, it
                            assumes you are running at 120 second collection
                            intervals.  ****DO NOT USE IF YOUR COLLECTION INTERVALS
                            ARE SHORTER THAN 120 SECONDS****  Due to limits in
                            the Windows OS, only 100 files can be deleted at a
                            time using this option.  If you wish to remove all
                            files at once, you will need to manually run the
                            analyzer -archive -all -delete -o naviseccli command.

    --ns                    Overrides the current NAR logging period to be nonstop.

    --ni=<NAR_Interval>     [default: 120] Overrides the default NAR Interval
                            setting.

    --nnf=<Num_NAR_to_retrieve>    [default: 33] Overrides the default number of
                            NAR files to retrieve.

    --l=<log_path>          [default: """+var_cwd+"""\ArraySetandGet.log]

    --debug

"""

##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
##   MAIN FUNCTION
##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

def main():
    log = options['--l']
    if options['--debug'] == True:
        main_logger = Logger(
            log,
            logging.DEBUG,
            logging.INFO
            )
    else:
        main_logger = Logger(
            log,
            logging.INFO,
            logging.INFO
            )

    rd_csv = ReadCSV(
        log,
        options
        )

    if options['--set'] == True:
        main_logger.debug(
            'Set argument is set'
            )
        ScriptSet(
            log,
            rd_csv.host,
            rd_csv.uname,
            rd_csv.passwd,
            rd_csv.scope,
            options
            )
    if options['--get'] == True:
        main_logger.debug(
            'Get argument is set'
            )
        ScriptGet(
            log,
            rd_csv.host,
            rd_csv.uname,
            rd_csv.passwd,
            rd_csv.scope,
            options
            )

    if options['--c'] == True:
        main_logger.debug(
            'Cleanup argument is set with the Get argument'
            )
        if options['--get'] == False:
            main_logger.debug(
                'Cleanup argument is set by itself'
                )
            OnlyCleanupOldNar(
                log,
                rd_csv.host,
                rd_csv.uname,
                rd_csv.passwd,
                rd_csv.scope,
                options
                )
    main_logger.debug(
        'Exiting.'
        )
    main_logger.info(
        'Script Complete.'
        )
    sys.exit(0)

def _exit_gracefully(signum, frame):
    signal.signal(signal.SIGINT, original_sigint)

    try:
        if raw_input("\nDo you really want to quit? (y/n)> ").lower().startswith('y'):
            sys.exit(1)

    except KeyboardInterrupt:
        print("Ok, Exiting....")
        sys.exit(1)

    signal.signal(signal.SIGINT, _exit_gracefully)

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

if __name__ == '__main__':
    original_sigint = signal.getsignal(signal.SIGINT)
    signal.signal(signal.SIGINT, _exit_gracefully)
    options = docopt(
        __doc__,
        argv=None,
        help=True,
        version=None,
        options_first=False
        )
    main()