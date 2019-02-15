import myhouse
import os, sys, datetime, time
import logging

def main(argv):

  now = datetime.datetime.now()
  home = myhouse.Home()

  logging.debug('Running Leave Script')

  leaveFile = home.private.get('Path','ifttt')+"/leave/leave_home.txt"
  logging.debug("leaveFile: "+leaveFile)

  run='True'

  # set the person who triggered script as away
  # must be done first so that when we check for others being home it wont run
  if os.path.isfile(leaveFile):
    with open(leaveFile) as f:
      s = f.readline().rstrip()
      logging.info('marking '+s+' as not home')
      home.public.set("people_home", s,"false")
      home.saveSettings()
      home.blinkGroup( home.private.get('Groups','main_floor') )

  # check and see if anyone is home, if they are dont run actions
  for section in home.public.sections():
    if section == "people_home":
      for person, value in home.public.items(section):
        if value == "true":
          run=False
          logging.debug('leave-script: '+person+' is still home, not running leave function')

  if run:
    logging.debug('Executing RUN()')
    time.sleep(2)
    home.public.set('settings','autorun', 'false')
    home.public.set ('auto','currentscene','null')
    home.saveSettings()

    if home.private.getboolean("Devices", "hue"):
      if home.private.getboolean("HueBridge", "count_down_lights_active"):
        # light 21 bloom
        # set all light to red using group countDownClock id
        home.setCountdownLights(home.private.get("Groups", "count_down_clock"), 'red', True)
        # light 1
        home.singleLightCountdown("16", 100)
        # light 2
        home.singleLightCountdown("19", 100)
        # light 3
        home.singleLightCountdown("20", 100)
      # turn off all lights, group 0
      home.groupLightsOff(0)

    if home.private.getboolean("Devices", "Wemo"):
      if home.private.getboolean("Wemo", "wdevice2_active"):
        cmd = 'wemo switch '+home.public.get("wemo", "wdevice2_name")+" off"
        os.system(cmd)

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

  end = datetime.datetime.now()
  logging.debug('finished '+str(end-now))

if __name__ == "__main__":
  main(sys.argv[1:])

