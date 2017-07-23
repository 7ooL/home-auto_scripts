import time, datetime
import myhouse
import os, sys
import logging
import ConfigParser

public = ConfigParser.RawConfigParser()
public.read('/home/host/home_auto_scripts/public.ini')
leaveFile ="/home/host/Dropbox/IFTTT/leave/leave_home.txt"

def saveSettings():
  with open(r'/home/host/home_auto_scripts/public.ini', 'wb') as configfile:
    public.write(configfile)

def main(argv):

  logging.debug('leave-script: START')

  run='True'
  # set the person who triggered script as away
  # must be done first so that when we check for others being home it wont run
  if os.path.isfile(leaveFile):
    with file(leaveFile) as f:
      s = f.readline().rstrip()
      logging.info('leave-script: '+s)
      public.set("people_home", s,"no")
      saveSettings()

  # check and see if anyone is home, if they are dont run actions
  for section in public.sections():
    if section == "people_home":
      for person, value in public.items(section):
        if value == 'yes':
          run=False
          logging.debug('leave-script: '+person+' is still home, not running leave function')

  if run:
    logging.debug('leave-script: Executing RUN()')
    time.sleep(2)
    home = myhouse.Home()
    public.set('settings','autorun', 'off')
    public.set ('auto','currentscene','null')
    saveSettings()
    # light 21 bloom
    # set all counters to red using group countDownClock id=4
    home.setCountdownLights("4", 'red', True)
    # counter 1
    home.singleLightCountdown("16", 100)
    # counter 2
    home.singleLightCountdown("19", 100)
    # counter 3
    home.singleLightCountdown("20", 100)
    # turn off all lights, group 0
    home.groupLightsOff(0)

  # remove file that triggered script
  if os.path.isfile(leaveFile):
    logging.debug('leave-script: removeing '+leaveFile)
    os.remove(leaveFile)

  logging.debug('leave-script: END')

if __name__ == "__main__":
  main(sys.argv[1:])

