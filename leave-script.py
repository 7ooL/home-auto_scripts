import myhouse
import os, sys, datetime, time, subprocess
import logging

def main(argv):

  now = datetime.datetime.now()
  home = myhouse.Home()

  logging.debug('Running Leave Script')

  leaveFile = sys.argv[1]
  logging.debug("leaveFile: "+leaveFile)

  run='True'

  # set the person who triggered script as away
  # must be done first so that when we check for others being home it wont run
  if os.path.isfile(leaveFile):
    with open(leaveFile) as f:
      s = f.readline().rstrip()
      logging.info('Marking '+s+' as not home')
      home.public.set("people_home", s,"false")
      home.saveSettings()
      home.blinkGroup( home.private.get('HueGroups','main_floor') )

  # check and see if anyone is home, if they are dont run actions
  for section in home.public.sections():
    if section == "people_home":
      for person, value in home.public.items(section):
        if value == "true":
          run=False
          logging.debug(person+' is still home, not running leave function')

  if run:
    logging.debug('Executing RUN()')
    home.public.set('settings','autorun', 'false')

    cs = []
    for z in (0,1,2):
      home.public.set('zone'+str(z),'currentscene', 'null')
      logging.debug('zone'+str(z)+' current scene set to: null')
      home.public.set('zone'+str(z), 'previousscene', 'null')
      logging.debug('zone'+str(z)+' previous scene set to: null')
      home.saveSettings()

    if home.private.getboolean("Devices", "hue"):
      if home.private.getboolean("HueBridge", "count_down_lights_active"):
        # light 21 bloom
        # set all light to red using group countDownClock id
        home.setCountdownLights(home.private.get("HueGroups", "count_down_clock"), 'red', True)
        # light 1
        home.singleLightCountdown("16", 100)
        # light 2
        home.singleLightCountdown("19", 100)
        # light 3
        home.singleLightCountdown("20", 100)
      # turn off all lights, group 0
      home.groupLightsOff(0)

    # turn off all deocra wifi lights
    if home.private.getboolean('Devices','decora'):
      for x in range(1,6):
        home.decora(home.private.get('Decora', 'switch_'+str(x)), "OFF", "None")

    # turn off wemos
    for x in range(1,4):
      if home.private.getboolean('Wemo', 'wdevice'+str(x)+'_active'):
        if home.public.getboolean('wemo','wdevice'+str(x)+'_status'):
          cmd = '/usr/local/bin/wemo switch "' + home.public.get('wemo', 'wdevice'+str(x)+'_name')+ '" off'
          proc = subprocess.Popen([cmd], stdout=subprocess.PIPE, shell=True )
          (out, err) = proc.communicate()
          logging.debug(cmd)

    if home.private.getboolean("Devices", "Kevo"):
      # lock the door if necessary
      lockState = home.public.get('lock', 'status')
      # if the house is unlocked, then lock the door
      if lockState == "Unlocked":
         home.kevo("lock")
         home.public.set('lock', 'status', "Locked")
         home.saveSettings()

  # remove file that triggered script
  if os.path.isfile(leaveFile):
    logging.debug('removeing '+leaveFile)
    os.remove(leaveFile)

  home.saveSettings()
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

