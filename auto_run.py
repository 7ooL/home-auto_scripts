import time, datetime
import ConfigParser
import sys, getopt
import myhouse
import pyInfinitude.pyInfinitude
import logging
from decimal import Decimal

public = ConfigParser.RawConfigParser()
public.read('/home/host/home_auto_scripts/public.ini')
private = ConfigParser.RawConfigParser()
private.read('/home/host/home_auto_scripts/private.ini')

def saveSettings():
  with open(r'/home/host/home_auto_scripts/public.ini', 'wb') as configfile:
    public.write(configfile)
  with open(r'/home/host/home_auto_scripts/private.ini', 'wb') as configfile:
    private.write(configfile)


def triggerSceneChange (whichtag, whichScene):
  cs = public.get('auto','currentscene')
  public.set('auto','currentscene', str(whichtag)+'_'+str(whichScene))
  logging.debug('auto_run.py.triggerSceneChange: current scene set to: '+str(whichtag)+'_'+str(whichScene))
  public.set('auto', 'previousscene', cs)
  logging.debug('auto_run.py.triggerSceneChange: previous scene set to: '+cs)

  # if vacation mode is on trigger the first scene of the evening
  if whichtag == 'vaca':
    whichScene = 1
    whichtag = 'scene' 

  # actually activate scene with transition time
  home.setTransTimeOfScene(private.get('Scenes', str(whichtag)+'_'+str(whichScene)), public.get('auto', str(whichtag)+'_'+str(whichScene)+'_trans_time'))
  time.sleep(.2)
  home.playScene(private.get('Scenes', str(whichtag)+'_'+str(whichScene)),private.get('Groups','main_floor'))

  # set the transition time for the current scene back to quick on the hue bridge

  # this keeps making them trigger fast and not respecting the setrasition time, try using that fucntion after play, or a time delay before this
  #  home.SetQuickTrans(str(whichtag)+'_'+str(whichScene))


def calculateScenes(howmany):

  # if calculate is called and the time is before default start, use default start time to calculate
  if len(sys.argv) > 1:
    fst = private.get('time', 'first_time').split(':')
    calcNow = now.replace(hour=int(fst[0]), minute=int(fst[1]), second=int(fst[2]))
  else:
    calcNow = now

  # read in last scene trigger (lst) time in from config file
  lst = private.get('time', 'last_time').split(':')
  diff = (datetime.datetime.today().replace(hour=int(lst[0]), minute=int(lst[1]), second=int(lst[2]))) - calcNow
  # time to next scene (ttns)
  ttns=diff/howmany
  # transition time (tt) should be 60% of the ttns, and then converted into 100's of mili seconds
  tp = (float(private.get('time', 'trans_percent'))/100)
  tt = int(((int(ttns.total_seconds())*tp)*1000)/100)

  if howmany == 4:
    public.set('auto','scene_1_on_time', calcNow.time().strftime("%H:%M:%S"))
    public.set('auto','scene_1_trans_time', tt)
    public.set('auto','scene_2_on_time', (calcNow+ttns).time().strftime("%H:%M:%S"))
    public.set('auto','scene_2_trans_time', tt)
    public.set('auto','scene_3_on_time', (calcNow+(ttns*2)).time().strftime("%H:%M:%S"))
    public.set('auto','scene_3_trans_time', tt)
    public.set('auto','scene_4_on_time', (calcNow+(ttns*3)).time().strftime("%H:%M:%S"))
    public.set('auto','scene_4_trans_time', tt)
    public.set('auto','scene_5_on_time', (calcNow+diff).time().strftime("%H:%M:%S"))
    public.set('auto','scene_5_trans_time', tt)
  if howmany == 3:
    public.set('auto','scene_1_on_time', 'null')
    public.set('auto','scene_1_trans_time', 'null')
    public.set('auto','scene_2_on_time',calcNow.time().strftime("%H:%M:%S"))
    public.set('auto','scene_2_trans_time', tt)
    public.set('auto','scene_3_on_time', (calcNow+ttns).time().strftime("%H:%M:%S"))
    public.set('auto','scene_3_trans_time', tt)
    public.set('auto','scene_4_on_time', (calcNow+(ttns*2)).time().strftime("%H:%M:%S"))
    public.set('auto','scene_4_trans_time', tt)
    public.set('auto','scene_5_on_time', (calcNow+diff).time().strftime("%H:%M:%S"))
    public.set('auto','scene_5_trans_time', tt)
  if howmany == 2:
    public.set('auto','scene_1_on_time', 'null')
    public.set('auto','scene_1_trans_time', 'null')
    public.set('auto','scene_2_on_time', 'null')
    public.set('auto','scene_2_trans_time', 'null')
    public.set('auto','scene_3_on_time', calcNow.time().strftime("%H:%M:%S"))
    public.set('auto','scene_3_trans_time', tt)
    public.set('auto','scene_4_on_time', (calcNow+ttns).time().strftime("%H:%M:%S"))
    public.set('auto','scene_4_trans_time', tt)
    public.set('auto','scene_5_on_time', (calcNow+diff).time().strftime("%H:%M:%S"))
    public.set('auto','scene_5_trans_time', tt)
  if howmany == 1:
    public.set('auto','scene_1_on_time', 'null')
    public.set('auto','scene_1_trans_time', 'null')
    public.set('auto','scene_2_on_time', 'null')
    public.set('auto','scene_2_trans_time', 'null')
    public.set('auto','scene_3_on_time', 'null')
    public.set('auto','scene_3_trans_time', 'null')
    public.set('auto','scene_4_on_time', calcNow.time().strftime("%H:%M:%S"))
    public.set('auto','scene_4_trans_time', tt)
    public.set('auto','scene_5_on_time', (calcNow+diff).time().strftime("%H:%M:%S"))
    public.set('auto','scene_5_trans_time', tt)

  saveSettings()
  # end calculate scenes

def main(argv):
  logging.debug('auto_run.py: Running Main()')
  cs = public.get('auto','currentscene')
  # if auto run is off calculate transition times
  # 3,600,000/100 = 36000ms = 1 hour
  # 18000 = 30 minutes
  # 27000 = 45 minutes

  # define all morning times based off global morning value
  gm = public.get('global','global_morning')
  global_Morning = datetime.datetime.strptime(gm, '%H:%M:%S')

  # make the morning triggers 30 minutes before global to allow fades
  newMorning = (global_Morning - datetime.timedelta(minutes=30)).time()
  # check and set hvac wake timer in hvac section below

  # check and set morning lights
  lm = public.get('auto','morning_1_on_time')
  if lm != 'null':
    light_Morning = datetime.datetime.strptime(lm, '%H:%M:%S').time()
    if newMorning != light_Morning:
      # set light scene morning 
      public.set('auto','morning_1_on_time', newMorning)
      saveSettings()

  # check and set morning light alarm clock
  wm = public.get('wakeup_schedule','localtime').split("T",1)[1]
  if wm != 'null':
    wake_Morning = datetime.datetime.strptime(wm, '%H:%M:%S').time()
    if newMorning != wake_Morning:
      # set bedroom wake schedule 
      home.setLightScheduleTime(1,newMorning)

  # check and see if you are on vacation and configure
  if public.getboolean('settings', 'vacation'):
    public.set('settings','morning', 'off')
    public.set('settings','autorun', 'on')
    public.set('settings','evening', 'on')
    v_on = str(private.get('time', 'vaca_on_time')).split(':')
    v_off = str(private.get('time', 'vaca_off_time')).split(':')
    private.set('time','last_time', str(private.get('time', 'vaca_off_time')))
  else:
    # turned off because this kept making morning come on when it was turned off
    #public.set('settings','morning', 'on') 
    private.set('time','last_time', private.get('time','default_last_time'))

  # set evening start and end times to default if before first start time, so it auto is on before then it works
  fst = private.get('time', 'first_time').split(':')
  if now <= now.replace(hour=int(fst[0]), minute=int(fst[1]), second=int(fst[2])):
    logging.debug('auto_run.py: Default settings applied '+str(now)+' <= '+ str(now.replace(hour=int(fst[0]), minute=int(fst[1]), second=int(fst[2]))))
    public.set('settings','evening', 'on')
    public.set('settings','bed', 'off')
    sys.argv.append("Defaults") #used in claculateSecenes
    calculateScenes(4)
    if cs != 'morn_1' and cs != 'daytime_1' and cs != 'home':
      public.set('auto','currentscene', 'null')
      logging.debug('auto_run.py: current scene set to: null')
      public.set('auto', 'previousscene', cs)
      logging.debug('auto_run.py: previous scene set to: '+cs)


  ##########################
  # AUTO RUN LIGHT SECTION #
  ##########################

  # if auto run is on do  auto run stuff
  if public.getboolean('settings', 'autoRun'):

    # get the start time for all the scenes
    st_morn = str(public.get('auto', 'morning_1_on_time')).split(':')
    st_day = str(public.get('auto', 'daytime_1_on_time')).split(':')
    st_1 = str(public.get('auto', 'scene_1_on_time')).split(':')
    st_2 = str(public.get('auto', 'scene_2_on_time')).split(':')
    st_3 = str(public.get('auto', 'scene_3_on_time')).split(':')
    st_4 = str(public.get('auto', 'scene_4_on_time')).split(':')
    st_5 = str(public.get('auto', 'scene_5_on_time')).split(':')
    ls_bed = str(private.get('time', 'last_time')).split(':')

    #################
    # VACATION MODE #
    # if its past the  vacation on time turn on the lights and trigger the first scene
    if public.getboolean('settings', 'vacation'):
      if now.replace(hour=int(v_on[0]), minute=int(v_on[1]), second=int(v_on[2])) <= now <= now.replace(hour=int(v_off[0]), minute=int(v_off[1]), second=int(v_off[2])):
        if cs == 'null' and cs != 'vaca':
          home.groupLightsOn(0)
          triggerSceneChange('vaca', 1)

    ################
    # MORNING MODE #
    # if morning scene is enabled
    if cs == 'null':
      if public.getboolean('settings', 'morning'):
        if now.replace(hour=int(st_morn[0]), minute=int(st_morn[1]), second=int(st_morn[2])) <= now <= now.replace(hour=int(st_day[0]), minute=int(st_day[1]), second=int(st_day[2])) :
          triggerSceneChange('morn', 1)
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
    if public.getboolean('settings', 'evening'):
      # stage 1
      if st_1 != ['null']:
        if now.replace(hour=int(st_1[0]), minute=int(st_1[1]), second=int(st_1[2])) <= now <= now.replace(hour=int(st_2[0]), minute=int(st_2[1]), second=int(st_2[2])):
          if cs == 'null' or cs == 'scene_vaca' or cs == 'daytime_1' or cs == 'home':
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
            public.set('auto','currentscene', 'null')
            if public.getboolean('settings', 'vacation'):
              public.set('auto','currentscene', 'scene_5')
            triggerSceneChange('scene',5)

      # if its past the vacation off time turn off the lights
      if public.getboolean('settings', 'vacation') and now.replace(hour=int(v_off[0]), minute=int(v_off[1]), second=int(v_off[2])) <= now:
        if cs == 'scene_5':    
          logging.info('auto_run.py: vacation mode enabled, turning lights off')
          home.groupLightsOff(0)      
          public.set('auto','currentscene', 'null')

  #end auto run  
  else:
    logging.debug('auto_run.py: autorun is not enabled')


  ######################
  # Pull hue schedules #
  ######################

  lightSchedule = home.getLightSchedule(1);
  public.set('wakeup_schedule', 'localtime', lightSchedule['localtime']) 
  public.set('wakeup_schedule', 'status', lightSchedule['status']) 

  ####################
  # Pull KEVO Status #
  ####################

  public.set('lock', 'status', home.kevo("status"))

  ########################
  # Pull todays TV shows #
  ########################

  public.set('extra', 'upcoming_shows', home.getDVRToday())

  ########################
  # Pull Current Weather #
  ########################

  weatherdata = home.getWeather();
  public.set('weather', 'weather', weatherdata['current_observation']['weather']) #mostly cloudy
  public.set('weather', 'icon', weatherdata['current_observation']['icon'])
  public.set('weather', 'icon_url', weatherdata['current_observation']['icon_url'])
  public.set('weather', 'oh', weatherdata['current_observation']['relative_humidity'].replace('%',''))
  public.set('weather', 'ot', weatherdata['current_observation']['temp_f'])
  public.set('weather', 'forecast_url', weatherdata['current_observation']['forecast_url'])

  ##################
  # Pull HVAC Data #
  ##################
  # pull configuation file from hvac and set public ini file for web interface

  if not hvac.pullConfig():
    public.set('hvac','status','error')
  else:
    public.set('hvac','status','ok')

    zone = int(private.get('hvac', 'zone'))
    # adjust days of week num to allign with carrier and infinitude numbering
    day = (int(datetime.datetime.today().weekday())+1)
    if day == 7:
      day = 0

    # clear out todays schedule, do this after the queries are made so it is faster
    for x in range(0,5):
      public.set('hvac', "event_"+str(x)+"_on_time", 'null')
      public.set('hvac', "event_"+str(x)+"_activity", 'null')
    # get the HVAC mode
    public.set('hvac','mode', hvac.get_mode());

    # pull out today's hvac activity and times for schedule, insert it into config file
    for period in range(0,5):
      if hvac.get_zone_program_day_period_enabled(zone, day, period) == 'on':
        public.set('hvac', "event_"+str(period)+"_on_time", hvac.get_zone_program_day_period_time(zone, day, period)) 
        public.set('hvac', "event_"+str(period)+"_activity", hvac.get_zone_program_day_period_activity(zone, day, period)) 

    # pull out clsp and htsp for each profile name
    # id: 0 = home, 1 = away, 2 = sleep, 3 = wake, 4 = manual
    for id in range(0,5):
      profile = hvac.get_zone_activity_name(zone, id)
      public.set('profile_current', profile+'_fan', hvac.get_zone_activity_fan(zone, id))
      public.set('profile_current', profile+'_clsp', hvac.get_zone_activity_clsp(zone, id))
      public.set('profile_current', profile+'_htsp', hvac.get_zone_activity_htsp(zone, id))

    # get the avcation data too
    public.set('profile_current','vacmaxt', hvac.get_vacmaxt())
    public.set('profile_current','vacmint', hvac.get_vacmint())
    public.set('profile_current','vacfan', hvac.get_vacfan())


    # find if hvac has a wake profile actively set and set it to be inline with global morning
    for period in range(0,5):
      if public.get('hvac', 'event_'+str(period)+'_activity') == 'wake':
        hm = public.get('hvac', 'event_'+str(period)+'_on_time')
        hvac_Morning = datetime.datetime.strptime(hm, '%H:%M').time()
        if hvac_Morning != newMorning:
          hvac.set_zone_program_day_period_time(zone, day, period, newMorning.strftime('%H:%M'))
          # make the hvac change
          hvac.pushConfig()

  #########################
  # save any new settings #
  #########################
  saveSettings()
  end = datetime.datetime.now()
  logging.debug('auto_run.py: finished '+str(end-now))
# end mai


if __name__ == "__main__":
  home = myhouse.Home()

  hvacIP = private.get('hvac', 'ip')
  hvacPort = private.get('hvac', 'port')
  hvacFile = private.get('hvac', 'file')
  hvac = pyInfinitude.pyInfinitude.infinitude(hvacIP,hvacPort,hvacFile)

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
      public.set('settings','autorun', sys.argv[3])
      saveSettings()

  saveSettings()
  main(sys.argv[1:])


