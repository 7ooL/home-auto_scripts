
import myhouse
import os
import sys, getopt
import logging
import ConfigParser
import datetime

public = ConfigParser.RawConfigParser()
public.read('/home/host/home_auto_scripts/public.ini')

private = ConfigParser.RawConfigParser()
private.read('/home/host/home_auto_scripts/private.ini')

arriveFile = "/home/host/Dropbox/IFTTT/arrive/arrive_home.txt"


def saveSettings():
  with open(r'/home/host/home_auto_scripts/public.ini', 'wb') as configfile:
    public.write(configfile)

def main(argv):

  logging.debug('arrive-script: START')

  run='True'
  # check and see if any one is home, if they are dont change anthing
  for section in public.sections():
    if section == "people_home":
      for person, value in public.items(section):
        if value == 'yes':
          run=False
          logging.debug('arrive-script: '+person+' already home')

  # set the person who triggered the script as home
  if os.path.isfile(arriveFile):
    with file(arriveFile) as f:
      s = f.readline().rstrip()
      logging.info('arrive-script: '+s)
      public.set("people_home", s,"yes")
      saveSettings()

  if run:
    logging.debug('arrive-script: Executing RUN()')
    home = myhouse.Home(); 
    public.set('settings','autorun', 'on')
    home.playScene(private.get('Scenes', 'home'),private.get('Groups','main_floor')) 
    public.set('auto', 'currentscene', 'home')
    saveSettings()
#    home.setHVACprofile(datetime.datetime.now(),'home')

  # remove file that triggered script
  if os.path.isfile(arriveFile):
    logging.debug('arrive-script: removeing '+arriveFile)
    os.remove(arriveFile)

  logging.debug('arrive-script: END')

if __name__ == "__main__":
  main(sys.argv[1:])
