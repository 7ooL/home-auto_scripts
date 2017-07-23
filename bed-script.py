import time, ast
import myhouse
import os, sys, datetime
import logging
import ConfigParser

public = ConfigParser.RawConfigParser()
public.read('/home/host/home_auto_scripts/public.ini')

private = ConfigParser.RawConfigParser()
private.read('/home/host/home_auto_scripts/private.ini')

bedFile = "/home/host/Dropbox/IFTTT/bed/bed.txt" 

def saveSettings():
  with open(r'/home/host/home_auto_scripts/public.ini', 'wb') as configfile:
    public.write(configfile)
  with open(r'/home/host/home_auto_scripts/private.ini', 'wb') as configfile:
     private.write(configfile)

def main(argv):

  logging.info('bed-script.sh: Running bed Script')
  home = myhouse.Home()

  # check and see if the time now is greater than the morning routine,
  # meaning if it is the AM (after midnight) turn the lights off but 
  # dont stop the next evening from activating  
  now = datetime.datetime.now()
  st_morn = str(public.get('auto', 'morning_1_on_time')).split(':')
  if now >= now.replace(hour=int(st_morn[0]), minute=int(st_morn[1]), second=int(st_morn[2])):
    # the eveing will come back on during auto-runs default 
    public.set('settings','evening', 'off')
    public.set('settings','bed', 'on')


  public.set('auto','currentscene', 'null')

  # lock the door if necessary
  lockState = public.get('lock', 'status')

  if lockState == "Unlocked":
     home.kevo("lock")
     public.set('lock', 'status', "Locked")


  if public.getboolean('settings','movie'):
    logging.info('bed-script: Movie is on, turning off')
    public.set('settings','movie', 'off')
    settings = ast.literal_eval(private.get("Movie","settings"))
    logging.info('bed-script: resetting previous move settings')
    public.set("settings","morning", settings['morning'])
    public.set("settings","autorun", settings['autorun'])
    private.set('Movie','settings', 'Null' )
    logging.info('bed-script: '+str(settings))
 
  saveSettings()
  # define some variables
  bedroom = private.get('Groups','master_bedroom')
  mainfloor = private.get('Groups','main_floor')
  cdclock = private.get('Groups','count_down_clock')
  bedtimeScene = private.get('Scenes','bed_1')
  # turn on bedroom lights
  home.playScene( bedtimeScene , bedroom )
  # light 21 bloom
  # set all counters to red using group countDownClock id=4
  time.sleep(1)
  home.setCountdownLights( cdclock , "blue", False)
  time.sleep(2)
  # counter 1
  home.singleLightCountdown("16", 100)
  # counter 2
  home.singleLightCountdown("19", 100)
  # counter 3
  home.singleLightCountdown("20", 100)
  # turn off all lights
  home.groupLightsOff( mainfloor )
  # remove file that triggered script

  if os.path.isfile(bedFile):
    os.remove(bedFile)
    logging.debug('bed-script: removeing '+bedFile)

  logging.debug('bed-script.sh: END')

if __name__ == "__main__":
  main(sys.argv[1:])

