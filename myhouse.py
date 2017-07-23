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

private = ConfigParser.RawConfigParser()
private.read('/home/host/home_auto_scripts/private.ini')

bridgeIP = private.get('Bridge','ip')
bridgeUN = private.get('Bridge','username')

hvacIP = private.get('hvac', 'ip')
hvacPort = private.get('hvac', 'port')

public = ConfigParser.RawConfigParser()
public.read('/home/host/home_auto_scripts/public.ini')



logging.config.fileConfig('/home/host/home_auto_scripts/logging.ini')
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
#logging.getLogger("pyInfinitude".setLevel(logging.WARNING)

class Home:

  def kevo(self, command):
    logging.debug('command:'+str(command))
    username = private.get('Kevo','username')
    password = private.get('Kevo','password')
    Door = pyKevo.pyKevo(username,password)
    Door.connect()
    if command == "status":
      return Door.lockState()
    elif command == "info":
      return Door.returnLockInfo()
    elif command == "lock":
      Door.lockLock()
      logging.info(command+' Door')
      return "check"
    elif command == "unlock":
      Door.unlockLock()
      logging.info(command+' Door')
      return "check"
    else:
      logging.info(command+' Door')
      return "error"


  def setTransTimeOfScene(self, sid, transtime):
    logging.debug('SID:'+str(sid)+' transtime:'+str(transtime))
    # get the current light states in the scene to update transition times
    api_url='http://'+bridgeIP+'/api/'+bridgeUN+'/scenes/'+sid
    r = requests.get(api_url)
    json_str = json.dumps(r.json())
    json_objects = json.loads(json_str)
    for lights in json_objects['lightstates'].iteritems():
      lights[1]['transitiontime'] = int(transtime)
      api_url='http://'+bridgeIP+'/api/'+bridgeUN+'/scenes/'+sid+'/lightstates/'+lights[0]
      payload = lights[1]
      r = requests.put(api_url, data=json.dumps(payload))
      logging.debug(r.text)
      if 'error' in r.text:
        logging.error(r.text)
    logging.debug('END')


  def setBringhtOfScene(self, sid, bri):
    logging.debug('SID:'+str(sid)+' bri:'+str(bri))
    # get the current light states in the scene to update transition times
    api_url='http://'+bridgeIP+'/api/'+bridgeUN+'/scenes/'+sid
    r = requests.get(api_url)
    json_str = json.dumps(r.json())
    json_objects = json.loads(json_str)
    for lights in json_objects['lightstates'].iteritems():
      lights[1]['bri'] = int(bri)
      api_url='http://'+bridgeIP+'/api/'+bridgeUN+'/scenes/'+sid+'/lightstates/'+lights[0]
      payload = lights[1]
      r = requests.put(api_url, data=json.dumps(payload))
      logging.debug(r.text)
      if 'error' in r.text:
        logging.error(r.text)
    logging.debug('END')

  def playScene(self, sid, gid):
    for key, value in private.items('Scenes'):
      if value == sid:
        logging.info(key)
    # dealing with all lights, use group 0
    api_url='http://'+bridgeIP+'/api/'+bridgeUN+'/groups/'+str(gid)+'/action'
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
    api_url='http://'+bridgeIP+'/api/'+bridgeUN+'/groups/'+str(gid)+'/action'
    # turn off all the lights in the house with a slow trasition
    payload = {'on': False,'transitiontime': 100}
    r = requests.put(api_url, data=json.dumps(payload))
    logging.debug(r.text)
    if 'error' in r.text:
      logging.error(r.text)

  def groupLightsOn (self, gid):
    logging.debug('GID:'+str(gid))
    # dealing with all lights, use group 0
    api_url='http://'+bridgeIP+'/api/'+bridgeUN+'/groups/'+str(gid)+'/action'
    # turn off all the lights in the house with a slow trasition
    payload = {'on': True,'transitiontime': 100}
    r = requests.put(api_url, data=json.dumps(payload))
    logging.debug(r.text)
    if 'error' in r.text:
      logging.error(r.text)
    logging.debug('END')

  def singleLightCountdown(self, light, transTime ):
    logging.debug('light:'+str(light)+' transtime:'+str(transTime))
    api_url='http://'+bridgeIP+'/api/'+bridgeUN+'/lights/'+light+'/state'
    payload = {'on': False,'transitiontime': transTime}
    r = requests.put(api_url, data=json.dumps(payload))
    logging.debug(r.text)
    if 'error' in r.text:
      logging.error(r.text)
    time.sleep(transTime/10)
    logging.debug('END')

  def setCountdownLights (self, group, color, alert):
    logging.debug('group:'+str(group))
    api_url='http://'+bridgeIP+'/api/'+bridgeUN+'/groups/'+group+'/action'
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
    api_url = 'http://'+bridgeIP+'/api/'+bridgeUN+'/scenes/'+sid
    tempName = 'saveState_'+time.strftime('%a-%H-%M-%S')
    logging.debug('saveLightState: tempName='+tempName)
    payload = {'name':tempName, "storelightstate": True} 
    r = requests.put(api_url, data=json.dumps(payload))
    logging.info(r.text)

  def getLightSchedule (self, id):
    # saves the current light state of the lights in the scene
    logging.debug('id:'+str(id))
    api_url = 'http://'+bridgeIP+'/api/'+bridgeUN+'/schedules/'+str(id)
    r = requests.get(api_url)
    json_str = json.dumps(r.json())
    json_objects = json.loads(json_str)
    logging.debug('END')
    return json_objects

  def setLightScheduleStatus (self, id, status):
    # saves the current light state of the lights in the scene
    logging.debug('id:'+str(id)+' status:'+str(status))
    api_url = 'http://'+bridgeIP+'/api/'+bridgeUN+'/schedules/'+str(id)
    payload = payload = {'status': status} 
    r = requests.put(api_url, data=json.dumps(payload))
    logging.info(r.text)
    logging.debug('myhouse.setLightSchedules: END')

  def setLightScheduleTime (self, id, time):
    # saves the current light state of the lights in the scene
    logging.debug('id:'+str(id)+' time:'+str(time))
    api_url = 'http://'+bridgeIP+'/api/'+bridgeUN+'/schedules/'+str(id)
    payload = payload = {'localtime': "W127/T"+str(time)} 
    r = requests.put(api_url, data=json.dumps(payload))
    logging.info(r.text)
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
      api_url='http://'+bridgeIP+'/api/'+bridgeUN+'/lights/'+str(light['light'])+'/state/'
      r = requests.put(api_url, data=json.dumps(payload))
      logging.debug(r.text)
      if 'error' in r.text:
        logging.error(r.text)
    # update movie temp scene with the blubs that should be on
    api_url='http://'+bridgeIP+'/api/'+bridgeUN+'/scenes/'+sid
    payload = {'lights':lightList, "storelightstate": True}
    r = requests.put(api_url, data=json.dumps(payload))
    logging.info(r.text)
    if 'error' in r.text:
      logging.error(r.text)
    logging.debug('END')

  def SetQuickTrans(self, scene):
    logging.debug('scene'+scene)
    self.setTransTimeOfScene(private.get('Scenes', scene), 10)
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

  def getDVRToday(self):
    logging.debug('myhouse.getDVRtoday')
    showlist= {}
    api_url='http://192.168.1.250:6544/Dvr/GetUpcomingList?'
    now = datetime.datetime.now()
    today = now.strftime('%Y-%m-%d')
    from_zone = tz.gettz('UTC')
    to_zone = tz.gettz('America/New_York')
    r = requests.get(api_url)
    if r.status_code == 200:
        with open("upcomingPrograms.xml", 'wb') as f:
            for chunk in r:
                f.write(chunk)
    root = ET.parse("upcomingPrograms.xml").getroot()
    for programlist in root.iter('ProgramList'):
        for program in programlist.iter('Programs'):
            x=1
            for show in program.findall('Program'):
                showStart = show.find('StartTime').text
                utc = datetime.datetime.strptime(showStart, '%Y-%m-%dT%H:%M:%SZ')
                utc = utc.replace(tzinfo=from_zone)
                if  utc.astimezone(to_zone).strftime('%Y-%m-%d') == today:
                    starttime = utc.astimezone(to_zone).strftime('%H:%M:%S')
                    title = show.find('Title').text
                    subtitle = show.find('SubTitle').text
                    for entry in program.iter('Recording'):
                        recordID = entry.find('RecordedId').text
                        status =  entry.find('Status').text
                    oneshow = {'starttime':starttime, 'title':title, 'subtitle':subtitle, 'RecordedID':recordID, 'Status':status}
		    showlist['show_'+str(x)] = oneshow
                    logging.debug('myhouse.getDVRToday: found: '+str(oneshow['title']))
                    x=x+1
    logging.debug('myhouse.getDVRToday: END')
    return json.dumps(showlist)



  def getHVACmode(self):
    api_url='http://'+str(hvacIP)+':'+str(hvacPort)+'/api/config/mode'
    r = requests.get(api_url)
    json_str = json.dumps(r.json())
    json_objects = json.loads(json_str)
    logging.debug('myhouse.getHVACmode: END')
    return json_objects['data']

  def getHVACvacaData(self):
    logging.debug('myhouse.getHVACvacaData')
    d = {}
    vacaData = [ 'vacmaxt', 'vacmint', 'vacfan' ]
    for setting in vacaData:
      api_url='http://'+str(hvacIP)+':'+str(hvacPort)+'/api/config/'+setting
      r = requests.get(api_url)
      json_str = json.dumps(r.json())
      json_objects = json.loads(json_str)
      d[setting] = json_objects['data']
    logging.debug('myhouse.getHVACvacaData: END')
    return d

  def getHVACzonedata(self):
    logging.debug('myhouse.getHVACzonedata')
    api_url='http://'+str(hvacIP)+':'+str(hvacPort)+'/api/config/zones'
    try:
      r = requests.get(api_url)
    except:
      logging.error('myhouse.getHVACzonedata: request error')
      return "Error"
    else:
      if 'error' in r.text:
        logging.error(r.text)
        return "Error";
      json_str = json.dumps(r.json())
      json_objects = json.loads(json_str)
      todayNum = (int(datetime.datetime.today().weekday())+1)
      logging.debug('myhouse.getHVACzonedata: END')
      return json_objects

  def getHVACstatus(self):
    logging.debug('myhouse.getHVACstatus')
    api_url='http://'+str(hvacIP)+':'+str(hvacPort)+'/status.json'
    try:
      r = requests.get(api_url)
    except:
      logging.error('myhouse.getHVACstatus: request error')
      return "Error"
    else:
      if 'error' in r.text:
        logging.error(r.text)
        return "Error";
      json_str = json.dumps(r.json())
      json_objects = json.loads(json_str)
      logging.debug('myhouse.getHVACstatus: END')
      return json_objects


  def setHVACprofile(self, until, profile):
#    minute = (now.minute // 15+1)*15
#    adjT = now.replace(minute=0, second=0)+datetime.timedelta(minutes=minute)
#    until = adjT.strftime("%H:%M")
    api_url='http://'+str(hvacIP)+':'+str(hvacPort)+'/api/1/hold?activity='+profile+'&until="'+until+'"'
    current_activity = public.get('hvac_current', 'currentActivity')
    if current_activity !=  profile :
      logging.info('myhouse.setHVACprofile: '+profile)
#    public.set('hvac_current', "currentActivity", profile)
#    public.set('hvac_current', "hold_time", until)
#    public.set('hvac_current', "hold", 'on')
    with open(r'/home/host/home_auto_scripts/public.ini', 'wb') as configfile:
      public.write(configfile)
    r = requests.get(api_url)
    logging.debug(r)
    logging.debug('myhouse.setHVACprofile: END')

  def setHVACzonedata(self, payload):
    logging.debug('myhouse.setHVACzonedata')
    api_url='http://'+str(hvacIP)+':'+str(hvacPort)+'/api/config/zones'
    payload = lights[1]
    r = requests.put(api_url, data=json.dumps(payload))
    logging.info(r.text)

  def setHVACmanual(self, temp):
    ct = float(public.get('hvac_current', 'rt'))
    temp = float(temp)
    if ct > temp:
      logging.debug('myhouse.setHVACmanual: '+str(ct)+" > "+str(temp))
      clsp = temp
      htsp = temp - 3
    elif ct < temp:
      logging.debug('myhouse.setHVACmanual: '+str(ct)+" < "+str(temp))
      clsp = temp + 3
      htsp = temp 
    else:
      clsp = temp
      htsp = temp
    logging.info('myhouse.setHVACmanual: temp:'+str(temp)+' clsp:'+str(clsp)+' htsp:'+str(htsp))
    api_url = 'http://'+str(hvacIP)+':'+str(hvacPort)+'/api/1/activity/manual?clsp='+str(clsp)+'&htsp='+str(htsp)
    r = requests.get(api_url)
    logging.debug(r)
