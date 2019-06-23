import myhouse
import os, sys, ast, time, datetime
import logging, subprocess

def main(argv):

  now = datetime.datetime.now()
  home = myhouse.Home()

  bedFile = sys.argv[1]

  logging.info('Running relax script')
  # this is for when we are in the bedroom and not going back 
  # into the rest of the house at night

  home.public.set('settings','zone0_evening', 'false')
  home.public.set('settings','zone1_evening', 'false')

  # lock the door if necessary
  if home.private.getboolean('Devices', 'kevo'):
    lockState = home.public.get('lock', 'status')
    # if the house is unlocked, then lock the door
    if lockState == "Unlocked":
       home.kevo("lock")
       home.public.set('lock', 'status', "Locked")

  # save new settings
  home.saveSettings()

  # turn off other lights (leave litch lamp on untill bed script)
  if home.private.getboolean('Devices', 'decora'):
    for x in range(2,home.private.getint('Decora','switch_count')+1)):
      x = str(x)
      home.decora(home.private.get('Decora', 'switch_'+str(x)), "OFF", "None")

  # turn off wemo devices not  device 1  (lava lamp in bedr0om)
  if home.private.getboolean('Devices', 'wemo'):
    for x in range(2,4):
      x = str(x)
      if home.private.getboolean('Wemo', 'wdevice'+x+'_active'):
        if home.public.get('wemo', 'wdevice'+x+'_status'):
          cmd = '/usr/local/bin/wemo switch "'+home.public.get('wemo', 'wdevice'+x+'_name')+'" off'
          proc = subprocess.Popen([cmd], stdout=subprocess.PIPE, shell=True )
          (out, err) = proc.communicate()
          logging.debug(cmd)

  cs = []
  for z in (0,1):  # keep zone 2 active
    home.public.set('zone'+str(z),'currentscene', 'null')
    logging.debug('zone'+str(z)+' current scene set to: null')
    home.saveSettings()

  # turn off all zone lights
  home.groupLightsOff(home.private.get('HueGroups','main_floor'))
  home.groupLightsOff(home.private.get('HueGroups','movie'))
  home.groupLightsOff(home.private.get('HueGroups','basement_hall'))



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

