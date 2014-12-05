ArraySetandGet
===========
   ------------------------------------------------------------------------
   Version 4.0.1
   
Summary
-------

This tool is designed to take a list of arrays and set the logging options to comply with what we expect to gather for MiTrend analysis.  Once the correct options have been set, the tool can be used to collect NAR, SPcollect, and Skew data (OE 32+) from the arrays for analysis.

<br> 
Install
-------
   If you are running this in python, it was written against Python 2.7.8 and will require the docopt package to be installed using:
   
      
      pip install docopt
    
   
   If you are running in Windows without Python, use the compiled executable XtremIOSnap.exe.  Visual C++ 2008 Redistributable package from MS (http://www.microsoft.com/en-us/download/details.aspx?id=29 ) is required for the compiled Windows executable.
<br>
Usage
-------   
      
      ArraySetandGet -h | --help
      ArraySetandGet (--csv=<array_list_csv>) [(LDAP_USER LDAP_PASS)] (--set | --get) [--c] [--ns] [--ni=<NAR_Interval>] [--nnf=<Num_NAR_to_retrieve>] [--l=<log_path>] [--debug]

Arguments
---------

      LDAP_USER               LDAP Username
      LDAP_PASS               LDAP Password

Options
-------

      -h --help               Show this help screen

      --csv=<array_list_csv>   CSV file containing a list of arrays and optionally
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


  
Running ArraySetandGet
----------- 
   
      ArraySetandGet <LDAP_UserID> <LDAP_Password> --csv=<file_containg_SP_addresses> --set --ns
      
![alt tag](https://github.com/evanbattle/imagefiles/blob/master/ArraySetandGet1.png)

![alt tag](https://github.com/evanbattle/imagefiles/blob/master/ArraySetandGet2.png)
   
      ArraySetandGet <LDAP_UserID> <LDAP_Password> --csv=<file_containg_SP_addresses> --get
      
![alt tag](https://github.com/evanbattle/imagefiles/blob/master/ArraySetandGet_get1.png)

![alt tag](https://github.com/evanbattle/imagefiles/blob/master/ArraySetandGet_get2.png)

Contributing
-----------
Please contribute in any way to the project.  Specifically, normalizing differnet image sizes, locations, and intance types would be easy adds to enhance the usefulness of the project.


Licensing
---------
Licensed under the Apache License, Version 2.0 (the “License”); you may not use this file except in compliance with the License. You may obtain a copy of the License at <http://www.apache.org/licenses/LICENSE-2.0>

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an “AS IS” BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

Support
-------
Please file bugs and issues at the Github issues page. For more general discussions you can contact the EMC Code team at <a href="https://groups.google.com/forum/#!forum/emccode-users">Google Groups</a>. The code and documentation are released with no warranties or SLAs and are intended to be supported through a community driven process.
