import time, datetime
import myhouse
import os, sys
import logging

now = datetime.datetime.now()
leaveFile ="/home/host/Dropbox/IFTTT/leave/leave_home.txt"

def main(argv):

  home = myhouse.Home()
  logging.debug('Start')

  run='True'
  # set the person who triggered script as away
  # must be done first so that when we check for others being home it wont run
  if os.path.isfile(leaveFile):
    with file(leaveFile) as f:
      s = f.readline().rstrip()
      logging.info('marking '+s+' as not home')
      home.public.set("people_home", s,"no")
      home.saveSettings()
      home.blinkGroup( home.private.get('Groups','count_down_clock') )

  # check and see if anyone is home, if they are dont run actions
  for section in home.public.sections():
    if section == "people_home":
      for person, value in home.public.items(section):
        if value == 'yes':
          run=False
          logging.debug('leave-script: '+person+' is still home, not running leave function')

  if run:
    logging.debug('Executing RUN()')
    time.sleep(2)
    home.public.set('settings','autorun', 'off')
    home.public.set ('auto','currentscene','null')
    home.saveSettings()
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

end = datetime.datetime.now()
logging.debug('finished '+str(end-now))

if __name__ == "__main__":
  main(sys.argv[1:])

