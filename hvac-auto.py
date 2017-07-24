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
  current_humid = home.public.get('hvac_current', 'humid')
  current_heat_mode = home.public.get('hvac_current', 'heat_mode')
  
  if not hvac.pullStatus():
    return
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

    new_humid = home.public.get('hvac_current', 'humid')
    if current_humid !=  new_humid :
      if new_humid == 'on' :
        logging.info('Hudmidifer turned on')
      else :
        logging.info('Hudmidifer turned off')

  # setTime allows HVAC to be set ahead so not to undo itself
  setTime = datetime.datetime.strptime( (now + datetime.timedelta(minutes=3)).strftime("%H:%M"), '%H:%M')
  profile = home.public.get('hvac_current', 'currentactivity')
  hold = home.public.get('hvac_current','hold')
  hold_time = home.public.get('hvac_current','hold_time')

  if hold_time == "[{}]" :
    hold_time = now.time()
  else :
    hold_time = datetime.datetime.strptime(home.public.get('hvac_current','hold_time'), '%H:%M').time()

  logging.debug('profile = '+profile+', hold = '+hold+', hold_time = '+hold_time.strftime("%H:%M") )

  if home.public.getboolean('settings', 'hvac_auto'):
    ran=False
    until = setTime.strftime("%H:%M")
    # check if any one is home
    for section in home.public.sections():
      if section == "people_home":
        for person, value in home.public.items(section):
          if value == 'yes' and not ran:
            ran='True'
            # someone is home, Check HVAC profiles
            logging.debug(person+' home, checking if AWAY profile')
            if profile == 'away':
              # set hvac to home for 15 minutes
              if hvac.set_current_profile(until,'home'):
                current_activity = home.public.get('hvac_current', 'currentActivity')
              if current_activity !=  'home' :
                logging.info('setting home until '+until)

    # if ran is false, then no one is home, check profiles
    if not ran:
      logging.debug('nobody home, checking for test')
      if hold_time < setTime.time():
        # set hvac to home for 15 minutes
        if hvac.set_current_profile(until,'away'):
          current_activity = home.public.get('hvac_current', 'currentActivity')
        if current_activity !=  'away' :
          logging.info('setting away until '+until)


  end = datetime.datetime.now()
  logging.debug('finished '+str(end-now))

if __name__ == "__main__":
  main(sys.argv[1:])


