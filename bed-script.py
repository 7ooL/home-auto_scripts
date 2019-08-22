import myhouse
import os, sys, ast, time, datetime
import logging, subprocess

def main(argv):

  now = datetime.datetime.now()
  home = myhouse.Home()

  bedFile = sys.argv[1] 

  logging.info('Running bed script')


  cs = []
  for z in (0,1,2):
    home.public.set('zone'+str(z),'currentscene', 'null')
    logging.debug('zone'+str(z)+' current scene set to: null')
    home.public.set('settings','zone'+str(z)+'_evening', 'false')
    home.public.set('settings','bedtime', 'true')
    home.saveSettings()


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

  # turn off all lights
  home.groupLightsOff(0)


  # turn off other lights
  if home.private.getboolean('Devices', 'decora'):
    for x in range(1,home.private.getint('Decora','switch_count')+1):
      x = str(x)
      home.decora(home.private.get('Decora', 'switch_'+str(x)), "OFF", "None")

  # turn off wemo devices
  if home.private.getboolean('Devices', 'wemo'):
    for x in range(1,home.private.getint('Wemo','device_count')+1):
      home.triggerWemoDeviceOff(x)

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
    main(sys.argv[1])

