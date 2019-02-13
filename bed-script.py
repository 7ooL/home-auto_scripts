import myhouse
import os, sys, ast, time, datetime
import logging

def main(argv):

  now = datetime.datetime.now()
  home = myhouse.Home()

  bedFile = home.private.get('Path','ifttt')+"/bed/bed.txt" 

  logging.info('Running bed script')

  # turn on bedroom lights
  bedtimeScene = home.private.get('Scenes','bed_1')
  bedroom = home.private.get('Groups','master_bedroom')
  home.playScene( bedtimeScene , bedroom )

  # check and see if the time now is greater than the morning routine,
  # meaning if it is the AM (after midnight) turn the lights off but 
  # dont stop the next evening from activating  
  st_morn = str(home.public.get('auto', 'morning_1_on_time')).split(':')
  if now >= now.replace(hour=int(st_morn[0]), minute=int(st_morn[1]), second=int(st_morn[2])):
    # the eveing will come back on during auto-runs default 
    home.public.set('settings','evening', 'off')
    home.public.set('settings','bed', 'on')

  home.public.set('auto','currentscene', 'null')

  # lock the door if necessary
  lockState = home.public.get('lock', 'status')

  # if the house is unlocked, then lock the door
  if lockState == "Unlocked":
     home.kevo("lock")
     home.public.set('lock', 'status', "Locked")

  # if bed script was triggered and we are still in movie mode, make changes
  if home.public.getboolean('settings','movie'):
    logging.info('Movie is on, turning off')
    home.public.set('settings','movie', 'off')
    settings = ast.literal_eval(home.private.get("Movie","settings"))
    home.public.set("settings","morning", settings['morning'])
    home.public.set("settings","autorun", settings['autorun'])
    home.private.set('Movie','settings', 'Null' )
    logging.info('Restoring: '+str(settings))
 
  # save new settings
  home.saveSettings()
  # define some variables
  mainfloor = home.private.get('Groups','main_floor')
  cdclock = home.private.get('Groups','count_down_clock')
  time.sleep(1)

  # turn off lava lamp
  os.system('wemo switch "lava lamp" off')
  os.system('wemo switch "wemo im home" off')

  # set all counters to default 
  home.setCountdownLights( cdclock , "default", False)
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
    logging.debug('removeing '+bedFile)

  end = datetime.datetime.now()
  logging.debug('finished '+str(end-now))

if __name__ == "__main__":
  main(sys.argv[1:])

