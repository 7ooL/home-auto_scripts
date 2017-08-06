import json
import requests
import time, datetime
from datetime import timedelta
from dateutil import tz
import xml.etree.ElementTree as ET
import os
import sys, getopt
import ast
import ConfigParser
import pyKevo
import logging
from logging.config import BaseConfigurator
from logging.config import fileConfig

logging.config.fileConfig('/home/host/home_auto_scripts/logging.ini')
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

class Home(object):

  private = ConfigParser.RawConfigParser()
  private.read('/home/host/home_auto_scripts/private.ini')

  public = ConfigParser.RawConfigParser()
  public.read('/home/host/home_auto_scripts/public.ini')

  bridgeIP = private.get('Bridge','ip')
  bridgeUN = private.get('Bridge','username')

  hvacIP = private.get('hvac', 'ip')
  hvacPort = private.get('hvac', 'port')

  def saveSettings(self):
    with open(r'/home/host/home_auto_scripts/public.ini', 'wb') as configfile:
      Home.public.write(configfile)
    with open(r'/home/host/home_auto_scripts/private.ini', 'wb') as configfile:
      Home.private.write(configfile)

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
    api_url='http://'+Home.bridgeIP+'/api/'+Home.bridgeUN+'/scenes/'+sid
    r = requests.get(api_url)
    json_str = json.dumps(r.json())
    json_objects = json.loads(json_str)
    for lights in json_objects['lightstates'].iteritems():
      lights[1]['transitiontime'] = int(transtime)
      api_url='http://'+Home.bridgeIP+'/api/'+Home.bridgeUN+'/scenes/'+sid+'/lightstates/'+lights[0]
      payload = lights[1]
      r = requests.put(api_url, data=json.dumps(payload))
      logging.debug(r.text)
      if 'error' in r.text:
        logging.error(r.text)
    logging.debug('END')


  def setBringhtOfScene(self, sid, bri):
    logging.debug('SID:'+str(sid)+' bri:'+str(bri))
    # get the current light states in the scene to update transition times
    api_url='http://'+Home.bridgeIP+'/api/'+Home.bridgeUN+'/scenes/'+sid
    r = requests.get(api_url)
    json_str = json.dumps(r.json())
    json_objects = json.loads(json_str)
    for lights in json_objects['lightstates'].iteritems():
      lights[1]['bri'] = int(bri)
      api_url='http://'+Home.bridgeIP+'/api/'+Home.bridgeUN+'/scenes/'+sid+'/lightstates/'+lights[0]
      payload = lights[1]
      r = requests.put(api_url, data=json.dumps(payload))
      logging.debug(r.text)
      if 'error' in r.text:
        logging.error(r.text)
    logging.debug('END')

  def playScene(self, sid, gid):
    for key, value in Home.private.items('Scenes'):
      if value == sid:
        logging.debug(str(key)+' '+str(value))
    # dealing with all lights, use group 0
    api_url='http://'+Home.bridgeIP+'/api/'+Home.bridgeUN+'/groups/'+str(gid)+'/action'
    # turn off all the lights in the house with a slow trasition
    payload = {'scene': sid}
    r = requests.put(api_url, data=json.dumps(payload))
    logging.debug(r.text)
    if 'error' in r.text:
      logging.error(r.text)
    logging.debug('END')

  def groupLightsOff (self, gid):
    logging.debug('GID:'+str(gid))
    # dealing with all lights, use group 0
    api_url='http://'+Home.bridgeIP+'/api/'+Home.bridgeUN+'/groups/'+str(gid)+'/action'
    # turn off all the lights in the house with a slow trasition
    payload = {'on': False,'transitiontime': 100}
    r = requests.put(api_url, data=json.dumps(payload))
    logging.debug(r.text)
    if 'error' in r.text:
      logging.error(r.text)

  def groupLightsOn (self, gid):
    logging.debug('GID:'+str(gid))
    # dealing with all lights, use group 0
    api_url='http://'+Home.bridgeIP+'/api/'+Home.bridgeUN+'/groups/'+str(gid)+'/action'
    # turn off all the lights in the house with a slow trasition
    payload = {'on': True,'transitiontime': 100}
    r = requests.put(api_url, data=json.dumps(payload))
    logging.debug(r.text)
    if 'error' in r.text:
      logging.error(r.text)
    logging.debug('END')

  def singleLightCountdown(self, light, transTime ):
    logging.debug('light:'+str(light)+' transtime:'+str(transTime))
    api_url='http://'+Home.bridgeIP+'/api/'+Home.bridgeUN+'/lights/'+light+'/state'
    payload = {'on': False,'transitiontime': transTime}
    r = requests.put(api_url, data=json.dumps(payload))
    logging.debug(r.text)
    if 'error' in r.text:
      logging.error(r.text)
    time.sleep(transTime/10)
    logging.debug('END')

  def setCountdownLights (self, group, color, alert):
    logging.debug('group:'+str(group))
    api_url='http://'+Home.bridgeIP+'/api/'+Home.bridgeUN+'/groups/'+group+'/action'
    if color == "blue":
#blue      hue=47125
      hue=47125 
      transTime=30
    else:
      hue=64978
      transTime=10
    payload = {'on': True, 'bri': 254, 'hue': hue, 'sat': 254, 'transitiontime': transTime}
    r = requests.put(api_url, data=json.dumps(payload))
    logging.debug(r.text)
    if 'error' in r.text:
      logging.error(r.text)
    if alert:
      time.sleep(.1)
      payload = {'on': True, 'bri': 254, 'hue': 64978, 'sat': 254, 'alert': "select"}
      r = requests.put(api_url, data=json.dumps(payload))
      logging.debug(r.text)
      if 'error' in r.text:
        logging.error(r.text)
    time.sleep(1)
    logging.debug('END')

  def saveLightState (self, sid):
    # saves the current light state of the lights in the scene
    logging.debug('sid:'+str(sid))
    api_url = 'http://'+Home.bridgeIP+'/api/'+Home.bridgeUN+'/scenes/'+sid
    tempName = 'saveState_'+time.strftime('%a-%H-%M-%S')
    logging.debug('saveLightState: tempName='+tempName)
    payload = {'name':tempName, "storelightstate": True} 
    r = requests.put(api_url, data=json.dumps(payload))
    logging.debug(r.text)

  def getLightSchedule (self, id):
    # saves the current light state of the lights in the scene
    logging.debug('id:'+str(id))
    api_url = 'http://'+Home.bridgeIP+'/api/'+Home.bridgeUN+'/schedules/'+str(id)
    r = requests.get(api_url)
    json_str = json.dumps(r.json())
    json_objects = json.loads(json_str)
    logging.debug('END')
    return json_objects

  def setLightScheduleStatus (self, id, status):
    # saves the current light state of the lights in the scene
    logging.debug('id:'+str(id)+' status:'+str(status))
    api_url = 'http://'+Home.bridgeIP+'/api/'+Home.bridgeUN+'/schedules/'+str(id)
    payload = payload = {'status': status} 
    r = requests.put(api_url, data=json.dumps(payload))
    logging.debug(r.text)
    logging.debug('myhouse.setLightSchedules: END')

  def setLightScheduleTime (self, id, time):
    # saves the current light state of the lights in the scene
    logging.debug('id:'+str(id)+' time:'+str(time))
    api_url = 'http://'+Home.bridgeIP+'/api/'+Home.bridgeUN+'/schedules/'+str(id)
    payload = payload = {'localtime': "W127/T"+str(time)} 
    r = requests.put(api_url, data=json.dumps(payload))
    logging.debug(r.text)
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
      api_url='http://'+Home.bridgeIP+'/api/'+Home.bridgeUN+'/lights/'+str(light['light'])+'/state/'
      r = requests.put(api_url, data=json.dumps(payload))
      logging.debug(r.text)
      if 'error' in r.text:
        logging.error(r.text)
    # update movie temp scene with the blubs that should be on
    api_url='http://'+Home.bridgeIP+'/api/'+Home.bridgeUN+'/scenes/'+sid
    payload = {'lights':lightList, "storelightstate": True}
    r = requests.put(api_url, data=json.dumps(payload))
    logging.debug(r.text)
    if 'error' in r.text:
      logging.error(r.text)
    logging.debug('END')

  def SetQuickTrans(self, scene):
    logging.debug('scene'+scene)
    self.setTransTimeOfScene(Home.private.get('Scenes', scene), 10)
    time.sleep(.5)
    logging.debug('END')

  def getWeather(self):
    logging.debug('myhouse.getWeather')
    api_url='http://api.wunderground.com/api/9a995caa21869c46/conditions/q/20170.json'
    r = requests.get(api_url)
    json_str = json.dumps(r.json())
    json_objects = json.loads(json_str)
    logging.debug('myhouse.getWeather: END')
    return json_objects

  def pullDVRList(self):
    api_url='http://192.168.1.250:6544/Dvr/GetUpcomingList?'
    r = requests.get(api_url)
    if r.status_code == 200:
        with open("upcomingPrograms.xml", 'wb') as f:
            for chunk in r:
                f.write(chunk)

  # today = 0, tomorrow = 1, next = 2 so on , max like 18
  def getDVRshows(self, day_num):
    logging.debug('START')
    showlist= {}

    now = datetime.datetime.now()
    dayAdjust = now + timedelta(days=day_num)
    target = dayAdjust.strftime('%Y-%m-%d')


    from_zone = tz.gettz('UTC')
    to_zone = tz.gettz('America/New_York')
    root = ET.parse("upcomingPrograms.xml").getroot()
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


