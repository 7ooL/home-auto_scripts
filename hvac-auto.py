import myhouse
import pyInfinitude.pyInfinitude
import os, sys, datetime, time
import logging

def main(argv):

  now = datetime.datetime.now()
  logging.debug('Running hvac-auto script')

  home = myhouse.Home()

  hvacIP = home.private.get('hvac', 'ip')
  hvacPort = home.private.get('hvac', 'port')
  hvacFile = home.private.get('hvac', 'file')
  hvacStatus = home.private.get('hvac', 'status')
  hvac = pyInfinitude.pyInfinitude.infinitude(hvacIP,hvacPort,hvacFile, hvacStatus)

  # pull and set current hvac conditions
  prev_humid = home.public.get('hvac_current', 'humid')
  prev_hold = home.public.get('hvac_current', "hold")
  prev_profile = home.public.get('hvac_current', 'currentactivity')

  if not hvac.pullStatus():
    logging.error('pullStatus Fail')
  else:
    zone = int(home.private.get('hvac', 'zone'))
    home.public.set('hvac_current', "rt", hvac.get_current_zone_rt(zone)) # current temp
    home.public.set('hvac_current', "rh", hvac.get_current_zone_rh(zone)) # current humdiity
    home.public.set('hvac_current', "currentActivity", hvac.get_current_zone_currentActivity(zone))
    home.public.set('hvac_current', "htsp", hvac.get_current_zone_htsp(zone)) # current heat setpoint
    home.public.set('hvac_current', "clsp", hvac.get_current_zone_clsp(zone)) # current cool setpoint
    home.public.set('hvac_current', "fan", hvac.get_current_zone_fan(zone)) # current fan status
    home.public.set('hvac_current', "hold", hvac.get_current_zone_hold(zone)) # current hold status
    home.public.set('hvac_current', "hold_time",hvac.get_current_zone_otmr(zone)) # current hold time
    home.public.set('hvac_current', "vaca_running",hvac.get_current_vacatrunning())
    home.public.set('hvac_current', "heat_mode",hvac.get_current_mode()) 
    home.public.set('hvac_current', "temp_unit",hvac.get_current_cfgem()) # F or C
    home.public.set('hvac_current', "filtrlvl",hvac.get_current_filtrlvl() )
    home.public.set('hvac_current', "humlvl",hvac.get_current_humlvl() ) 
    home.public.set('hvac_current', "humid", hvac.get_current_humid()) 
    home.public.set('hvac_current', 'updating', 'no')
    home.saveSettings()

    current_humid = home.public.get('hvac_current', 'humid')
    if prev_humid !=  current_humid :
      logging.info('humid status change: '+prev_humid+' to '+current_humid)

    current_hold = home.public.get('hvac_current','hold')
    if prev_hold != current_hold:
      logging.info('hold status change: '+prev_hold+' to '+current_hold)

    current_profile = home.public.get('hvac_current', 'currentactivity')
    if prev_profile != current_profile:
      logging.info('profile status change: '+prev_profile+' to '+current_profile)

    # setTime allows HVAC to be set ahead so not to undo itself
    setTime = datetime.datetime.strptime( (now + datetime.timedelta(minutes=3)).strftime("%H:%M"), '%H:%M')
    hold_time = home.public.get('hvac_current','hold_time')

    if hold_time == "[{}]" :
      hold_time = now.time()
    else :
      hold_time = datetime.datetime.strptime(home.public.get('hvac_current','hold_time'), '%H:%M').time()

    logging.debug('profile = '+current_profile+', hold = '+current_hold+', hold_time = '+hold_time.strftime("%H:%M") )

    if home.public.getboolean('settings', 'hvac_auto'):
      ran = False
      until = setTime.strftime("%H:%M")
      # check if any one is home
      for section in home.public.sections():
        if section == "people_home":
          for person, value in home.public.items(section):
            if value == 'yes' and not ran:
              ran = True
              # someone is home, Check HVAC profiles
              logging.debug(person+' home, checking if AWAY profile')
              if current_profile == 'away':
                # set hvac to home for 15 minutes
                if hvac.set_current_profile(until,'home'):
                  if not hvac.pushConfig():
                    logging.error('pushConfig Fail')
                else:
                  logging.error('set profile Fail')


      # if ran is false, then no one is home, check profiles
      if not ran:
        logging.debug('nobody home, checking for test')
        if hold_time < setTime.time():
          # set hvac to home for 15 minutes
          if hvac.set_current_profile(until,'away'):
            if not hvac.pushConfig():
              logging.error('pushConfig Fail')
          else:
              logging.error('set profile Fail')


  end = datetime.datetime.now()
  logging.debug('finished '+str(end-now))

if __name__ == "__main__":
  main(sys.argv[1:])


