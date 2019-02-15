import logging
import configparser

def checkSection(file, section):
  if not file.has_section(section):
    logging.warning('missing section '+section)
    try:
      file.add_section(section)
      logging.info('added missing section '+section)
    except:
      logging.error('cannot add section '+section)


def checkOption(file, section, option, placeHolder):
  if not file.has_option(section,option):
    logging.warning('missing option '+option+' in section '+section)
    try:
      file.set(section,option,placeHolder)
      logging.info('added missing option '+option+' in section '+section)
    except:
      logging.error('cannot add '+option+' in section '+section)

def compareOptions(file,section,options):
  a = list(set(options).symmetric_difference(file.options(section)))
  if a:
    logging.warning('options not tested for in section '+str(file)+':'+section)
    logging.warning(a)

def doTest(file,section,options, placeHolder):
  checkSection(file,section)
  for option in options:
    checkOption(file,section,option,placeHolder)
  compareOptions(file,section,options)


private = configparser.RawConfigParser()
private.read('private.ini')

file = private

section = 'Devices'
options = ['hue','kevo','hvac', 'wemo', 'dvr', 'weather', 'ifttt']
placeHolder='false'
doTest(file,section,options,placeHolder)

section = 'Path'
options = ['scriptroot', 'ifttt', "hvac", 'dvr']
placeHolder='/UNDEFINED/HERE'
doTest(file,section,options,placeHolder)

section = 'HueBridge'
options = ['ip','username', 'count_down_lights_active']
placeHolder='UNDEFINED'
doTest(file,section,options,placeHolder)

section = 'Wemo'
options = ['wdevice1_active','wdevice2_active', 'wdevice3_active']
placeHolder='UNDEFINED_DEVICE_NAME'
doTest(file,section,options,placeHolder)

section = 'Kevo'
options = ['username','password']
placeHolder='UNDEFINED'
doTest(file,section,options,placeHolder)

section = 'Time'
options = ['default_last_time','first_time','# trans_percent is a value between 1-99', 'trans_percent','last_time','vaca_on_time','vaca_off_time']
placeHolder='00:00:00'
doTest(file,section,options,placeHolder)

section = 'Scenes'
options = ['scene_1','scene_2','scene_3','scene_4','scene_5','morn_1','daytime_1','daytime_2','bed_1', 'bed_2','movie','home','home_kitchen','home_fireplace','temp_scene','clean_master', 'clean_main', 'office_1', 'office_2', 'office_3', 'office_4', 'office_5', 'office_6', 'office_7', 'basement_chill']
placeHolder='UNDEFINED_ID'
doTest(file,section,options,placeHolder)

section = 'Groups'
options = ['main_floor','master_bedroom', 'count_down_clock', 'kitchen', 'fireplace', 'movie', 'office']
placeHolder='UNDEFINED_ID'
doTest(file,section,options,placeHolder)

section = 'hvac'
options = ['ip','port','file','status','zone']
placeHolder='UNDEFINED'
doTest(file,section,options,placeHolder)

section = 'Movie'
options = ['settings']
placeHolder='UNDEFINED'
doTest(file,section,options,placeHolder)

section = 'dvr'
options = ['recfile','upfile']
placeHolder='UNDEFINED'
doTest(file,section,options,placeHolder)

with open(r'private.ini', 'w') as configfile:
    private.write(configfile)


###
###

public = configparser.RawConfigParser()
public.read('public.ini')

file = public

section = 'mornings'
options = ['0_morning','1_morning','2_morning','3_morning','4_morning','5_morning','6_morning','updating']
placeHolder='00:"00:00'
doTest(file,section,options,placeHolder)

section = 'people_home'
options = ['person_name']
placeHolder='true/false'
doTest(file,section,options,placeHolder)

section = 'auto'
options = ['currentscene','previousscene','morning_1_on_time','daytime_1_on_time','scene_1_on_time','scene_2_on_time','scene_3_on_time','scene_4_on_time','scene_5_on_time','scene_1_trans_time','scene_2_trans_time','scene_3_trans_time','scene_4_trans_time','scene_5_trans_time','morn_1_trans_time','daytime_1_trans_time','scene_test_trans_time','vaca_1_trans_time']
placeHolder='UNDEFINED'
doTest(file,section,options,placeHolder)

section = 'wemo'
options = ['wdevice1_name', 'wdevice1_on_time', 'wdevice1_off_time', 'wdevice1_status', 'wdevice2_name', 'wdevice2_on_time', 'wdevice2_off_time', 'wdevice2_status', 'wdevice3_name', 'wdevice3_on_time', 'wdevice3_off_time', 'wdevice3_status']
placeHolder='UNDEFINED'
doTest(file,section,options,placeHolder)

section = 'settings'
options = ['autorun','morning','hvac_auto','vacation','movie','evening','bed','clean']
placeHolder='UNDEFINED'
doTest(file,section,options,placeHolder)
	
section = 'wakeup_schedule'
options = ['localtime','status']
placeHolder='UNDEFINED'
doTest(file,section,options,placeHolder)

section = 'hvac_current'
options = ['rt','rh','currentactivity','htsp','clsp','fan','hold','hold_time','vaca_running','heat_mode','temp_unit','filtrlvl','humlvl','humid','updating']
placeHolder='UNDEFINED'
doTest(file,section,options,placeHolder)

section = 'profile_current'
options = ['home_clsp','home_htsp','home_fan','sleep_clsp','sleep_htsp','sleep_fan','wake_clsp','wake_htsp','wake_fan','away_clsp','away_htsp','away_fan','vacmaxt','vacmint','vacfan','manual_clsp','manual_htsp','manual_fan']
placeHolder='UNDEFINED'
doTest(file,section,options,placeHolder)

section = 'lock'
options = ['status']
placeHolder='UNDEFINED'
doTest(file,section,options,placeHolder)

section ='hvac'
options =['mode','status','day_0_event_0_on_time','day_0_event_0_activity','day_0_event_1_on_time','day_0_event_1_activity','day_0_event_2_on_time','day_0_event_2_activity','day_0_event_3_on_time','day_0_event_3_activity','day_0_event_4_on_time','day_0_event_4_activity','day_1_event_0_on_time','day_1_event_0_activity','day_1_event_1_on_time','day_1_event_1_activity','day_1_event_2_on_time','day_1_event_2_activity','day_1_event_3_on_time','day_1_event_3_activity','day_1_event_4_on_time','day_1_event_4_activity','day_2_event_0_on_time','day_2_event_0_activity','day_2_event_1_on_time','day_2_event_1_activity','day_2_event_2_on_time','day_2_event_2_activity','day_2_event_3_on_time','day_2_event_3_activity','day_2_event_4_on_time','day_2_event_4_activity','day_3_event_0_on_time','day_3_event_0_activity','day_3_event_1_on_time','day_3_event_1_activity','day_3_event_2_on_time','day_3_event_2_activity','day_3_event_3_on_time','day_3_event_3_activity','day_3_event_4_on_time','day_3_event_4_activity','day_4_event_0_on_time','day_4_event_0_activity','day_4_event_1_on_time','day_4_event_1_activity','day_4_event_2_on_time','day_4_event_2_activity','day_4_event_3_on_time','day_4_event_3_activity','day_4_event_4_on_time','day_4_event_4_activity','day_5_event_0_on_time','day_5_event_0_activity','day_5_event_1_on_time','day_5_event_1_activity','day_5_event_2_on_time','day_5_event_2_activity','day_5_event_3_on_time','day_5_event_3_activity','day_5_event_4_on_time','day_5_event_4_activity','day_6_event_0_on_time','day_6_event_0_activity','day_6_event_1_on_time','day_6_event_1_activity','day_6_event_2_on_time','day_6_event_2_activity','day_6_event_3_on_time','day_6_event_3_activity','day_6_event_4_on_time','day_6_event_4_activity']
placeHolder='UNDEFINED'
doTest(file,section,options,placeHolder)

section = 'weather'
options = ['weather','ot','oh','icon','icon_url','forecast_url']
placeHolder='UNDEFINED'
doTest(file,section,options,placeHolder)

section = 'extra'
options = ['light_state']
placeHolder='UNDEFINED'
doTest(file,section,options,placeHolder)

placeHolder='{}'
section = 'dvr'
options = ['0_shows','1_shows','2_shows','3_shows','4_shows','5_shows','6_shows','7_shows']
placeHolder='UNDEFINED'
doTest(file,section,options,placeHolder)

section = 'dvrRecorded'
options = ['shows']
placeHolder='UNDEFINED'
doTest(file,section,options,placeHolder)

with open(r'public.ini', 'w') as configfile2:
    public.write(configfile2)
                    
