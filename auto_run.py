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

  lm = public.get('auto','morning_1_on_time')
  if lm != 'null':
    light_Morning = datetime.datetime.strptime(lm, '%H:%M:%S').time()
    if newMorning != light_Morning:
      # set light scene morning 
      public.set('auto','morning_1_on_time', newMorning)
      saveSettings()

  wm = public.get('wakeup_schedule','localtime').split("T",1)[1]
  if wm != 'null':
    wake_Morning = datetime.datetime.strptime(wm, '%H:%M:%S').time()
    if newMorning != wake_Morning:
      # set bedroom wake schedule 
      home.setLightScheduleTime(1,newMorning)

  hm = public.get('hvac', 'event_1_on_time')
  if hm != 'null':
    hvac_Morning = datetime.datetime.strptime(hm, '%H:%M').time()
 #  if newMorning != hvac_Morning:
      # set HVAC wake time if different
   #   payload = {'time': newMorning.hour+':'newMorning.minute}
   #   home.setHVACzonedata



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

  # set eveing start and end times to default if before first start time, so it auto is on before then it works
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

    #end of bed check, bed is on, check that its past that last_time and turn it off 
   # else:
   #   if now <= now.replace(hour=int(ls_bed[0]), minute=int(ls_bed[1]), second=int(ls_bed[2])):
   #     logging.info('autoRun: end of bed check '+str(now.replace(hour=int(ls_bed[0]), minute=int(ls_bed[1]), second=int(ls_bed[2])))+' <= '+str(now)) 
   #     public.set('settings', 'evening', 'on')

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
  

  zonedata = home.getHVACzonedata()
  if (zonedata == "Error"):
    public.set('hvac','status','error')
  else:
    public.set('hvac','status','ok')
    # adjust days of week num to allign with carrier and infinitude numbering
    todayNum = (int(datetime.datetime.today().weekday())+1)
    if todayNum == 7:
      todayNum = 0

    # clear out todays schedule, do this after the queries are made so it is faster
    for x in [1,2,3,4]:
      public.set('hvac', "event_"+str(x)+"_on_time", 'null')
      public.set('hvac', "event_"+str(x)+"_activity", 'null')
    # get the HVAC mode
    public.set('hvac','mode', home.getHVACmode());

    # pull out today's hvac activity and times for schedule, insert it into config file
    x=1
    for period in zonedata['data']['zone'][0]['program'][0]['day'][todayNum]['period']:
      if period['enabled'] == ['on']:
        public.set('hvac', "event_"+str(x)+"_on_time", str(period['time']).replace('[u\'' ,'').replace("\']",""))
        public.set('hvac', "event_"+str(x)+"_activity", str(period["activity"]).replace('[u\'','').replace("\']",""))
        x+=1

    # pull out clsp and htsp for each profile
    x=0
    for activity in zonedata['data']['zone'][0]['activities'][0]['activity']:
      public.set('profile_current', activity['id']+'_fan', str(activity['fan']).replace('[u\'','').replace("\']",""))
      public.set('profile_current', activity['id']+'_clsp', str(activity['clsp']).replace('[u\'','').replace("\']",""))
      public.set('profile_current', activity['id']+'_htsp', str(activity['htsp']).replace('[u\'','').replace("\']",""))

    vacaData = home.getHVACvacaData()
    public.set('profile_current','vacmaxt', vacaData['vacmaxt'])
    public.set('profile_current','vacmint', vacaData['vacmint'])
    public.set('profile_current','vacfan', vacaData['vacfan'])


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


