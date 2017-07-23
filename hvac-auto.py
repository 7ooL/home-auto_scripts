import ConfigParser
import myhouse
import datetime, time
import logging
import subprocess
import sys, os


public = ConfigParser.RawConfigParser()
public.read('/home/host/home_auto_scripts/public.ini')

private = ConfigParser.RawConfigParser()
private.read('/home/host/home_auto_scripts/private.ini')

home = myhouse.Home()
now = datetime.datetime.now()

logging.debug('hvac-auto.py: START')

def pullCurrentStatus ():
  current_humid = public.get('hvac_current', 'humid')
  current_heat_mode = public.get('hvac_current', 'heat_mode')

  # get the current operating status of the havc system, including indoor numbers
  statusData = home.getHVACstatus()
#  logging.info(statusData)
  # if for some reason you get pull hvac data, restart that server
  if statusData == "Error":
    HOST=private.get('hvac', 'ip')
    RESPONSE = os.system("ping -c 1 " + HOST +' &>\\dev\\null')
    # check if server is up.
    if RESPONSE == 0:
      COMMAND="sudo reboot"
      ssh = subprocess.Popen(["ssh", "%s" % 'pi@'+HOST, COMMAND],
                       shell=False,
                       stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE)
      logging.info('hvac-auto.py: Attempting to restart Infinitude server')
    else:
      logging.info('hvac-auto.py: Server unreachable')


  else:
    public.set('hvac_current', "rt", str(statusData['status'][0]['zones'][0]['zone'][0]['rt']).replace('[u\'' ,'').replace("\']","")) # current temp
    public.set('hvac_current', "rh", str(statusData['status'][0]['zones'][0]['zone'][0]['rh']).replace('[u\'' ,'').replace("\']","")) # current humdiity
    public.set('hvac_current', "currentActivity", str(statusData['status'][0]['zones'][0]['zone'][0]['currentActivity']).replace('[u\'' ,'').replace("\']",""))
    public.set('hvac_current', "htsp", str(statusData['status'][0]['zones'][0]['zone'][0]['htsp']).replace('[u\'' ,'').replace("\']","")) # current heat setpoint
    public.set('hvac_current', "clsp", str(statusData['status'][0]['zones'][0]['zone'][0]['clsp']).replace('[u\'' ,'').replace("\']","")) # current cool setpoint
    public.set('hvac_current', "fan", str(statusData['status'][0]['zones'][0]['zone'][0]['fan']).replace('[u\'' ,'').replace("\']","")) # current fan status
    public.set('hvac_current', "hold", str(statusData['status'][0]['zones'][0]['zone'][0]['hold']).replace('[u\'' ,'').replace("\']","")) # current hold status
    public.set('hvac_current', "hold_time", str(statusData['status'][0]['zones'][0]['zone'][0]['otmr']).replace('[u\'' ,'').replace("\']","")) # current hold time
    public.set('hvac_current', "vaca_running", str(statusData['status'][0]['vacatrunning']).replace('[u\'' ,'').replace("\']",""))
    public.set('hvac_current', "heat_mode", str(statusData['status'][0]['mode']).replace('[u\'' ,'').replace("\']","")) # this is what gives value of, off, hpelecthea$
    public.set('hvac_current', "temp_unit", str(statusData['status'][0]['cfgem']).replace('[u\'' ,'').replace("\']","")) # F or C
    public.set('hvac_current', "filtrlvl", str(statusData['status'][0]['filtrlvl']).replace('[u\'' ,'').replace("\']","")) # F or C
    public.set('hvac_current', "humlvl", str(statusData['status'][0]['humlvl']).replace('[u\'' ,'').replace("\']","")) # F or C
    public.set('hvac_current', "humid", str(statusData['status'][0]['humid']).replace('[u\'' ,'').replace("\']","")) # F or C
    public.set('hvac_current', 'updating', 'no')
    with open(r'/home/host/home_auto_scripts/public.ini', 'wb') as configfile:
      public.write(configfile)

    new_humid = public.get('hvac_current', 'humid')
    if current_humid !=  new_humid :
      if new_humid == 'on' :
        logging.info('hvac-auto.py: Hudmidifer turned on')
      else :
        logging.info('hvac-auto.py: Hudmidifer turned off')


#########################
# HVAC PROFILE TRIGGERS #
#########################
pullCurrentStatus()

# setTime allows HVAC to be set ahead so not to undo itself
setTime = datetime.datetime.strptime( (now + datetime.timedelta(minutes=3)).strftime("%H:%M"), '%H:%M')
profile = public.get('hvac_current', 'currentactivity')
hold = public.get('hvac_current','hold')
hold_time = public.get('hvac_current','hold_time')
if hold_time == "[{}]" :
  hold_time = now.time()
else :
  hold_time = datetime.datetime.strptime(public.get('hvac_current','hold_time'), '%H:%M').time()
logging.debug('hvac-auto.py: profile = '+profile+', hold = '+hold+', hold_time = '+hold_time.strftime("%H:%M") )
logging.debug('hvac-auto.py: test: '+hold_time.strftime("%c")+' < '+setTime.time().strftime("%c") )
logging.debug('hvac-auto.py: test: '+hold_time.strftime("%H:%M")+' < '+setTime.strftime("%H:%M") )

if ( hold_time < setTime.time()):
  logging.debug('hvac-auto.py: test: TRUE')
else:
  logging.debug('hvac-auto.py: test: FALSE')

if public.getboolean('settings', 'hvac_auto'):
  ran=False
  until = setTime.strftime("%H:%M")
  # check if any one is home
  for section in public.sections():
    if section == "people_home":
      for person, value in public.items(section):
        if value == 'yes' and not ran:
          ran='True'
          # someone is home, Check HVAC profiles
          logging.debug('hvac-auto.py: '+person+' home, checking if AWAY profile')
          if profile == 'away':
            # set hvac to home for 15 minutes
            home.setHVACprofile(until,'home')


  # if ran is false, then noone is home, check profiles
  if not ran:
    logging.debug('hvac-auto.py: Nobody home, checking for test')
    if hold_time < setTime.time():
      # set hvac to home for 15 minutes
      home.setHVACprofile(until,'away')

logging.debug('hvac-auto.py: END')
