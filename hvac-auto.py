import myhouse
import pyInfinitude.pyInfinitude
import os, sys, datetime, time
import logging

def main(argv):

  now = datetime.datetime.now()
  logging.debug('Running hvac-auto script')

  home = myhouse.Home()

  for s in range(0,home.private.getint('HVAC', 'total')):

    logging.debug('hvac_current_'+str(s)+' running')
    zone = int(home.private.get('HVAC_'+str(s), 'zone'))
    hvacIP = home.private.get('HVAC_'+str(s), 'ip')
    hvacPort = home.private.get('HVAC_'+str(s), 'port')
    hvacFile = home.private.get('Path','hvac')+'/'+home.private.get('HVAC_'+str(s), 'file')
    hvacStatus = home.private.get('Path','hvac')+'/'+home.private.get('HVAC_'+str(s), 'status')
    hvac = pyInfinitude.pyInfinitude.infinitude(hvacIP,hvacPort,hvacFile, hvacStatus)

    if home.public.get('hvac_current_'+str(s), 'updating') == 'yes':
      logging.debug('updating was yes')
      file = open('/var/www/html/home-auto/hvac/hvac_hold.txt','r')
      words = file.readline()
      file.close()

      line = words.split(",")

      cd = line[0]
      temp = line[1]
      until = line[2]

      #  set HVAC manual temp
      ct = float(home.public.get('hvac_current_'+str(s), 'rt'))
      temp = float(temp)
      if ct > temp:
        clsp = temp
        htsp = (temp - 3)
        logging.debug(str(ct)+' > '+str(temp)+' htsp-3')
      elif ct < temp:
        clsp = (temp + 3)
        htsp = temp
        logging.debug(str(ct)+" < "+str(temp)+' clsp+3')
      else:
        clsp = temp
        htsp = temp

      logging.debug('temp: '+str(temp)+' until: '+str(until))

      # update manual profile clsp and htsp
      # manual is ID:4
      hvac.pullConfig()
      time.sleep(1)
      hvac.set_zone_activity_clsp(zone,4,clsp)
      hvac.set_zone_activity_htsp(zone,4,htsp)
      hvac.set_zone_otmr(zone,until)
      hvac.set_zone_holdActivity(zone,'manual')
      hvac.set_zone_hold(zone,'on')
      time.sleep(1)
      hvac.pushConfig()

    # pull and set current hvac conditions
    prev_humid = home.public.get('hvac_current_'+str(s), 'humid')
    prev_hold = home.public.get('hvac_current_'+str(s), "hold")
    prev_profile = home.public.get('hvac_current_'+str(s), 'currentactivity')

    if not hvac.pullStatus():
      logging.error('pullStatus Fail')
    else:
      home.public.set('hvac_current_'+str(s), "rt", hvac.get_current_zone_rt(zone)) # current temp
      home.public.set('hvac_current_'+str(s), "rh", hvac.get_current_zone_rh(zone)) # current humdiity
      home.public.set('hvac_current_'+str(s), "currentActivity", hvac.get_current_zone_currentActivity(zone))
      home.public.set('hvac_current_'+str(s), "htsp", hvac.get_current_zone_htsp(zone)) # current heat setpoint
      home.public.set('hvac_current_'+str(s), "clsp", hvac.get_current_zone_clsp(zone)) # current cool setpoint
      home.public.set('hvac_current_'+str(s), "fan", hvac.get_current_zone_fan(zone)) # current fan status
      home.public.set('hvac_current_'+str(s), "hold", hvac.get_current_zone_hold(zone)) # current hold status
      home.public.set('hvac_current_'+str(s), "hold_time",hvac.get_current_zone_otmr(zone)) # current hold time
      home.public.set('hvac_current_'+str(s), "vaca_running",hvac.get_current_vacatrunning())
      home.public.set('hvac_current_'+str(s), "heat_mode",hvac.get_current_mode()) 
      home.public.set('hvac_current_'+str(s), "temp_unit",hvac.get_current_cfgem()) # F or C
      home.public.set('hvac_current_'+str(s), "filtrlvl",hvac.get_current_filtrlvl() )
      home.public.set('hvac_current_'+str(s), "humlvl",hvac.get_current_humlvl() ) 
      home.public.set('hvac_current_'+str(s), "humid", hvac.get_current_humid()) 
      home.public.set('hvac_current_'+str(s), 'updating', 'no')
      home.saveSettings()

      current_humid = home.public.get('hvac_current_'+str(s), 'humid')
      if prev_humid !=  current_humid :
        logging.info('system('+str(s)+') humid status change: '+prev_humid+' to '+current_humid)

      current_hold = home.public.get('hvac_current_'+str(s),'hold')
      if prev_hold != current_hold:
        logging.info('system('+str(s)+') hold status change: '+prev_hold+' to '+current_hold)

      current_profile = home.public.get('hvac_current_'+str(s), 'currentactivity')
      if prev_profile != current_profile:
        logging.info('system('+str(s)+') profile status change: '+prev_profile+' to '+current_profile)

      # setTime allows HVAC to be set ahead so not to undo itself
      setTime = datetime.datetime.strptime( (now + datetime.timedelta(minutes=2)).strftime("%H:%M"), '%H:%M')
      hold_time = home.public.get('hvac_current_'+str(s),'hold_time')

      if hold_time == "[{}]" :
        hold_time = now.time()
      else :
        hold_time = datetime.datetime.strptime(home.public.get('hvac_current_'+str(s),'hold_time'), '%H:%M').time()

      logging.debug('profile = '+current_profile+', hold = '+current_hold+', hold_time = '+hold_time.strftime("%H:%M") )

      if home.public.getboolean('settings', 'hvac_auto'):
        ran = False
        # check if any one is home
          # check and see if anyone is home, if they are dont run actions
        for person, value in home.public.items("people_home"):
          if value == "true":
            ran = True
            # someone is home, Check HVAC profiles
            logging.debug(person+' home, checking if AWAY profile')
            if current_profile == 'away':
              # take hold off, defaulting back to per schedule
              hvac.pullConfig()
              time.sleep(1)
              hvac.set_zone_hold(zone,'off')
              time.sleep(1)
              hvac.pushConfig()


        # if ran is false, then no one is home, check profiles
        if not ran:
          logging.debug('nobody home, checking for test')
          if hold_time < setTime.time():
            # set hvac to home for 15 minutes
            dt = now + datetime.timedelta(minutes=2)
            newHold = dt.replace(minute=0, second=0) + datetime.timedelta(hours=2, minutes=(dt.minute//15+1)*15)
            hvac.pullConfig()
            time.sleep(1)
            hvac.set_zone_holdActivity(zone,'away')
            hvac.set_zone_otmr(zone,newHold.strftime("%H:%M"))
            hvac.set_zone_hold(zone,'on')
            time.sleep(1)
            logging.info('system('+str(s)+') Set AWAY profile until '+str(newHold))
            hvac.pushConfig()

  end = datetime.datetime.now()
  logging.debug('finished '+str(end-now))

if __name__ == "__main__":
  main(sys.argv[1:])


