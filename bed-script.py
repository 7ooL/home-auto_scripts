import myhouse
import os, sys, ast, time, datetime
import logging

def main(argv):

  now = datetime.datetime.now()
  home = myhouse.Home()

  bedFile = sys.argv[1] 

  logging.info('Running bed script')

  # turn on bedroom lights
  bedtimeScene = home.private.get('HueScenes','bed_1')
  bedroom = home.private.get('HueGroups','master_bedroom')
  home.playScene( bedtimeScene , bedroom )

  # check and see if the time now is greater than the morning routine,
  # meaning if it is the AM (after midnight) turn the lights off but 
  # dont stop the next evening from activating  
  st_morn = str(home.public.get('auto', 'morning_1_on_time')).split(':')
  if now >= now.replace(hour=int(st_morn[0]), minute=int(st_morn[1]), second=int(st_morn[2])):
    # the eveing will come back on during auto-runs default 
    home.public.set('settings','evening', 'false')
    home.public.set('settings','bedtime', 'true')

  home.public.set('auto','currentscene', 'null')

  # lock the door if necessary
  if home.private.getboolean('Devices', 'kevo'):
    lockState = home.public.get('lock', 'status')
    # if the house is unlocked, then lock the door
    if lockState == "Unlocked":
       home.kevo("lock")
       home.public.set('lock', 'status', "Locked")

  # if bed script was triggered and we are still in movie mode, make changes
  if home.public.getboolean('settings','movie'):
    logging.info('Movie is on, turning off')
    home.public.set('settings','movie', 'false')
    settings = ast.literal_eval(home.private.get("Movie","settings"))
    home.public.set("settings","morning", settings['morning'])
    home.public.set("settings","autorun", settings['autorun'])
    home.private.set('Movie','settings', 'Null' )
    logging.info('Restoring: '+str(settings))
 
  # save new settings
  home.saveSettings()

  time.sleep(1)

  # turn off wemo devices
  if home.private.getboolean('Devices', 'wemo'):
    for x in range(1,3):
      x = str(x)
      if home.private.getboolean('Wemo', 'wdevice'+x+'_active'):
        if home.public.get('wemo', 'wdevice'+x+'_status'):
          cmd = '/usr/local/bin/wemo switch "'+home.public.get('wemo', 'wdevice'+x+'_name')+'" off'
          proc = subprocess.Popen([cmd], stdout=subprocess.PIPE, shell=True )
          (out, err) = proc.communicate()
          logging.info(cmd)

  # set all counters to default
  if home.private.getboolean('HueBridge', 'count_down_lights_active'):
    home.setCountdownLights(  home.private.get('HueGroups','count_down_clock') , "default", False)
    time.sleep(2)
    # counter 1
    home.singleLightCountdown("16", 100)
    # counter 2
    home.singleLightCountdown("19", 100)
    # counter 3
    home.singleLightCountdown("20", 100)
  else:
    time.sleep(5)

  # turn off all lights
  home.groupLightsOff(0)

  # turn off other lights
  if home.private.getboolean('Devices', 'decora'):
    for x in range(1,6):
      x = str(x)
      home.decora(home.private.get('Decora', 'switch_'+str(x)), "OFF", "None")

  # remove file that triggered script
  if os.path.isfile(bedFile):
    os.remove(bedFile)
    logging.debug('removeing '+bedFile)

  end = datetime.datetime.now()
  logging.debug('finished '+str(end-now))

if __name__ == "__main__":
  if len(sys.argv) == 1: 
   logging.error("No input file provided")
  elif not os.path.isfile(sys.argv[1]):
    logging.error("Input file does not exist")
  else:
    with open(sys.argv[1]) as f:
      if not f.readline().rstrip():
        logging.error("Input file is empty")
      else:
        main(sys.argv[1])

