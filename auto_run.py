import time, datetime
import subprocess, sys, getopt
import myhouse
import pyInfinitude.pyInfinitude
import logging
from decimal import Decimal
from subprocess import call

def triggerSceneChange (whichtag, whichScene):
  logging.info(str(whichtag)+'_'+str(whichScene))
  cs = home.public.get('auto','currentscene')
  home.public.set('auto','currentscene', str(whichtag)+'_'+str(whichScene))
  logging.debug('current scene set to: '+str(whichtag)+'_'+str(whichScene))
  home.public.set('auto', 'previousscene', cs)
  logging.debug('previous scene set to: '+cs)

  # set any temp scenes to off
  for section in home.public.sections():
    if section == "light_scenes":
      for scene, value in home.public.items(section):
        if value == 'on':
          home.public.set('light_scenes', scene, 'off')

  home.saveSettings()

  # if vacation mode is on trigger the first scene of the evening
  if whichtag == 'vaca':
    whichScene = '1'
    whichtag = 'scene' 

  # actually activate scene with transition time
  home.setTransTimeOfScene(home.private.get('Scenes', str(whichtag)+'_'+str(whichScene)), home.public.get('auto', str(whichtag)+'_'+str(whichScene)+'_trans_time'))
  time.sleep(.2)
  home.playScene(home.private.get('Scenes', str(whichtag)+'_'+str(whichScene)),home.private.get('Groups','main_floor'))
  # set the transition time for the current scene back to quick on the hue bridge

  # this keeps making them trigger fast and not respecting the setrasition time, try using that fucntion after play, or a time delay before this
  #  home.SetQuickTrans(str(whichtag)+'_'+str(whichScene))

  #####################
  # WEMO Home CONTROL #
  # device that is on when ever some one is home except for bed 
  # check and see if any one is home, if they are dont change ant$
  if not home.public.getboolean('wemo','wemo_home_status'):
    for section in home.public.sections():
      if section == "people_home":
        for person, value in home.public.items(section):
          if value == 'yes':
            proc = subprocess.Popen(['/usr/local/bin/wemo switch "wemo im home" on'], stdout=subprocess.PIPE, shell=True ) 
            (out, err) = proc.communicate()
            logging.info('wemo im home turned on')



def calculateScenes(howmany):

  # if calculate is called and the time is before default start, use default start time to calculate
  if len(sys.argv) > 1:
    fst = home.private.get('Time', 'first_time').split(':')
    calcNow = now.replace(hour=int(fst[0]), minute=int(fst[1]), second=int(fst[2]))
  else:
    calcNow = now

  # read in last scene trigger (lst) time in from config file
  lst = home.private.get('Time', 'last_time').split(':')
  diff = (datetime.datetime.today().replace(hour=int(lst[0]), minute=int(lst[1]), second=int(lst[2]))) - calcNow
  # time to next scene (ttns)
  ttns=diff/howmany
  # transition time (tt) should be 60% of the ttns, and then converted into 100's of mili seconds
  tp = (float(home.private.get('Time', 'trans_percent'))/100)
  tt = int(((int(ttns.total_seconds())*tp)*1000)/100)

  if howmany == 4:
    home.public.set('auto','scene_1_on_time', calcNow.time().strftime("%H:%M:%S"))
    home.public.set('auto','scene_1_trans_time', tt)
    home.public.set('auto','scene_2_on_time', (calcNow+ttns).time().strftime("%H:%M:%S"))
    home.public.set('auto','scene_2_trans_time', tt)
    home.public.set('auto','scene_3_on_time', (calcNow+(ttns*2)).time().strftime("%H:%M:%S"))
    home.public.set('auto','scene_3_trans_time', tt)
    home.public.set('auto','scene_4_on_time', (calcNow+(ttns*3)).time().strftime("%H:%M:%S"))
    home.public.set('auto','scene_4_trans_time', tt)
    home.public.set('auto','scene_5_on_time', (calcNow+diff).time().strftime("%H:%M:%S"))
    home.public.set('auto','scene_5_trans_time', tt)
  if howmany == 3:
    home.public.set('auto','scene_1_on_time', 'null')
    home.public.set('auto','scene_1_trans_time', 'null')
    home.public.set('auto','scene_2_on_time',calcNow.time().strftime("%H:%M:%S"))
    home.public.set('auto','scene_2_trans_time', tt)
    home.public.set('auto','scene_3_on_time', (calcNow+ttns).time().strftime("%H:%M:%S"))
    home.public.set('auto','scene_3_trans_time', tt)
    home.public.set('auto','scene_4_on_time', (calcNow+(ttns*2)).time().strftime("%H:%M:%S"))
    home.public.set('auto','scene_4_trans_time', tt)
    home.public.set('auto','scene_5_on_time', (calcNow+diff).time().strftime("%H:%M:%S"))
    home.public.set('auto','scene_5_trans_time', tt)
  if howmany == 2:
    home.public.set('auto','scene_1_on_time', 'null')
    home.public.set('auto','scene_1_trans_time', 'null')
    home.public.set('auto','scene_2_on_time', 'null')
    home.public.set('auto','scene_2_trans_time', 'null')
    home.public.set('auto','scene_3_on_time', calcNow.time().strftime("%H:%M:%S"))
    home.public.set('auto','scene_3_trans_time', tt)
    home.public.set('auto','scene_4_on_time', (calcNow+ttns).time().strftime("%H:%M:%S"))
    home.public.set('auto','scene_4_trans_time', tt)
    home.public.set('auto','scene_5_on_time', (calcNow+diff).time().strftime("%H:%M:%S"))
    home.public.set('auto','scene_5_trans_time', tt)
  if howmany == 1:
    home.public.set('auto','scene_1_on_time', 'null')
    home.public.set('auto','scene_1_trans_time', 'null')
    home.public.set('auto','scene_2_on_time', 'null')
    home.public.set('auto','scene_2_trans_time', 'null')
    home.public.set('auto','scene_3_on_time', 'null')
    home.public.set('auto','scene_3_trans_time', 'null')
    home.public.set('auto','scene_4_on_time', calcNow.time().strftime("%H:%M:%S"))
    home.public.set('auto','scene_4_trans_time', tt)
    home.public.set('auto','scene_5_on_time', (calcNow+diff).time().strftime("%H:%M:%S"))
    home.public.set('auto','scene_5_trans_time', tt)

  home.saveSettings()
  # end calculate scenes

def main(argv):
  logging.debug('Running Main()')


  cs = home.public.get('auto','currentscene')
  # if auto run is off calculate transition times
  # 3,600,000/100 = 36000ms = 1 hour
  # 18000 = 30 minutes
  # 27000 = 45 minutes

  # Monday is 0 and Sunday is 6.
  today = now.today().weekday()

  ################################
  # Clean up trigger directories #
  call(["find", home.private.get('IFTTT','dir'), "-type", "f", "-name", "*.txt", "-exec", "rm", "{}", "+"])

  ####################
  # Pull Wemo Status #
  # lava lamp
  prevLL = home.public.get('wemo', 'll_status')
  proc = subprocess.Popen(['/usr/local/bin/wemo switch "lava lamp" status'], stdout=subprocess.PIPE, shell=True ) 
  (out, err) = proc.communicate()
  home.public.set('wemo', 'll_status', out.rstrip('\n') )
  home.saveSettings()
  currentLL = home.public.get('wemo', 'll_status')
  if prevLL != currentLL:
    logging.info('Lava Lamp changed from '+prevLL+' to '+currentLL)
  # wemo im home
  prevHome = home.public.get('wemo', 'wemo_home_status')
  proc = subprocess.Popen(['/usr/local/bin/wemo switch "wemo im home" status'], stdout=subprocess.PIPE, shell=True ) 
  (out, err) = proc.communicate()
  home.public.set('wemo', 'wemo_home_status', out.rstrip('\n') )
  home.saveSettings()
  currentHome = home.public.get('wemo', 'wemo_home_status')
  if prevHome != currentHome:
    logging.info('Wemo im home changed from '+prevHome+' to '+currentHome)

  ###############################
  # Configure Vacation Settings #
  # check and see if you are on vacation and configure
  if home.public.getboolean('settings', 'vacation'):
    home.public.set('settings','morning', 'off')
    home.public.set('settings','autorun', 'on')
    home.public.set('settings','evening', 'on')
    v_on = str(home.private.get('Time', 'vaca_on_time')).split(':')
    v_off = str(home.private.get('Time', 'vaca_off_time')).split(':')
    home.private.set('Time','last_time', str(home.private.get('Time', 'vaca_off_time')))
  else:
    # turned off because this kept making morning come on when it was turned off
    #home.public.set('settings','morning', 'on') 
    home.private.set('Time','last_time', home.private.get('Time','default_last_time'))

  ##############################
  # Configure Default Settings #
  # set evening start and end times to default if before first start time, so it auto is on before then it works
  fst = home.private.get('Time', 'first_time').split(':')
  if now <= now.replace(hour=int(fst[0]), minute=int(fst[1]), second=int(fst[2])):
    logging.debug('Default settings applied '+str(now)+' <= '+ str(now.replace(hour=int(fst[0]), minute=int(fst[1]), second=int(fst[2]))))
    home.public.set('settings','evening', 'on')
    home.public.set('settings','bed', 'off')
    sys.argv.append("Defaults") #used in claculateSecenes
    calculateScenes(4)
    if cs != 'morn_1' and cs != 'daytime_1' and cs != 'home':
      home.public.set('auto','currentscene', 'null')
      logging.debug('current scene set to: null')
      home.public.set('auto', 'previousscene', cs)
      logging.debug('previous scene set to: '+cs)


  ##########################
  # AUTO RUN LIGHT SECTION #
  ##########################

  # if auto run is on do  auto run stuff
  if home.public.getboolean('settings', 'autoRun'):

    # get the start time for all the scenes
    st_morn = str(home.public.get('auto', 'morning_1_on_time')).split(':')
    st_day = str(home.public.get('auto', 'daytime_1_on_time')).split(':')
    st_1 = str(home.public.get('auto', 'scene_1_on_time')).split(':')
    st_2 = str(home.public.get('auto', 'scene_2_on_time')).split(':')
    st_3 = str(home.public.get('auto', 'scene_3_on_time')).split(':')
    st_4 = str(home.public.get('auto', 'scene_4_on_time')).split(':')
    st_5 = str(home.public.get('auto', 'scene_5_on_time')).split(':')
    ls_bed = str(home.private.get('Time', 'last_time')).split(':')

    #################
    # VACATION MODE #
    # if its past the  vacation on time turn on the lights and trigger the first scene
    if home.public.getboolean('settings', 'vacation'):
      if now.replace(hour=int(v_on[0]), minute=int(v_on[1]), second=int(v_on[2])) <= now <= now.replace(hour=int(v_off[0]), minute=int(v_off[1]), second=int(v_off[2])):
        if cs == 'null' and cs != 'vaca':
          home.groupLightsOn(0)
          triggerSceneChange('vaca', 1)


    #####################
    # LAVA LAMP CONTROL # 
    ll_on = str(home.public.get('wemo', 'll_switch_on_time')).split(':')
    ll_off = str(home.public.get('wemo', 'll_switch_off_time')).split(':')
    # times must be between 0..59, by doing a -10 it can cause error 
    for i in range(1,3):
      if int(ll_off[i]) < 11:
         ll_off[i] = str(49 + int(ll_off[i]))
      if int(ll_on[i]) < 11:
         ll_on[i] = str(49 + int(ll_on[i]))
    # if vacation mode is off check the time
    if not home.public.getboolean('settings', 'vacation'):
      if now.replace(hour=int(ll_on[0]), minute=int(ll_on[1]), second=int(ll_on[2])) <= now <= now.replace(hour=int(ll_on[0]), minute=int(ll_on[1])+10, second=int(ll_on[2])):
        proc = subprocess.Popen(['/usr/local/bin/wemo switch "lava lamp" on'], stdout=subprocess.PIPE, shell=True )
        (out, err) = proc.communicate()
        logging.info('lava lamp turned on')
      if now.replace(hour=int(ll_off[0]), minute=int(ll_off[1])-10, second=int(ll_off[2])) <= now <= now.replace(hour=int(ll_off[0]), minute=int(ll_off[1]), second=int(ll_off[2])):
        proc = subprocess.Popen(['/usr/local/bin/wemo switch "lava lamp" off'], stdout=subprocess.PIPE, shell=True )
        (out, err) = proc.communicate()
        logging.info('lava lamp turned off')

    #######################
    # Hoime Light CONTROL # 
    # if bed mode is on turn off the wemo home light
    if home.public.getboolean('settings', 'bed'):
      if home.public.getboolean('wemo','wemo_home_status'):
        proc = subprocess.Popen(['/usr/local/bin/wemo switch "wemo im home" off'], stdout=subprocess.PIPE, shell=True )
        (out, err) = proc.communicate()
        logging.info('wemo im home turned off')


    ################
    # MORNING MODE #
    # if morning scene is enabled
    if cs == 'null':
      if home.public.getboolean('settings', 'morning'):
        if now.replace(hour=int(st_morn[0]), minute=int(st_morn[1]), second=int(st_morn[2])) <= now <= now.replace(hour=int(st_day[0]), minute=int(st_day[1]), second=int(st_day[2])) :
          triggerSceneChange('morn', 1)
          # if morning mode is enabled, check if wake is on if so turn on the bedroom wake
          home.setLightScheduleStatus(1,"enabled")
      else:
        # if morning mode is disabled also turn off the bedroom wake scene
        home.setLightScheduleStatus(1,"disabled")

    ################
    # DAYTIME MODE #
    # if morning sceene is over and its before evening 1
    if st_1  != ['null']:
      if cs == 'morn_1' or cs == 'home' or cs == 'null':
        if now.replace(hour=int(st_day[0]), minute=int(st_day[1]), second=int(st_day[2])) <= now <= now.replace(hour=int(st_1[0]), minute=int(st_1[1]), second=int(st_1[2])) :
          triggerSceneChange('daytime', 1)

    ######################
    # EVENING CYCLE MODE #
    # if i haven't said im going to bed then run evening mode
    if home.public.getboolean('settings', 'evening'):
      # stage 1
      if st_1 != ['null']:
        if now.replace(hour=int(st_1[0]), minute=int(st_1[1]), second=int(st_1[2])) <= now <= now.replace(hour=int(st_2[0]), minute=int(st_2[1]), second=int(st_2[2])):
          if cs == 'null' or cs == 'vaca_1' or cs == 'daytime_1' or cs == 'home':
            calculateScenes(4)
            triggerSceneChange('scene', 1)

      # stage 2
      if st_2 != ['null']:
        if now.replace(hour=int(st_2[0]), minute=int(st_2[1]), second=int(st_2[2])) <= now <= now.replace(hour=int(st_3[0]), minute=int(st_3[1]), second=int(st_3[2])):        
          if cs == 'null':
            calculateScenes(3)
          if cs == 'scene_1' or cs == 'null' or cs == 'home':
            triggerSceneChange('scene',2)

      # stage 3
      if st_3 != ['null']:
        if now.replace(hour=int(st_3[0]), minute=int(st_3[1]), second=int(st_3[2])) <= now <= now.replace(hour=int(st_4[0]), minute=int(st_4[1]), second=int(st_4[2])):        
          if cs == 'null':
            calculateScenes(2)
          if cs == 'scene_2' or cs == 'null' or cs == 'home':
            triggerSceneChange('scene',3)

      # stage 4
      if st_4 != ['null']:
        if now.replace(hour=int(st_4[0]), minute=int(st_4[1]), second=int(st_4[2])) <= now <= now.replace(hour=int(st_5[0]), minute=int(st_5[1]), second=int(st_5[2])):        
          if cs == 'null':
            calculateScenes(1)
          if cs == 'scene_3' or cs == 'null' or cs == 'home':
            triggerSceneChange('scene',4)

      # stage 5
      if st_5 != ['null']:
        if now.replace(hour=int(st_5[0]), minute=int(st_5[1]), second=int(st_5[2])) <= now:
          if cs == 'scene_4' or cs == 'null' or cs == 'home':
            home.public.set('auto','currentscene', 'null')
            if home.public.getboolean('settings', 'vacation'):
              home.public.set('auto','currentscene', 'scene_5')
            triggerSceneChange('scene',5)

      # if its past the vacation off time turn off the lights
      if home.public.getboolean('settings', 'vacation') and now.replace(hour=int(v_off[0]), minute=int(v_off[1]), second=int(v_off[2])) <= now:
        if cs == 'scene_5' or cs == 'vaca_1':
          logging.info('vacation mode enabled, turning lights off')
          home.groupLightsOff(0)
          home.public.set('auto','currentscene', 'vaca_off')

  #end auto run
  else:
    logging.debug('autorun is not enabled')


  ###########################
  # global morning settings #
  ###########################

  # define all morning times based off global morning value
  gm = home.public.get('mornings', str(today)+'_morning')
  global_Morning = datetime.datetime.strptime(gm, '%H:%M:%S')

  # make the morning triggers 30 minutes before global to allow fades
  newMorning = (global_Morning - datetime.timedelta(minutes=30)).time()

  # HVAC settings set below for wake and home
  # make the home profile trigger 1.5hrs after morning
  newHome = (global_Morning + datetime.timedelta(hours=1, minutes=30)).time()
  # check and set morning lights
  lm = home.public.get('auto','morning_1_on_time')
  if lm != 'null':
    light_Morning = datetime.datetime.strptime(lm, '%H:%M:%S').time()
    if newMorning != light_Morning:
      # set light scene morning 
      home.public.set('auto','morning_1_on_time', newMorning)
      home.saveSettings()

  # check and set morning light alarm clock
  wm = home.public.get('wakeup_schedule','localtime').split("T",1)[1]
  if wm != 'null':
    wake_Morning = datetime.datetime.strptime(wm, '%H:%M:%S').time()
    if newMorning != wake_Morning:
      # set bedroom wake schedule 
      home.setLightScheduleTime(1,newMorning)

  ######################
  # Pull hue schedules #
  ######################

  lightSchedule = home.getLightSchedule(1);
  home.public.set('wakeup_schedule', 'localtime', lightSchedule['localtime']) 
  home.public.set('wakeup_schedule', 'status', lightSchedule['status']) 

  ####################
  # Pull KEVO Status #
  ####################

  prevLock = home.public.get('lock', 'status')
  try:
    home.public.set('lock', 'status', home.kevo("status"))
    home.saveSettings()
  except: 
    logging.error('Lock status set error')
 
  currentLock = home.public.get('lock', 'status')
  if prevLock != currentLock:
    logging.info('Lock changed from '+prevLock+' to '+currentLock)

  ############################
  # Pull TV shows for 7 days #
  ############################

  home.pullDVRupcoming()
  for x in range(0,8):
    home.public.set('dvr', str(x)+'_shows', home.getDVRshows(x, home.upFile))

  home.pullDVRrecorded()
  home.public.set('dvrRecorded', 'shows', home.getDVRshows(0, home.recFile))


  ########################
  # Pull Current Weather #
  ########################

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

  if not hvac.pullConfig():
    home.public.set('hvac','status','error')
  else:
    home.public.set('hvac','status','ok')

    zone = int(home.private.get('hvac', 'zone'))

    # adjust days of week num to allign with carrier and infinitude numbering
    for day in range(0,7):
      # nullify each value because if there is no value it will be blank
      for period in range(0,5):
        home.public.set('hvac', "day_"+str(day)+"_event_"+str(period)+"_on_time", 'null')
        home.public.set('hvac', "day_"+str(day)+"_event_"+str(period)+"_activity", 'null')

      # pull out all hvac activity and times for schedule, insert it into config file
        if hvac.get_zone_program_day_period_enabled(zone, day, period) == 'on':
          home.public.set('hvac', "day_"+str(day)+"_event_"+str(period)+"_on_time", hvac.get_zone_program_day_period_time(zone, day, period)) 
          home.public.set('hvac', "day_"+str(day)+"_event_"+str(period)+"_activity", hvac.get_zone_program_day_period_activity(zone, day, period)) 

    # get the HVAC mode
    home.public.set('hvac','mode', hvac.get_mode());

    # pull out clsp and htsp for each profile name
    # id: 0 = home, 1 = away, 2 = sleep, 3 = wake, 4 = manual
    for id in range(0,5):
      profile = hvac.get_zone_activity_name(zone, id)
      home.public.set('profile_current', profile+'_fan', hvac.get_zone_activity_fan(zone, id))
      home.public.set('profile_current', profile+'_clsp', hvac.get_zone_activity_clsp(zone, id))
      home.public.set('profile_current', profile+'_htsp', hvac.get_zone_activity_htsp(zone, id))

    # get the vacation data too
    home.public.set('profile_current','vacmaxt', hvac.get_vacmaxt())
    home.public.set('profile_current','vacmint', hvac.get_vacmint())
    home.public.set('profile_current','vacfan', hvac.get_vacfan())

    # find if hvac has a wake profile actively set and set it to be inline with global morning
    # today only
    day = (int(datetime.datetime.today().weekday())+1)
    change=False
    if day == 7:
      day = 0
    for period in range(0,5):
      if home.public.get('hvac', 'day_'+str(day)+'_event_'+str(period)+'_activity') == 'wake':
        hm = home.public.get('hvac', 'day_'+str(day)+'_event_'+str(period)+'_on_time')
        hvac_Morning = datetime.datetime.strptime(hm, '%H:%M').time()
        if hvac_Morning != newMorning:
          logging.info("Adjusting WAKE profile to "+str(newMorning)+' d:'+str(day))
          hvac.set_zone_program_day_period_time(zone, day, period, newMorning.strftime('%H:%M'))
          change=True

    # check and set todays home profile to be after wake
    for period in range(0,5):
      if home.public.get('hvac', 'day_'+str(day)+'_event_'+str(period)+'_activity') == 'home':
        hm = home.public.get('hvac', 'day_'+str(day)+'_event_'+str(period)+'_on_time')
        hvac_home = datetime.datetime.strptime(hm, '%H:%M').time()
        if hvac_home != newHome:
          logging.info("Adjusting HOME profile to "+str(newHome)+' d:'+str(day))
          hvac.set_zone_program_day_period_time(zone, day, period, newHome.strftime('%H:%M'))
          # make the hvac change
          change=True

    if change:
      if not hvac.pushConfig():
        logging.error('pushConfig failed')


  #########################
  # save any new settings #
  #########################
  home.saveSettings()
  end = datetime.datetime.now()
  logging.debug('finished '+str(end-now))
# end mai


if __name__ == "__main__":
  home = myhouse.Home()

  hvacIP = home.private.get('hvac', 'ip')
  hvacPort = home.private.get('hvac', 'port')
  hvacFile = '/home/host/home_auto_scripts/support/'+home.private.get('hvac', 'file')
  hvacStatusFile = '/home/host/home_auto_scripts/support/'+home.private.get('hvac', 'status')
  hvac = pyInfinitude.pyInfinitude.infinitude(hvacIP,hvacPort,hvacFile,hvacStatusFile)

  # this allows you to pass in a time for testing ./script <hour> <min>
  now = datetime.datetime.now()

  if len(sys.argv) > 1:
    # reset all transition times to quick
    if sys.argv[1] == 'reset':
      home.SetQuickTrans('daytime_1')
      home.SetQuickTrans('morn_1')
      home.SetQuickTrans('home_1')
      for x in range(1,5):
        home.SetQuickTrans('scene_'+str(x))
    else:    
      now = now.replace(hour=int(sys.argv[1]),minute=int(sys.argv[2]))
      home.public.set('settings','autorun', sys.argv[3])
      home.saveSettings()

  home.saveSettings()
  main(sys.argv[1:])


