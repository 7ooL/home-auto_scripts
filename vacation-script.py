import myhouse
import os
import sys, getopt
import logging
import ConfigParser

public = ConfigParser.RawConfigParser()
public.read('/home/host/home_auto_scripts/public.ini')


vacationFile = "/home/host/Dropbox/IFTTT/vacation/vacation.txt"
vacationFile2 = "/var/www/html/home-auto/vacation/vacation.txt"



def saveSettings():
  with open(r'/home/host/home_auto_scripts/public.ini', 'wb') as configfile:
    public.write(configfile)

def main(argv):

  logging.debug('vacation script started') 
  home = myhouse.Home(); 
  public.set('settings','autorun', 'on')

  if public.getboolean('settings', 'vacation'):
    logging.info('vacation mode toggled off') 
    public.set('settings','vacation', 'off')
    public.set('settings','morning', 'on')
  else:
    logging.info('vacation mode toggled on') 
    public.set('settings','vacation', 'on')
    public.set('settings','morning', 'off')

  saveSettings()

  if os.path.isfile(vacationFile):
    os.remove(vacationFile)
    logging.debug('vacation-script: removeing '+vacationFile)
  if os.path.isfile(vacationFile2):
    os.remove(vacationFile2)
    logging.debug('vacation-script: removeing '+vacationFile2)



  logging.debug('vacation script finished') 

if __name__ == "__main__":
  main(sys.argv[1:])
