import json
import requests
import time, datetime
from datetime import timedelta
from dateutil import tz
import xml.etree.ElementTree as ET
import os, subprocess
import sys, getopt
import ast
import configparser
#import pyKevo
import logging
import vivint
import smtplib
import requests
from decora_wifi import DecoraWiFiSession
from decora_wifi.models.person import Person
from decora_wifi.models.residential_account import ResidentialAccount
from decora_wifi.models.residence import Residence
from logging.config import BaseConfigurator
from logging.config import fileConfig

# must define using absolute path
RootPATH = "/home/ha/home_auto_scripts/" 

logging.config.fileConfig(RootPATH+'logging.ini', defaults={'logfilename': RootPATH+'home-auto.log'})
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

class Home(object):

  private = configparser.RawConfigParser()
  private.read(RootPATH+'private.ini')

  public = configparser.RawConfigParser()
  public.read(RootPATH+'public.ini')

  API = private.get('API','api')

  HueBridgeIP = private.get('HueBridge','ip')
  HueBridgeUN = private.get('HueBridge','username')

  recFile = private.get('Path','dvr')+'/'+private.get('dvr', 'recFile')
  upFile =  private.get('Path','dvr')+'/'+private.get('dvr', 'upFile')

  def saveSettings(self):
    with open(RootPATH+'public.ini', 'w+') as configfile:
      Home.public.write(configfile)
    with open(RootPATH+'private.ini', 'w+') as configfile:
      Home.private.write(configfile)

  def putCommand(self, api_url, payload):
    try:
      r = requests.put(api_url, data=json.dumps(payload))
      logging.debug(r.text)
      if 'error' in r.text:
        logging.error(r.text)
    except:
      logging.error(api_url)
      logging.error(payload)

  def sendText(self, message):

    sent_time = datetime.datetime.strptime(Home.private.get("MMS","sent"), "%Y-%m-%d %H:%M:%S.%f")
    now = datetime.datetime.now()
    max_delay = timedelta(minutes=int(Home.private.get("MMS","delay")))

    if now - sent_time > max_delay:
      logging.debug('attempting to send text: '+message)
      gmail_user = Home.private.get("Gmail","username")
      gmail_password = Home.private.get("Gmail","password")

      sent_from = "Home-Auto"
      to = [Home.private.get("MMS","email_1")]
      subject = 'Home-Auto'
      email_text = message
      try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(gmail_user, gmail_password)
        server.sendmail(sent_from, to, email_text)
        server.close()
        Home.private.set("MMS","sent", str(now) )
        Home.saveSettings(self)
        logging.info(message)
      except:
        logging.error('Something went wrong sending text.')
    else:
      logging.debug("not sending text as a recent one was sent")

  def get_armed_state(self):
    logging.debug('contacting vivint')
    try:
      session = vivint.VivintCloudSession( Home.private.get('Vivint','username'),Home.private.get('Vivint','password'))
      panels = session.get_panels()
      for panel in panels:
        panel.update_devices()
        devices = panel.get_devices()
        logging.debug('vivint: '+ panel.get_armed_state())
        return  panel.get_armed_state()
    except:
      return "connection error"

  def decora(self, switch_name, command, brightness):
    logging.debug('switch:'+switch_name+' command:'+str(command)+' brightness: '+brightness)
    username = Home.private.get('Decora','username')
    password = Home.private.get('Decora','password')

    session = DecoraWiFiSession()
    session.login(username, password)

    perms = session.user.get_residential_permissions()
    all_residences = []
    for permission in perms:
      if permission.residentialAccountId is not None:
        acct = ResidentialAccount(session, permission.residentialAccountId)
        for res in acct.get_residences():
          all_residences.append(res)
      elif permission.residenceId is not None:
        res = Residence(session, permission.residenceId)
        all_residences.append(res)
    for residence in all_residences:
      for switch in residence.get_iot_switches():
        attribs = {}
        if switch.name == switch_name:
          if brightness is not "None":
            attribs['brightness'] = brightness
          if command == 'ON':
            attribs['power'] = 'ON'
          else:
            attribs['power'] = 'OFF'
          logging.debug(switch.name+':'+str(attribs))
        switch.update_attributes(attribs)

    Person.logout(session)

  def isDropboxRunning(self):
    pidfile = os.path.expanduser("~/.dropbox/dropbox.pid")
    try:
      with open(pidfile, "r") as f:
          pid = int(f.read())
      with open("/proc/%d/cmdline" % pid, "r") as f:
          cmdline = f.read().lower()
    except:
      cmdline = ""

    if cmdline:
      return True
    else:
      return False

  def kevo(self, command):
    logging.debug('command:'+str(command))
    username = Home.private.get('Kevo','username')
    password = Home.private.get('Kevo','password')
    Door = pyKevo.pyKevo(username,password)
    Door.connect()
    if command == "status":
      return Door.lockState()
    elif command == "info":
      return Door.returnLockInfo()
    elif command == "lock":
      Door.lockLock()
      logging.debug(command+' Door')
      return "check"
    elif command == "unlock":
      Door.unlockLock()
      logging.debug(command+' Door')
      return "check"
    else:
      logging.error(command+' Door')
      return "error"

  def setTransTimeOfScene(self, sid, transtime):
    logging.debug('SID:'+str(sid)+' transtime:'+str(transtime))
    # get the current light states in the scene to update transition times
    api_url='http://'+Home.HueBridgeIP+'/api/'+Home.HueBridgeUN+'/scenes/'+sid
    r = requests.get(api_url)
    json_str = json.dumps(r.json())
    json_objects = json.loads(json_str)
    for lights in json_objects['lightstates'].items():
      lights[1]['transitiontime'] = int(transtime)
      api_url='http://'+Home.HueBridgeIP+'/api/'+Home.HueBridgeUN+'/scenes/'+sid+'/lightstates/'+lights[0]
      payload = lights[1]
      self.putCommand(api_url, payload)
      logging.debug('END')


#  def setTransTimeOfScene(self, sid, gid, transtime):
#    logging.debug('SID:'+str(sid)+' gid:'+str(gid)+' transtime:'+str(transtime))
#    for key, value in Home.private.items('HueScenes'):
#      if value == sid:
#        logging.debug(str(key)+' '+str(value))
#    # dealing with all lights, use group 0
#    api_url='http://'+Home.HueBridgeIP+'/api/'+Home.HueBridgeUN+'/groups/'+str(gid)+'/action'
#    # set the sceen using the id provided
#    payload = {'scene': sid, 'transitiontime': int(transtime), 'storelightstate':true}
#    self.putCommand(api_url, payload)
#    logging.debug('END')

  def setBringhtOfScene(self, sid, bri):
    logging.debug('SID:'+str(sid)+' bri:'+str(bri))
    # get the current light states in the scene to update transition times
    api_url='http://'+Home.HueBridgeIP+'/api/'+Home.HueBridgeUN+'/scenes/'+sid
    r = requests.get(api_url)
    json_str = json.dumps(r.json())
    json_objects = json.loads(json_str)
    for lights in json_objects['lightstates'].items():
      lights[1]['bri'] = int(bri)
      api_url='http://'+Home.HueBridgeIP+'/api/'+Home.HueBridgeUN+'/scenes/'+sid+'/lightstates/'+lights[0]
      payload = lights[1]
      self.putCommand(api_url, payload)
    logging.debug('END')

  def playScene(self, sid, gid):
    for key, value in Home.private.items('HueScenes'):
      if value == sid:
        logging.debug(str(key)+' '+str(value))
    # dealing with all lights, use group 0
    api_url='http://'+Home.HueBridgeIP+'/api/'+Home.HueBridgeUN+'/groups/'+str(gid)+'/action'
    # set the sceen using the id provided
    payload = {'scene': sid}
    self.putCommand(api_url, payload)
    logging.debug('END')

  def groupLightsOff (self, gid):
    logging.debug('GID:'+str(gid))
    # dealing with all lights, use group 0
    api_url='http://'+Home.HueBridgeIP+'/api/'+Home.HueBridgeUN+'/groups/'+str(gid)+'/action'
    # turn off all the lights in the house with a slow trasition
    payload = {'on': False,'transitiontime': 100}
    self.putCommand(api_url, payload)
    logging.debug("END")

  def groupLightsOn (self, gid):
    logging.debug('GID:'+str(gid))
    # dealing with all lights, use group 0
    api_url='http://'+Home.HueBridgeIP+'/api/'+Home.HueBridgeUN+'/groups/'+str(gid)+'/action'
    # turn off all the lights in the house with a slow trasition
    payload = {'on': True,'transitiontime': 100}
    self.putCommand(api_url, payload)
    logging.debug("END")


  def singleLightCountdown(self, light, transTime ):
    logging.debug('light:'+str(light)+' transtime:'+str(transTime))
    api_url='http://'+Home.HueBridgeIP+'/api/'+Home.HueBridgeUN+'/lights/'+light+'/state'
    payload = {'on': False,'transitiontime': transTime}
    self.putCommand(api_url, payload)
    time.sleep(transTime/10)
    logging.debug('END')

  def setCountdownLights (self, group, color, alert):
    logging.debug('group:'+str(group))
    api_url='http://'+Home.HueBridgeIP+'/api/'+Home.HueBridgeUN+'/groups/'+group+'/action'

    if color == "blue":
      hue=47125 #blue
      sat=254
      transTime=30
    if color == "red": 
      hue=64978 #red
      sat=254
      transTime=10
    else:
      hue=14956 #default color
      sat=140
      transTime=30


    payload = {'on': True, 'bri': 254, 'hue': hue, 'sat': sat, 'transitiontime': transTime}
    self.putCommand(api_url, payload)

    if alert:
      time.sleep(.1)
      payload = {'on': True, 'bri': 254, 'hue': 64978, 'sat': 254, 'alert': "select"}
      self.putCommand(api_url, payload)
    time.sleep(1)
    logging.debug('END')

  def blinkGroup ( self, group):
    logging.debug('group:'+str(group))
    api_url='http://'+Home.HueBridgeIP+'/api/'+Home.HueBridgeUN+'/groups/'+group+'/action'
    payload = {'on': True, 'alert': "select"}
    self.putCommand(api_url, payload)
    time.sleep(1)
    logging.debug('END')

  def saveLightState (self, sid):
    # saves the current light state of the lights in the scene
    logging.debug('sid:'+str(sid))
    api_url = 'http://'+Home.HueBridgeIP+'/api/'+Home.HueBridgeUN+'/scenes/'+sid
    tempName = 'saveState_'+time.strftime('%a-%H-%M-%S')
    logging.debug('saveLightState: tempName='+tempName)
    payload = {'name':tempName, "storelightstate": True} 
    self.putCommand(api_url, payload)

  def getLightSchedule (self, id):
    # saves the current light state of the lights in the scene
    logging.debug('id:'+str(id))
    api_url = 'http://'+Home.HueBridgeIP+'/api/'+Home.HueBridgeUN+'/schedules/'+str(id)
    r = requests.get(api_url)
    json_str = json.dumps(r.json())
    json_objects = json.loads(json_str)
    logging.debug('END')
    return json_objects

  def setLightScheduleStatus (self, id, status):
    # saves the current light state of the lights in the scene
    logging.debug('id:'+str(id)+' status:'+str(status))
    api_url = 'http://'+Home.HueBridgeIP+'/api/'+Home.HueBridgeUN+'/schedules/'+str(id)
    payload = payload = {'status': status} 
    self.putCommand(api_url, payload)
    logging.debug('END')

  def setLightScheduleTime (self, id, time):
    # saves the current light state of the lights in the scene
    logging.debug('id:'+str(id)+' time:'+str(time))
    api_url = 'http://'+Home.HueBridgeIP+'/api/'+Home.HueBridgeUN+'/schedules/'+str(id)
    payload = payload = {'localtime': "W127/T"+str(time)} 
    self.putCommand(api_url, payload)
    logging.debug('END')

  # not being used any more
  def restoreLightState(self, rjson, sid):
    logging.debug('running')
    json_objects = json.loads(rjson)
    lightList = []
    for light in json_objects:
      if light['state']['on']:
#        payload = {'on':light['state']['on'], 'bri':light['state']['bri'], 'sat':light['state']['sat'], 'ct':light['state']['ct'], 'hue':light['state']['hue'], 'xy':light['state']['xy'], 'transitiontime':100}
        # set the light to its previosue state but dont turn it on yet
        payload = {'on': True, 'bri':light['state']['bri'], 'sat':light['state']['sat'], 'ct':light['state']['ct'], 'hue':light['state']['hue'], 'xy':light['state']['xy'], 'transitiontime':100}
        lightList.append(light)
      else:
        payload = {'on': False}
      api_url='http://'+Home.HueBridgeIP+'/api/'+Home.HueBridgeUN+'/lights/'+str(light['light'])+'/state/'
      self.putCommand(api_url, payload)
    # update movie temp scene with the blubs that should be on
    api_url='http://'+Home.HueBridgeIP+'/api/'+Home.HueBridgeUN+'/scenes/'+sid
    payload = {'lights':lightList, "storelightstate": True}
    self.putCommand(api_url, payload)
    logging.debug('END')

  def SetQuickTrans(self, scene):
    logging.debug('scene'+scene)
    self.setTransTimeOfScene(Home.private.get('Scenes', scene), 10)
    time.sleep(.5)
    logging.debug('END')

  def getWeather(self):
    logging.debug('myhouse.getWeather')
    api_url= Home.private.get('Weather', 'url')
    try:
      r = requests.get(api_url)
      json_str = json.dumps(r.json())
      json_objects = json.loads(json_str)
      logging.debug('myhouse.getWeather: END')
      return json_objects
    except:
      logging.error('could not get weather')
      return "error"

  def pullDVRupcoming(self):
    api_url='http://192.168.1.250:6544/Dvr/GetUpcomingList?'
    r = requests.get(api_url)
    if r.status_code == 200:
        with open(Home.upFile, 'wb') as f:
            for chunk in r:
                f.write(chunk)

  def pullDVRrecorded(self):
    api_url='http://192.168.1.250:6544/Dvr/GetRecordedList?Count=10&Descending=true'
    r = requests.get(api_url)
    if r.status_code == 200:
        with open(Home.recFile, 'wb') as f:
            for chunk in r:
                f.write(chunk)

  # today = 0, tomorrow = 1, next = 2 so on , max like 18
  def getDVRshows(self, day_num, file):
      logging.debug('START')
      showlist= {}

      now = datetime.datetime.now()
      dayAdjust = now + timedelta(days=day_num)
      target = dayAdjust.strftime('%Y-%m-%d')

      from_zone = tz.gettz('UTC')
      to_zone = tz.gettz('America/New_York')
      root = ET.parse(file).getroot()
      for programlist in root.iter('ProgramList'):
          for program in programlist.iter('Programs'):
              x=1
              for show in program.findall('Program'):
                  showStart = show.find('StartTime').text
                  utc = datetime.datetime.strptime(showStart, '%Y-%m-%dT%H:%M:%SZ')
                  utc = utc.replace(tzinfo=from_zone)
                  if  utc.astimezone(to_zone).strftime('%Y-%m-%d') == target:
                      starttime = utc.astimezone(to_zone).strftime('%H:%M:%S')
                      title = show.find('Title').text
                      subtitle = show.find('SubTitle').text
                      for entry in program.iter('Recording'):
                          recordID = entry.find('RecordedId').text
                          status =  entry.find('Status').text
                      oneshow = {'starttime':starttime, 'title':title, 'subtitle':subtitle, 'RecordedID':recordID, 'Status':status}
                      showlist['show_'+str(x)] = oneshow
                      logging.debug('found: '+str(oneshow['title']))
                      x=x+1
      logging.debug('END')
      return json.dumps(showlist)



  #######################
  # WEMO device CONTROL #
  def triggerWemoDeviceOn(self, num):
      logging.debug('start , using id'+str(num))
      if Home.private.getboolean('Wemo', 'wdevice'+str(num)+'_active'):
          if not Home.public.getboolean('wemo','wdevice'+str(num)+'_status'):
              cmd = '/usr/local/bin/wemo switch "'+Home.public.get('wemo', 'wdevice'+str(num)+'_name')+ '" on'
              proc = subprocess.Popen([cmd], stdout=subprocess.PIPE, shell=True )
              (out, err) = proc.communicate()
              logging.debug(cmd)
      else:
        logging.warning('Wemo device wdevice'+str(num)+' not active')

  def triggerWemoDeviceOff(self, num):
      if Home.private.getboolean('Wemo', 'wdevice'+str(num)+'_active'):
          if Home.public.getboolean('wemo','wdevice'+str(num)+'_status'):
              cmd = '/usr/local/bin/wemo switch "'+Home.public.get('wemo', 'wdevice'+str(num)+'_name')+ '" off'
              proc = subprocess.Popen([cmd], stdout=subprocess.PIPE, shell=True )
              (out, err) = proc.communicate()
              logging.debug(cmd)

  def updateWemo(self):
      for x in range(1,Home.private.getint('Wemo','device_count')+1,1):
          x = str(x)
          if Home.private.getboolean('Wemo', 'wdevice'+x+'_active'):
              pDevice = Home.public.get('wemo', 'wdevice'+x+'_status')
              cmd = '/usr/local/bin/wemo switch "'+Home.public.get('wemo', 'wdevice'+x+'_name')+'" status'
              proc = subprocess.Popen([cmd], stdout=subprocess.PIPE, shell=True )
              (out, err) = proc.communicate()
              Home.public.set('wemo', 'wdevice'+x+'_status', out.rstrip(b'\n').decode() )
              Home.saveSettings(self)
              cDevice = str(Home.public.get('wemo', 'wdevice'+x+'_status'))
              if pDevice != cDevice:
                  logging.info(Home.public.get('wemo', 'wdevice'+x+'_name')+' changed from '+pDevice+' to '+cDevice)


  def getPerson(self, name):
      r = requests.get(url = Home.API+"person/"+name)
      data = r.json()
      return data

  def togglePersonHome(self, id):
      r = requests.get(url =  Home.API+"person/"+str(id)+'/toggleHome')
      data = r.json()
      logging.info(data['status'])

  def getHueSensorData(self, id):
    logging.debug('id:'+str(id))
    api_url = 'http://'+Home.HueBridgeIP+'/api/'+Home.HueBridgeUN+'/sensors/'+str(id)
    r = requests.get(api_url)
    json_str = json.dumps(r.json())
    json_objects = json.loads(json_str)
    logging.debug('END')
    return json_objects


