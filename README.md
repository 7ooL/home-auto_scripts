# home-auto_scripts
Back end scripts for my home-auto project. This project automates as much as possible in my house. I don't own all the devices I once had so some devices like the Kevo still have code snippits that once worked but are no longer maintained.

You will need to customise the scripts to your own home!

## Configuation Files
The scripts run off two .ini files: ```public.ini``` and ``` private.ini```
The basic idea as stuff you don't want public should be in the private file and information you want pushed to a dashboard application should be in the public file.

see an older interface here: https://github.com/7ooL/OLD-home_auto_web

I even had an andriod application running on a rooted wink relay that read and manipulated the public.ini file.

```checkConfigs.py``` will help you build the ini files to get started. 

## Auto-Run
The main driver of the program is ```auto-run.py```

This program is run as a cron job every minute. I used to run it every 5 minutes but I prefer the quicker response times to changes in the house. 

### cron setup
```
* * * * * cd [your directory]/home_auto_scripts/ && python3 [your directory]/home_auto_scripts/auto_run.py >> [your directory]/home_auto_scripts/home-auto.log 2>&1

```

## Launching Helper Scripts
Scripts are primarly launched by creating file in a directory that is being monitored by incrontab to launch a python script.

My watch file is located inside of DropBox directories:
```
/Dropbox/IFTTT/
```
I can use IFTTT, Stringify, Alexa, or any other method to create a file. This will inturn lanuch a script.

### incrontab setup
```
[IFTTT watch dir]/arrive/ IN_MOVED_TO /usr/bin/python3 /home_auto_scripts/arrive-script.py $@$#
[IFTTT watch dir]/leave/ IN_MOVED_TO /usr/bin/python3 /home_auto_scripts/leave-script.py $@$#
[IFTTT watch dir]/movie/ IN_MOVED_TO /usr/bin/python3 /home_auto_scripts/movie-script.py $@$#
[IFTTT watch dir]/bed/ IN_MOVED_TO /usr/bin/python3 /home_auto_scripts/bed-script.py $@$#
[IFTTT watch dir]/relax/ IN_MOVED_TO /usr/bin/python3 /home_auto_scripts/relax-script.py $@$#
[IFTTT watch dir]/vacation/ IN_MOVED_TO /usr/bin/python3 /home_auto_scripts/vacation-script.py $@$#
[IFTTT watch dir]/scenes/ IN_MOVED_TO /usr/bin/python3 /home_auto_scripts/scenes-script.py $@$#
```
## Logging
the log file is ```home-auto.log```
You can switch between ```DEBUG``` and ```INFO``` messages in the ```logging.ini``` file

