EMC INTERNAL USE ONLY! NOT TO BE DISTRIBUTED EXTERNALLY

ReadMe:  ArraySetandGet.exe
Prerequisites:  Microsoft Visual C++ Redistributable 2008 (32-bit) http://www.microsoft.com/en-us/download/details.aspx?id=29

usage: ArraySetandGet.exe [-h] -f VAR_CSVFILE [-r] [-s] [-g] [-c] [-ns] 
					[-ni VAR_NIARG] [-nnf VAR_NUMNAR]
                          				[-ldapu VAR_LDAPUSER] [-ldapp VAR_LDAPPASS]
                          				[-l VAR_LOGFILE]
Version 3.1
Set Navisphere Analyzer options and retrieve NAR data for VNX OE and FLARE versions 30 and newer.
This is a multifunction tool to make NAR/NAZ management and collection across multiple arrays easier.  Its main functions are to set the NAR options in accordance with MiTrend guidance, to ensure the data is useful; retrieve NAR and SPCollect data from the prior 7 days (assuming ~5 hours of data per NAR file which equals 120 second interval); and to clean up old NAR data if desired.
The most common usage scenarios:
	 -Set the proper Navi Analyzer options using an LDAP user:
ArraySetandGet.exe -f c:\\EMC\\arraylist.csv -s -ldapu %Username% -ldapp %Password%
	-Ensure the Log Period is set to Non Stop logging (Logging will not stop after a certain period):
 ArraySetandGet.exe -f c:\\EMC\\arraylist.csv -s -ns -ldapu %Username% -ldapp %Password%
	 -Change the Log Period to a non-default interval:
 ArraySetandGet.exe -f c:\\EMC\\arraylist.csv -s -ni 300 -ldapu %Username% -ldapp %Password%
	-Get the NAR and SPcollect data:
 ArraySetandGet.exe -f c:\\EMC\\arraylist.csv -g -ldapu %Username% -ldapp %Password%
	-Get the NAR and SPcollect data and cleanup old NAR data:
ArraySetandGet.exe -f c:\\EMC\\arraylist.csv -g -c -ldapu %Username% -ldapp %Password%
        ------------------------------------------------------------------------
optional arguments:
  -h, --help            show this help message and exit
  -f VAR_CSVFILE, --file VAR_CSVFILE
Path to the CSV file containing the array IP/DNS name, username, password, and scope. If the -ldapu and -ldapp options are used, the program will disregard the user, password, and scope info in the csv file
  -r, --report          
** Not Implemented ** Queries the arrays and logs thecurrent Navisphere Analyzer settings
  -s, --set             
Set the proper Navisphere Analyzer properties and start logging on the array. The -ns or --nonstop option can be used with this option to change the current NAR collection period to collect continuously without stopping.
  -g, --get             
Get the last 7 days of NAR data and a current SPcollect.
  -c, --cleanup         
Deletes NAR data on the array older than 7 days. It actually deletes all but the newest 33 files, it assumes you are running at 120 second collection intervals. ****DO NOT USE IF YOUR COLLECTION INTERVALS ARE SHORTER THAN 120 SECONDS**** Due to limits in the Windows OS, only 100 files can be deleted at a time using this option. If you wish to remove all files at once, you will need to manually run the analyzer -archive -all -delete -o naviseccli command.
  -ns, --nonstop        
Overrides the current NAR logging period to be nonstop.
  -ni VAR_NIARG, --narinterval VAR_NIARG
Overrides the default NAR Interval setting of 120 seconds.
  -nnf VAR_NUMNAR, --numnarfiles VAR_NUMNAR
Overrides the default number of NAR files to retrieve which is 33.
  -ldapu VAR_LDAPUSER, --ldapuser VAR_LDAPUSER
LDAP Username, sets Scope = 2. This will use the LDAP credentials specified, rather than the credentials in the .CSV file. This option must be used with the -ldapp option.
  -ldapp VAR_LDAPPASS, --ldappasswd VAR_LDAPPASS
LDAP Password. Must be used with the -ldapu option. sets Scope = 2
  -l VAR_LOGFILE, --log VAR_LOGFILE
Path to the log file. by default it will be D:\Documents\ArrayDataScriptv2\test\ArraySetandGetv3.1\ArraySetandGet.log
      