import myhouse
import pyInfinitude.pyInfinitude
import os, sys, datetime, time
import logging


def main(argv):

  now = datetime.datetime.now()
  logging.debug('Running hvac-hold script')

  home = myhouse.Home()

  hvacIP = home.private.get('hvac', 'ip')
  hvacPort = home.private.get('hvac', 'port')
  hvacFile = home.private.get('hvac', 'file')
  hvacStatus = home.private.get('hvac', 'status')
  hvac = pyInfinitude.pyInfinitude.infinitude(hvacIP,hvacPort,hvacFile, hvacStatus)

  home.public.set('hvac_current', 'updating', 'yes')
  home.saveSettings()

  file = open('/var/www/html/home-auto/hvac/hvac_hold.txt','r') 
  words = file.readline()
  file.close()

  line = words.split(",")

  cd = line[0]
  temp = line[1]
  until = line[2]

  #  set HVAC manual temp
  ct = float(home.public.get('hvac_current', 'rt'))
  temp = float(temp)
  if ct > temp:
    clsp = temp
    htsp = temp - 3
    logging.debug(str(ct)+' > '+str(temp)+' htsp-3')
  elif ct < temp:
    clsp = temp + 3
    htsp = temp
    logging.debug(str(ct)+" < "+str(temp)+' clsp+3')
  else:
    clsp = temp
    htsp = temp

  zone = int(home.private.get('hvac', 'zone'))
  # update manual profile clsp and htsp
  # manual is ID:4
  hvac.set_zone_activity_clsp(zone,4,clsp)
  hvac.set_zone_activity_htsp(zone,4,htsp)
  #  push config changes to hvac system
  if hvac.pushConfig():
    time.sleep(5)
    # activate the manual profile we just updated
    logging.info('attempting to set manual until '+until)
    hvac.set_current_profile(until,'manual')
  else:
    logging.error('push config failed')

  end = datetime.datetime.now()
  logging.debug('finished '+str(end-now))

if __name__ == "__main__":
  main(sys.argv[1:])


