import time, datetime
import sys, getopt, os, random, subprocess
import myhouse
import pyInfinitude.pyInfinitude
import logging
from decimal import Decimal
from subprocess import call

##########################
# HUE Light scene change #
def triggerSceneChange (z, tag, i, g):
  logging.debug('ZONE '+str(z)+' TAG '+str(tag)+' SID '+str(i)+' GID '+str(g))
  logging.info('Zone'+str(z)+' '+str(tag)+'_'+str(i))
  if 'evening' in tag:
    home.setTransTimeOfScene(home.private.get('HueScenes', 'zone'+str(z)+'_'+str(tag)+'_'+str(i)), home.public.get('zone'+str(z), str(tag)+'_trans_time'))
  else:
    home.setTransTimeOfScene(home.private.get('HueScenes', 'zone'+str(z)+'_'+str(tag)+'_'+str(i)), home.public.get('zone'+str(z), str(tag)+'_'+str(i)+'_trans_time'))

  time.sleep(.2)
  home.playScene(home.private.get('HueScenes', 'zone'+str(z)+'_'+str(tag)+'_'+str(i)),str(g))

  time.sleep(.2)
  # reset transiton times to fast
  home.setTransTimeOfScene(home.private.get('HueScenes', 'zone'+str(z)+'_'+str(tag)+'_'+str(i)), 40)

  cs = home.public.get('zone'+str(z),'currentscene')
  home.public.set('zone'+str(z),'currentscene', str(tag)+'_'+str(i))
  logging.debug('zone'+str(z)+' current scene set to '+str(tag)+'_'+str(i))
  home.public.set('zone'+str(z), 'previousscene', cs)
  logging.debug('previous scene set to '+cs)
  home.saveSettings()

#####################################
# Determine the Hue Tansition Times #
def calculateEvenings(z, howmany):

  # if auto run is off calculate transition times
  # 3,600,000/100 = 36000ms = 1 hour
  # 18000 = 30 minutes
  # 27000 = 45 minutes
  logging.debug('z '+str(z)+' thismany '+str(howmany))

  # if calculate is called and the time is before default start, use default start time to calculate

  if len(sys.argv) > 1:
    fst = home.public.get('zone'+str(z),'evening_first_time').split(':')
    logging.debug('FST: '+str(fst))
    calcNow = now.replace(hour=int(fst[0]), minute=int(fst[1]), second=int(fst[2]))
  else:
    calcNow = now

  # read in last scene trigger (lst) time in from config file
  lst = home.public.get('zone'+str(z),'last_time').split(':')
  logging.debug('LST: '+str(lst))
  diff = (datetime.datetime.today().replace(hour=int(lst[0]), minute=int(lst[1]), second=int(lst[2]))) - calcNow
  # time to next scene (ttns)
  ttns=diff/howmany
  # transition time (tt) should be 60% of the ttns, and then converted into 100's of mili seconds
  tp = (float(home.public.get('Time', 'trans_percent'))/100)
  tt = int(((int(ttns.total_seconds())*tp)*1000)/100)

  # max time allowed by hue lights, it will fail to set otherwise, i think this is 1.5 hours
  if tt > 65535:
    tt = 65543

  logging.debug('transition time calculated is: '+str(tt))

  if z in (0,1):
    home.public.set('zone'+str(z),'evening_0_on_time', calcNow.time().strftime("%H:%M:%S"))
    home.public.set('zone'+str(z),'evening_1_on_time', (calcNow+diff).time().strftime("%H:%M:%S"))
    home.public.set('zone'+str(z),'evening_trans_time', tt)
  else:
    if howmany == 4:
      home.public.set('zone'+str(z),'evening_0_on_time', calcNow.time().strftime("%H:%M:%S"))
      home.public.set('zone'+str(z),'evening_1_on_time', (calcNow+ttns).time().strftime("%H:%M:%S"))
      home.public.set('zone'+str(z),'evening_2_on_time', (calcNow+(ttns*2)).time().strftime("%H:%M:%S"))
      home.public.set('zone'+str(z),'evening_3_on_time', (calcNow+(ttns*3)).time().strftime("%H:%M:%S"))
      home.public.set('zone'+str(z),'evening_4_on_time', (calcNow+diff).time().strftime("%H:%M:%S"))
      home.public.set('zone'+str(z),'evening_trans_time', tt)
    if howmany == 3:
      home.public.set('zone'+str(z),'evening_0_on_time', 'null')
      home.public.set('zone'+str(z),'evening_1_on_time', calcNow.time().strftime("%H:%M:%S"))
      home.public.set('zone'+str(z),'evening_2_on_time', (calcNow+(ttns*2)).time().strftime("%H:%M:%S"))
      home.public.set('zone'+str(z),'evening_3_on_time', (calcNow+(ttns*3)).time().strftime("%H:%M:%S"))
      home.public.set('zone'+str(z),'evening_4_on_time', (calcNow+diff).time().strftime("%H:%M:%S"))
      home.public.set('zone'+str(z),'evening_trans_time', tt)
    if howmany == 2:
      home.public.set('zone'+str(z),'evening_0_on_time', 'null')
      home.public.set('zone'+str(z),'evening_1_on_time', 'null')
      home.public.set('zone'+str(z),'evening_2_on_time', calcNow.time().strftime("%H:%M:%S"))
      home.public.set('zone'+str(z),'evening_3_on_time', (calcNow+(ttns)).time().strftime("%H:%M:%S"))
      home.public.set('zone'+str(z),'evening_4_on_time', (calcNow+diff).time().strftime("%H:%M:%S"))
      home.public.set('zone'+str(z),'evening_trans_time', tt)
    if howmany == 1:
      home.public.set('zone'+str(z),'evening_0_on_time', 'null')
      home.public.set('zone'+str(z),'evening_1_on_time', 'null')
      home.public.set('zone'+str(z),'evening_2_on_time', 'null')
      home.public.set('zone'+str(z),'evening_3_on_time', (calcNow+(ttns)).time().strftime("%H:%M:%S"))
      home.public.set('zone'+str(z),'evening_4_on_time', (calcNow+diff).time().strftime("%H:%M:%S"))
      home.public.set('zone'+str(z),'evening_trans_time', tt)

  home.saveSettings()


########
# MAIN #
########
def main(argv):
  logging.debug('Running Main()')

  # Monday is 0 and Sunday is 6.
  today = now.today().weekday()

# ********
# CAPABILITY PORTED OVER
# ********
  ###########
  # DropBox #
  if home.private.getboolean('Devices','dropbox'):
    if home.isDropboxRunning():
     logging.debug("Dropbox is running")
    else:
     logging.warning("Dropbox isn't running")
     os.system("python3 ~/dropbox.py start >> ~/home_auto_scripts/home-auto.log 2>&1")

  ################################
  # Clean up watch directories #
  call(["find", home.private.get('Path','watch_dir'), "-type", "f", "-name", "*.txt", "-exec", "rm", "{}", "+"])

# ********
# CAPABILITY PORTED OVER
# ********
  ####################
  # Pull Wemo Status #
  if home.private.getboolean('Devices', 'wemo'):
    home.updateWemo()

# ********
# CAPABILITY PORTED OVER
# ********
  ######################
  # Pull hue schedules #
  ######################
  if home.private.getboolean('HueBridge', 'alarm_use'):
    lightSchedule = home.getLightSchedule( int(home.private.get('HueSchedules', 'alarm_work')));
    home.public.set('wakeup_schedule', 'work_localtime', lightSchedule['localtime']) 
    home.public.set('wakeup_schedule', 'work_status', lightSchedule['status']) 
    lightSchedule = home.getLightSchedule( int(home.private.get('HueSchedules', 'alarm_weekend')));
    home.public.set('wakeup_schedule', 'weekend_localtime', lightSchedule['localtime']) 
    home.public.set('wakeup_schedule', 'weekend_status', lightSchedule['status']) 
    home.saveSettings()

  ###########################
  # global morning settings #
  ###########################

  # if choseing to use hue schedule as the way to set global morning values
  if home.private.getboolean('HueBridge', 'alarm_use'):
    if today in range(5):
      wm = home.public.get('wakeup_schedule','work_localtime').split("T",1)[1]
    else:
      wm = home.public.get('wakeup_schedule','weekend_localtime').split("T",1)[1]
    if wm != 'null':
      logging.debug('we have a wake up morning time')
      wake_morning = datetime.datetime.strptime(wm, '%H:%M:%S').time()
      home.public.set('mornings', str(today)+'_morning', wake_morning)
      home.saveSettings()
      global_morning = datetime.datetime.strptime(str(home.public.get('mornings', str(today)+'_morning')),'%H:%M:%S')
      # make the morning triggers 10 minutes before global to allow fades
      #hue schedule already sets time back for fade in
      newMorning = (global_morning + datetime.timedelta(minutes=10)).time()
      newDaytime = (global_morning + datetime.timedelta(hours=1)).time()
  else :
      # define all morning times based off global morning value
      global_morning = datetime.datetime.strptime(str(home.public.get('mornings', str(today)+'_morning')),'%H:%M:%S')
      # make the morning triggers 10 minutes before global to allow fades
      newMorning = (global_morning + datetime.timedelta(minutes=10)).time()
      newDaytime = (global_morning + datetime.timedelta(hours=1)).time()
      # check and set morning light alarm clock
      if today in range(5):
        wm = home.public.get('wakeup_schedule','work_localtime').split("T",1)[1]
      else:
        wm = home.public.get('wakeup_schedule','weekend_localtime').split("T",1)[1]
      if wm != 'null':
        wake_Morning = datetime.datetime.strptime(wm, '%H:%M:%S').time()
        if newMorning != wake_Morning:
          # set bedroom wake schedule in HUE app
          home.setLightScheduleTime(1,newMorning)
  logging.debug("Global Morning is: "+global_morning.strftime("%H:%M:%S"))

# ********
# CAPABILITY IGNORED
# ********
  ####################
  # Pull KEVO Status #
  ####################
  if home.private.getboolean('Devices', 'kevo'):
    prevLock = home.public.get('lock', 'status')
    try:
      home.public.set('lock', 'status', home.kevo("status"))
      home.saveSettings()
    except: 
      logging.error('Lock status set error')
    currentLock = home.public.get('lock', 'status')
    if prevLock != currentLock:
      logging.info('Lock changed from '+prevLock+' to '+currentLock)

# ********
# CAPABILITY IGNORED
# ********
  ############################
  # Pull TV shows for 7 days #
  ############################
  if home.private.getboolean('Devices', 'dvr'):
    home.pullDVRupcoming()
    for x in range(0,8):
      home.public.set('dvr', str(x)+'_shows', home.getDVRshows(x, home.upFile))
    home.pullDVRrecorded()
    home.public.set('dvrRecorded', 'shows', home.getDVRshows(0, home.recFile))


  ########################
  # Pull Current Weather #
  ########################
  if home.private.getboolean('Devices', 'weather'):
    weatherdata = home.getWeather();
    if weatherdata != "error":
      if 'current_observation' in weatherdata:
        home.public.set('weather', 'weather', weatherdata['current_observation']['weather']) #mostly cloudy
        home.public.set('weather', 'icon', weatherdata['current_observation']['icon'])
        home.public.set('weather', 'icon_url', weatherdata['current_observation']['icon_url'])
        home.public.set('weather', 'oh', weatherdata['current_observation']['relative_humidity'].replace('%',''))
        home.public.set('weather', 'ot', weatherdata['current_observation']['temp_f'])
        home.public.set('weather', 'forecast_url', weatherdata['current_observation']['forecast_url'])

  ##################
  # Pull HVAC Data #
  ##################
  # pull configuation file from hvac and set home.public ini file for web interface
  if home.private.getboolean('Devices', 'hvac'):
    # HVAC settings set below for wake and home
    # make the home profile trigger 1.5hrs after morning
    newHome = (global_morning + datetime.timedelta(hours=1, minutes=30)).time()

    for s in range(0,home.private.getint('HVAC', 'total')):

      hvacIP = home.private.get('HVAC_'+str(s), 'ip')
      hvacPort = home.private.get('HVAC_'+str(s), 'port')
      hvacFile = home.private.get('Path','hvac')+'/'+home.private.get('HVAC_'+str(s), 'file')
      hvacStatus = home.private.get('Path','hvac')+'/'+home.private.get('HVAC_'+str(s), 'status')
      sys_name = home.public.get('hvac_'+str(s), 'name')
      hvac = pyInfinitude.pyInfinitude.infinitude(hvacIP,hvacPort,hvacFile, hvacStatus)

      if not hvac.pullConfig():
        home.public.set('hvac_'+str(s),'status','error')
      else:
        home.public.set('hvac_'+str(s),'status','ok')
        zone = int(home.private.get('HVAC_'+str(s), 'zone'))
        # adjust days of week num to allign with carrier and infinitude numbering
        for day in range(0,7):
          # nullify each value because if there is no value it will be blank
          for period in range(0,5):
            home.public.set('hvac_'+str(s), "day_"+str(day)+"_event_"+str(period)+"_on_time", 'null')
            home.public.set('hvac_'+str(s), "day_"+str(day)+"_event_"+str(period)+"_activity", 'null')
          # pull out all hvac activity and times for schedule, insert it into config file
            if hvac.get_zone_program_day_period_enabled(zone, day, period) == 'on':
              home.public.set('hvac_'+str(s), "day_"+str(day)+"_event_"+str(period)+"_on_time", hvac.get_zone_program_day_period_time(zone, day, period)) 
              home.public.set('hvac_'+str(s), "day_"+str(day)+"_event_"+str(period)+"_activity", hvac.get_zone_program_day_period_activity(zone, day, period)) 
        # get the HVAC mode
        home.public.set('hvac_'+str(s),'mode', hvac.get_mode());
        # pull out clsp and htsp for each profile name
        # id: 0 = home, 1 = away, 2 = sleep, 3 = wake, 4 = manual
        for id in range(0,5):
          profile = hvac.get_zone_activity_name(zone, id)
          home.public.set('profile_current_'+str(s), profile+'_fan', hvac.get_zone_activity_fan(zone, id))
          home.public.set('profile_current_'+str(s), profile+'_clsp', hvac.get_zone_activity_clsp(zone, id))
          home.public.set('profile_current_'+str(s), profile+'_htsp', hvac.get_zone_activity_htsp(zone, id))
        # get the vacation data too
        home.public.set('profile_current_'+str(s),'vacmaxt', hvac.get_vacmaxt())
        home.public.set('profile_current_'+str(s),'vacmint', hvac.get_vacmint())
        home.public.set('profile_current_'+str(s),'vacfan', hvac.get_vacfan())
        # find if hvac has a wake profile actively set and set it to be inline with global morning
        # today only
        day = (int(datetime.datetime.today().weekday())+1)
        change=False
        if day == 7:
          day = 0
        logging.debug("DAY "+str(day))
        for period in range(0,5):
          if home.public.get('hvac_'+str(s), 'day_'+str(day)+'_event_'+str(period)+'_activity') == 'wake':
            hm = home.public.get('hvac_'+str(s), 'day_'+str(day)+'_event_'+str(period)+'_on_time')
            logging.debug('hm = '+'hvac_'+str(s)+', day_'+str(day)+'_event_'+str(period)+'_on_time  '+hm)
            hvac_Morning = datetime.datetime.strptime(hm, '%H:%M').time()
            logging.debug("WAKE COMPARE "+ hvac_Morning.strftime("%m/%d/%Y, %H:%M:%S") + " != " + newMorning.strftime("%m/%d/%Y, %H:%M:%S"))
            if hvac_Morning != newMorning:
              logging.info("S("+str(s)+") Adjusting "+sys_name+" WAKE profile to "+str(newMorning)+' d '+str(day))
              hvac.set_zone_program_day_period_time(zone, day, period, newMorning.strftime('%H:%M'))
              change=True
        # check and set todays home profile to be after wake
        for period in range(0,5):
          if home.public.get('hvac_'+str(s), 'day_'+str(day)+'_event_'+str(period)+'_activity') == 'home':

            hm = home.public.get('hvac_'+str(s), 'day_'+str(day)+'_event_'+str(period)+'_on_time')
            hvac_home = datetime.datetime.strptime(hm, '%H:%M').time()
            logging.debug("HOME COMPARE "+ hvac_Morning.strftime("%m/%d/%Y, %H:%M:%S") + " != " + newMorning.strftime("%m/%d/%Y, %H:%M:%S"))
            if hvac_home != newHome:
              logging.info("S("+str(s)+") Adjusting "+sys_name+" HOME profile to "+str(newHome)+' d '+str(day))
              hvac.set_zone_program_day_period_time(zone, day, period, newHome.strftime('%H:%M'))
              # make the hvac change
              change=True
        if change:
          if not hvac.pushConfig():
            logging.error('pushConfig failed')


  ###############################
  # Configure Vacation Settings #
  # check and see if you are on vacation and configure
  if home.public.getboolean('settings', 'vacation'):
    home.public.set('settings','morning', 'false')
    home.public.set('settings','autorun', 'true')
    v_on = str(home.public.get('Time', 'vaca_on_time')).split(':')
    v_off = str(home.public.get('Time', 'vaca_off_time')).split(':')
    for z in (0,1,2):
      if z < 2:
        home.public.set('zone'+str(z),'last_time', str(home.public.get('Time', 'vaca_off_time')))
      home.public.set('settings','zone'+str(z)+'_evening', 'true')
  else:
    for z in (0,1,2):
      home.public.set('zone'+str(z),'last_time', home.public.get('zone'+str(z),'default_last_time'))

  #######################
  # PULL Current Scenes #
  cs = []
  for z in (0,1,2):
    logging.debug('pull current scene zone:'+str(z))
    cs.append(home.public.get('zone'+str(z),'currentscene'))


  # set Morning and daytime start
  for z in (0,1):
    home.public.set('zone'+str(z),'morning_0_on_time', newMorning)
    home.public.set('zone'+str(z),'morning_0_trans_time', 100)
    home.public.set('zone'+str(z),'daytime_0_on_time', newDaytime)
    home.public.set('zone'+str(z),'daytime_0_trans_time', 18000)
    logging.debug('zone'+str(z)+' setting morning start: '+str(newMorning))
    logging.debug('zone'+str(z)+' setting daytime start: '+str(newDaytime))
    home.saveSettings()


  ####################
  # AUTO RUN SECTION #
  ####################

  # if auto run is on do auto run stuff
  if home.public.getboolean('settings', 'autoRun'):

    ##########################################
    # Wemo Device CONTROL                    #
    # these devices are on the same schedule #
    if home.private.getboolean('Devices', 'wemo'):
      # if vacation mode is false check the time
      if not home.public.getboolean('settings', 'vacation'):
        #list each device to trigger in this schedule
        # 1 = lava lamp
        for i in [1,5]:
          if home.private.getboolean('Wemo', 'wdevice'+str(i)+'_active'):
            d1_on = str(home.public.get('wemo', 'wdevice'+str(i)+'_on_time')).split(':')
            d1_off = str(home.public.get('wemo', 'wdevice'+str(i)+'_off_time')).split(':')
            if int(d1_off[1]) < 11:
              d1_off[0] = str(int(d1_off[0])-1)
              d1_off[1] = str(49 + int(d1_off[1]))
            if int(d1_on[1]) < 11:
              d1_on[0] = str(int(d1_on[0])-1)
              d1_on[1] = str(49 + int(d1_on[1]))
            logging.debug('COMPARE wemo device'+str(i)+': '+d1_on[0]+':'+d1_on[1]+':'+d1_on[2]+' <= now <= '+d1_on[0]+':'+str(int(d1_on[1])+2)+':'+d1_on[2])
            if now.replace(hour=int(d1_on[0]), minute=int(d1_on[1]), second=int(d1_on[2])) <= now <= now.replace(hour=int(d1_on[0]), minute=int(d1_on[1])+10, second=int(d1_on[2])):
              logging.debug("Should turn on wemo device "+str(i))
              home.triggerWemoDeviceOn(i)
            try:
              if home.public.getboolean('wemo', 'wdevice'+str(i)+'_status'):
                logging.debug('COMPARE wemo device'+str(i)+': '+d1_off[0]+':'+str(int(d1_off[1])-2)+':'+d1_off[2]+' <= now <= '+d1_off[0]+':'+d1_off[1]+':'+d1_off[2])
                if now.replace(hour=int(d1_off[0]), minute=int(d1_off[1])-10, second=int(d1_off[2])) <= now <= now.replace(hour=int(d1_off[0]), minute=int(d1_off[1]), second=int(d1_off[2])):
                  logging.debug("Should turn off wemo device "+str(i))
                  home.triggerWemoDeviceOff(i)
            except:
              logging.error('wdevice'+str(i)+'_status not found')



    # get the start time for all the scenes and zones
    m = []
    d = []
    e = []
    for z in (0,1,2):
      logging.debug('z:'+str(z))
      if z < 2: #zones 0 and 1 only have a single morning and daytime but 2 evenings
        m.append(str(home.public.get('zone'+str(z), 'morning_0_on_time')).split(':'))
        logging.debug('zone'+str(z)+' morning_'+str(z)+': '+str(m[z]))
        d.append(str(home.public.get('zone'+str(z), 'daytime_0_on_time')).split(':'))
        logging.debug('zone'+str(z)+' daytime_'+str(z)+': '+str(d[z]))
        et = []
        for t in (0,1):
          et.append(str(home.public.get('zone'+str(z), 'evening_'+str(t)+'_on_time')).split(':'))
        e.append(et)
        logging.debug('zone'+str(z)+' evening_'+str(z)+': '+str(e[z]))
      else: # zone three has 5 evenings
        et = []
        for t in (0,1,2,3,4):
          et.append(str(home.public.get('zone'+str(z), 'evening_'+str(t)+'_on_time')).split(':'))
        e.append(et)
        logging.debug('zone'+str(z)+' evening_'+str(z)+': '+str(e[z]))

    logging.debug('m:'+str(m))
    logging.debug('d:'+str(d))
    logging.debug('e:'+str(e))

    ################
    # MORNING MODE #
    # if morning scene is enabled
    # morning is appliacble to zones 0 and 1
    for z in (0,1):
      if cs[z] == 'null':
        if home.public.getboolean('settings', 'morning'):
          logging.debug('COMPARE zone'+str(z)+'_morning_'+str(0)+':'+str(m[z][0])+':'+str(m[z][1])+':'+str(m[z][2])+' < now < '+str(d[z][0])+':'+str(d[z][1])+':'+str(d[z][2]))
          if now.replace(hour=int(m[z][0]), minute=int(m[z][1]), second=int(m[z][2])) <= now <= now.replace(hour=int(d[z][0]), minute=int(d[z][1]), second=int(d[z][2])) :
            if z == 0: # trigger these events only once, not per zone
              if home.private.getboolean('Devices', 'wemo'):
                if home.private.getboolean('Wemo', 'wdevice2_active'):
                  home.triggerWemoDeviceOn(2)
                if home.private.getboolean('Wemo', 'wdevice4_active'):
                  home.triggerWemoDeviceOn(4)
                if home.private.getboolean('Wemo', 'wdevice5_active'):
                  home.triggerWemoDeviceOn(5)
                if home.private.getboolean('Wemo', 'wdevice6_active'):
                  home.triggerWemoDeviceOn(6)
                if home.private.getboolean('Wemo', 'wdevice7_active'):
                  home.triggerWemoDeviceOn(7)
              if home.private.getboolean('Devices','decora'):
                home.decora(home.private.get('Decora', 'switch_1'), 'ON', '50')
                home.decora(home.private.get('Decora', 'switch_4'), 'ON', '50')
              if home.private.getboolean('Devices','hue'):
                triggerSceneChange(z,'morning', 0, int(home.private.get("HueGroups",'zone'+str(z))))
            else:
              if home.private.getboolean('Devices','hue'):
                triggerSceneChange(z,'morning', 0, int(home.private.get("HueGroups",'zone'+str(z))))


    ################
    # DAYTIME MODE #
    # if morning scene is over and its before evening 1 on the main floor
    # only plays when cs is not null, ie. only when morning was kicked off or you come home
    for z in (0,1):
      if cs[z] != 'null':
        if home.public.getboolean('settings', 'daytime'):
          logging.debug('COMPARE zone'+str(z)+'_daytime_'+str(0)+':'+str(d[z][0])+':'+str(d[z][1])+':'+str(d[z][2])+' < now < '+str(e[z][0][0])+':'+str(e[z][0][1])+':'+str(e[z][0][2]))
          if now.replace(hour=int(d[z][0]), minute=int(d[z][1]), second=int(d[z][2])) <= now <= now.replace(hour=int(e[z][0][0]), minute=int(e[z][0][1]), second=int(e[z][0][2])) :
            logging.debug('COMPARE zone'+str(z)+'_daytime_'+str(0)+' CS['+str(z)+']='+str(cs[z])+':morning_0,home,null')
            if cs[z] in ('morning_0','home','null'):
              if z == 0: # trigger these events only once, not per zone
                if home.private.getboolean('Devices','hue'):
                  triggerSceneChange(z,'daytime', 0, int(home.private.get("HueGroups","zone"+str(z))))
                if home.private.getboolean('Devices','decora'):
                  home.decora(home.private.get('Decora', 'switch_4'), "OFF", "None")
              else:
                if home.private.getboolean('Devices','hue'):
                  triggerSceneChange(z,'daytime', 0, int(home.private.get("HueGroups","zone"+str(z))))
                if home.private.getboolean('Devices', 'wemo'):
                  if home.private.getboolean('Wemo', 'wdevice2_active'):
                    home.triggerWemoDeviceOn(2)
                  if home.private.getboolean('Wemo', 'wdevice4_active'):
                    home.triggerWemoDeviceOn(4)


    #################
    # VACATION MODE #
    # if its past the vacation on time turn on the lights and trigger the first scene
    if home.public.getboolean('settings', 'vacation'):
      if now.replace(hour=int(v_on[0]), minute=int(v_on[1]), second=int(v_on[2])) <= now <= now.replace(hour=int(v_off[0]), minute=int(v_off[1]), second=int(v_off[2])):
        if cs[z] == 'null':
          if home.private.getboolean('Devices','hue'):
            for z in (0,1):
              triggerSceneChange(z,'evening', 0, int(home.private.get("HueGroups","zone"+str(z))))


    #######################################
    # EVENING CYCLE MODE  ZONE0 and ZONE1 #
    # if i haven't said im going to bed then run evening mode
    # this evening mode is appliacble to zones 1 and 2

    for z in (0,1):
      if home.public.getboolean('settings', 'zone'+str(z)+'_evening'):
        for i in (0,1):
          if e[z][i] != ['null']:
            if i == 1:
              logging.debug('COMPARE zone'+str(z)+'_evening_'+str(i)+':'+str(e[z][i][0])+':'+str(e[z][i][1])+':'+str(e[z][i][2])+' < now ')
              if now.replace(hour=int(e[z][i][0]), minute=int(e[z][i][1]), second=int(e[z][i][2])) <= now :
                logging.debug('COMPARE zone'+str(z)+'_evening_'+str(i)+' CS['+str(z)+']='+str(cs[z])+':null,daytime_'+str(i-1)+',evening_'+str(i-1)+',home')
                if cs[z] in ('null','vaca_1','daytime_'+str(i-1),'evening_0','home'):
                  if cs[z] == 'null':
                    calculateEvenings(z,1)
                  if home.private.getboolean('Devices','decora'):
                    home.decora(home.private.get('Decora', 'switch_4'), "ON", "75")
                  if home.private.getboolean('Devices','hue'):
                    triggerSceneChange(z,'evening', i, int(home.private.get("HueGroups","zone"+str(z))))
            else:
              logging.debug('COMPARE zone'+str(z)+'_evening_'+str(i)+':'+str(e[z][i][0])+':'+str(e[z][i][1])+':'+str(e[z][i][2])+' < now < '+str(e[z][i+1][0])+':'+str(e[z][i+1][1])+':'+str(e[z][i+1][2]))
              if now.replace(hour=int(e[z][i][0]), minute=int(e[z][i][1]), second=int(e[z][i][2])) <= now <= now.replace(hour=int(e[z][i+1][0]), minute=int(e[z][i+1][1]), second=int(e[z][i+1][2])):
                logging.debug('COMPARE zone'+str(z)+'_evening_'+str(i)+' CS['+str(z)+']='+str(cs[z])+':null,daytime_'+str(i)+'evening_'+str(i-1)+',home')
                if cs[z] in ('null','vaca_1','daytime_'+str(i),'evening_'+str(i-1),'home'):
                  if cs[z] == 'null':
                    calculateEvenings(z,1)
                  if home.private.getboolean('Devices','wemo'):
                    if home.private.getboolean('Wemo', 'wdevice2_active'):
                      home.triggerWemoDeviceOn(2)
                    if home.private.getboolean('Wemo', 'wdevice4_active'):
                      home.triggerWemoDeviceOn(4)
                  if home.private.getboolean('Devices','decora'):
                    home.decora(home.private.get('Decora', 'switch_4'), "ON", "100")
                  if home.private.getboolean('Devices','hue'):
                    triggerSceneChange(z,'evening', i, int(home.private.get("HueGroups","zone"+str(z))))
                  if home.private.getboolean('Devices','decora') and home.public.getboolean('settings', 'vacation'):
                    home.decora(home.private.get('Decora', 'switch_1'), 'ON', '75')
                    home.decora(home.private.get('Decora', 'switch_4'), 'ON', '75')

    ############################
    # EVENING CYCLE MODE ZONE2 #
    # if i haven't said im going to bed then run evening mode

    z = 2
    for i in (0,1,2,3,4):
      if home.public.getboolean('settings', 'zone'+str(z)+'_evening'):
        if e[z][i] != ['null']:
          if i == 4:
            logging.debug('COMPARE zone'+str(z)+'_evening_'+str(i)+':'+str(e[z][i][0])+':'+str(e[z][i][1])+':'+str(e[z][i][2])+' < now ')
            if now.replace(hour=int(e[z][i][0]), minute=int(e[z][i][1]), second=int(e[z][i][2])) <= now :
              logging.debug('COMPARE zone'+str(z)+'_evening_'+str(i)+' CS['+str(z)+']='+str(cs[z])+':null,daytime_'+str(i-1)+',evening,home')
              if cs[z] in ('null','daytime_'+str(i-1),'evening_'+str(i-1),'home'):
                if cs[z] == 'null':
                  calculateEvenings(z,1)
                if home.private.getboolean('Devices','hue'):
                  triggerSceneChange(z,'evening', i, int(home.private.get("HueGroups","zone"+str(z))))
          else:
            logging.debug('COMPARE zone'+str(z)+'_evening_'+str(i)+':'+str(e[z][i][0])+':'+str(e[z][i][1])+':'+str(e[z][i][2])+' < now < '+str(e[z][i+1][0])+':'+str(e[z][i+1][1])+':'+str(e[z][i+1][2]))
            if now.replace(hour=int(e[z][i][0]), minute=int(e[z][i][1]), second=int(e[z][i][2])) <= now <= now.replace(hour=int(e[z][i+1][0]), minute=int(e[z][i+1][1]), second=int(e[z]  [i+1][2])):
              logging.debug('COMPARE zone'+str(z)+'_evening_'+str(i)+' CS['+str(z)+']='+str(cs[z])+':null,daytime_'+str(i)+',evening_'+str(i-1)+',home')
              if cs[z] in ('null','daytime_'+str(i),'evening_'+str(i-1),'home'):
                if cs[z] == 'null':
                  calculateEvenings(z,4-i)
                if home.private.getboolean('Devices','hue'):
                  if i == 0 and home.public.getboolean('settings', 'vacation'):
                    home.sendText("House is in vacation mode, begining evening cycle")
                  triggerSceneChange(z,'evening', i, int(home.private.get("HueGroups","zone"+str(z))))

    # if its past the vacation off time turn off the lights
    if home.public.getboolean('settings', 'vacation') and now.replace(hour=int(v_off[0]), minute=int(v_off[1]), second=int(v_off[2])) <= now:
      if cs[z] == 'evening_4':
        home.sendText("House is in vacation mode, turning off lights")
        home.groupLightsOff(0)
        home.public.set('zone'+str(z),'currentscene', 'vaca_off')
        # turn off all wemos
        for x in range(1,home.private.getint('Wemo','device_count')+1):
          if home.private.getboolean('Wemo', 'wdevice'+str(x)+'_active'):
            if home.public.getboolean('wemo','wdevice'+str(x)+'_status'):
              cmd = '/usr/local/bin/wemo switch "' + home.public.get('wemo', 'wdevice'+str(x)+'_name')+ '" off'
              proc = subprocess.Popen([cmd], stdout=subprocess.PIPE, shell=True )
              (out, err) = proc.communicate()
              logging.debug(cmd)
        # turn off all decora wifi lights
        if home.private.getboolean('Devices','decora'):
          for x in range(1,home.private.getint('Decora','switch_count')+1):
            home.decora(home.private.get('Decora', 'switch_'+str(x)), "OFF", "None")
        # clear the scenes
        cs = []
        for y in (0,1,2):
          home.public.set('zone'+str(y),'currentscene', 'vaca_off')
          logging.debug('zone'+str(y)+' current scene set to: vaca_off')
          home.public.set('zone'+str(y), 'previousscene', 'vaca_off')
          logging.debug('zone'+str(y)+' previous scene set to: vaca_off')
          home.saveSettings()


  #end auto run
  else:
    logging.debug('autorun is not enabled')

  ##############################
  # Configure Default Settings #
  # set evening start and end times to default if before first start time, so it auto is on before then it works
  # moved to end of script so , if the scene is home, daytime will get picked up. 
  for z in (0,1,2):
    fst = home.public.get('zone'+str(z),'evening_first_time').split(':')
    if now <= now.replace(hour=int(fst[0]), minute=int(fst[1]), second=int(fst[2])):
      logging.debug('Default settings applied zone'+str(z))
      home.public.set('settings','zone'+str(z)+'_evening', 'true')
      if z == 0:
        home.public.set('settings','bedtime', 'false')
        sys.argv.append("Defaults") #used in claculateSecenes
        # calculate evenings for each zone and number of evening scenes
        calculateEvenings(0,2)
        calculateEvenings(1,2)
        calculateEvenings(2,4)
        if home.public.getboolean('settings', 'vacation'):
          for y in (0,1,2):
            home.public.set('zone'+str(y),'currentscene', 'null')
            logging.debug('zone'+str(y)+' current scene set to: null')
            home.public.set('zone'+str(y), 'previousscene', 'null')
            logging.debug('zone'+str(y)+' previous scene set to: null')
            home.saveSettings()



  ##########################
  # Get Vivint Armed State #
  if home.private.getboolean('Devices','vivint'):
    old_alarm_state = home.public.get('vivint', 'state')
    new_alarm_state = home.get_armed_state()

    #####################
    # Check Who Is Home #
    if new_alarm_state != old_alarm_state:
      home.public.set('vivint','state', new_alarm_state)
      home.saveSettings()
      logging.info('Vivint changed from '+old_alarm_state+' to '+new_alarm_state)
      # the new state is armed_away, everyone must be gone, for each person make a leave file
      # just encase the geo-tracking doesnt work
      if new_alarm_state == "armed_away":
        for person, value in home.public.items("people_home"):
          if value == "true":
            logging.info('alarm armed, making leave file for '+person)
            filename = "AR-leave-"+str(random.randint(1,21))
            os.system("echo " +person+" > "+filename)
            os.system("mv "+filename+" "+home.private.get('Path','watch_dir')+'/leave')
#                time.sleep(1)
#                subprocess.Popen(["python3", "leave-script.py", filename])
            time.sleep(10)


    #####################################################
    # Send a text reminder if not armed by certain time #
    ar1 = datetime.datetime.strptime(str(home.public.get('vivint', 'remind_time')),'%H:%M:%S')
    ar2 = (ar1 + datetime.timedelta(minutes=5)).time()
    ar = str(home.public.get('vivint', 'remind_time')).split(':')
    ar_l = str(ar2).split(':')
    if home.private.getboolean('Devices', 'gmail'):
      logging.debug('checking sms section, ar:'+str(ar)+' ar_l:'+str(ar_l))
      if now.replace(hour=int(ar[0]), minute=int(ar[1]), second=int(ar[2])) <= now <= now.replace(hour=int(ar_l[0]), minute=int(ar_l[1]), second=int(ar_l[2])):
        if not home.public.getboolean('vivint', 'reminded'):
          if new_alarm_state == "disarmed":
            home.sendText("House is disarmed")
            home.public.set('vivint', 'reminded', 'true')
      else:
        home.public.set('vivint', 'reminded', 'false')

    ############################################################
    # Send a text reminder if no one is home and its not armed #
    run_text=True
    for section in home.public.sections():
      if section == "people_home":
        for person, value in home.public.items(section):
          if value == "true":
            run_text=False
            logging.debug('send text check: '+person+' is home')

    if run_text and new_alarm_state == "disarmed":
      logging.debug("Arm house reminder send triggered")
      if not home.private.get("MMS","sent"):
        logging.warning("MMS sent time blank")
        home.private.set("MMS","sent", now)
        home.saveSettings()
      home.sendText("House was left disarmed")


  #########################
  # save any new settings #
  #########################
  end = datetime.datetime.now()
  logging.debug('finished '+str(end-now))
# end mai


if __name__ == "__main__":
  home = myhouse.Home()

  # this allows you to pass in a time for testing ./script <hour> <min>
  now = datetime.datetime.now()

  if len(sys.argv) > 1:
    # reset all transition times to quick
    if sys.argv[1] == 'reset':
      home.SetQuickTrans('daytime_1')
      home.SetQuickTrans('morning_1')
      home.SetQuickTrans('home_1')
      for x in range(1,5):
        home.SetQuickTrans('scene_'+str(x))
    else:
      now = now.replace(hour=int(sys.argv[1]),minute=int(sys.argv[2]))
      home.public.set('settings','autorun', sys.argv[3])
      home.saveSettings()

  home.saveSettings()
  main(sys.argv[1:])


