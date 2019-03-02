import sys
import argparse
import logging
import configparser

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

WRITE = False

def checkSection(file, section):
  if not file.has_section(section):
      logging.warning(' ** missing section '+section+" **")
      if WRITE:
          try:
              file.add_section(section)
              logging.info(' added missing section '+section)
              return True
          except:
              logging.error(' cannot add section '+section)
              return False
      else:
          return False
  else:
     logging.info("    Section - "+section)
     return True


def checkOption(file, section, option, placeHolder):
    if not file.has_option(section,option):
        logging.warning(' missing option '+option+' in section '+section)
        if WRITE:
            try:
                file.set(section,option,placeHolder)
                logging.info(' added missing option '+option+' in section '+section)
            except:
                logging.error(' cannot add '+option+' in section '+section)

def compareOptions(file,section,options):
    a = list(set(options).symmetric_difference(file.options(section)))
    if a:
        a.sort()
        logging.warning(" Missing - "+str(a))

def doTest(file,section,options, placeHolder):
    options.sort()
    if checkSection(file,section):
        for option in options:
            checkOption(file,section,option,placeHolder)
        compareOptions(file,section,options)

def privateFile():

    private = configparser.RawConfigParser()
    private.read('private.ini')

    file = private

    section = 'Devices'
    options = ['decora', 'dropbox', 'dvr', 'gmail', 'hue', 'hvac', 'kevo', 'vivint', 'weather', 'wemo']
    placeHolder='false'
    doTest(file,section,options,placeHolder)

    section = 'Path'
    options = ['dvr', 'hvac', 'scriptroot', 'watch_dir']
    placeHolder='/UNDEFINED/HERE'
    doTest(file,section,options,placeHolder)

    section = 'HueBridge'
    options = ['ip','username', 'count_down_lights_active', 'alarm_use']
    placeHolder='UNDEFINED'
    doTest(file,section,options,placeHolder)

    section = 'HueScenes'
    options = ['clean_all', 'movie', 'movie_chill', 'office_1', 'office_2', 'office_3', 'office_4', 'office_5', 'office_6', 'office_7', 'temp_scene', 'zone0_daytime_0', 'zone0_evening_0', 'zone0_evening_1', 'zone0_home', 'zone0_morning_0', 'zone1_daytime_0', 'zone1_evening_0', 'zone1_evening_1', 'zone1_home', 'zone1_morning_0', 'zone2_evening_0', 'zone2_evening_1', 'zone2_evening_2', 'zone2_evening_3', 'zone2_evening_4', 'zone2_home']
    placeHolder='UNDEFINED_ID'
    doTest(file,section,options,placeHolder)

    section = 'HueGroups'
    options = ['basement_floor', 'basement_hall', 'count_down_clock', 'main_floor', 'movie', 'office', 'zone0', 'zone1', 'zone2']
    placeHolder='UNDEFINED_ID'
    doTest(file,section,options,placeHolder)

    section = 'Wemo'
    options = ['wdevice1_active','wdevice2_active', 'wdevice3_active']
    placeHolder='UNDEFINED_DEVICE_NAME'
    doTest(file,section,options,placeHolder)

    section = 'Kevo'
    options = ['username','password']
    placeHolder='UNDEFINED'
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

    if WRITE:
        with open(r'private.ini', 'w') as configfile:
            private.write(configfile)


def publicFile():

    public = configparser.RawConfigParser()
    public.read('public.ini')

    file = public

    section = 'settings'
    options = ['autorun', 'bedtime', 'clean', 'daytime', 'hvac_auto', 'morning', 'movie', 'vacation', 'zone0_evening', 'zone1_evening', 'zone2_evening']
    placeHolder='false'
    doTest(file,section,options,placeHolder)

    section = 'mornings'
    options = ['0_morning','1_morning','2_morning','3_morning','4_morning','5_morning','6_morning','updating']
    placeHolder='00:00:00'
    doTest(file,section,options,placeHolder)

    section = 'people_home'
    options = ['name']
    placeHolder='false'
    doTest(file,section,options,placeHolder)

    section = 'zone0'
    options = ['currentscene', 'daytime_0_on_time', 'daytime_0_trans_time', 'default_last_time', 'evening_0_on_time', 'evening_1_on_time', 'evening_first_time', 'evening_trans_time', 'last_time', 'morning_0_on_time', 'morning_0_trans_time', 'previousscene']
    placeHolder='UNDEFINED'
    doTest(file,section,options,placeHolder)

    section = 'zone1'
    options = ['currentscene', 'daytime_0_on_time', 'daytime_0_trans_time', 'default_last_time', 'evening_0_on_time', 'evening_1_on_time', 'evening_first_time', 'evening_trans_time', 'last_time', 'morning_0_on_time', 'morning_0_trans_time', 'previousscene']
    placeHolder='UNDEFINED'
    doTest(file,section,options,placeHolder)

    section = 'zone2'
    options = ['currentscene', 'default_last_time', 'evening_0_on_time', 'evening_1_on_time', 'evening_2_on_time', 'evening_3_on_time', 'evening_4_on_time', 'evening_first_time', 'evening_trans_time', 'last_time', 'previousscene']
    placeHolder='UNDEFINED'
    doTest(file,section,options,placeHolder)

    section = 'wemo'
    options = ['wdevice1_name', 'wdevice1_on_time', 'wdevice1_off_time', 'wdevice1_status', 'wdevice2_name', 'wdevice2_on_time', 'wdevice2_off_time', 'wdevice2_status', 'wdevice3_name', 'wdevice3_on_time', 'wdevice3_off_time', 'wdevice3_status']
    placeHolder='UNDEFINED'
    doTest(file,section,options,placeHolder)

    section = 'wakeup_schedule'
    options = ['work_localtime','work_status','weekend_localtime','weekend_status']
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

    if WRITE:
        with open(r'public.ini', 'w') as configfile2:
          public.write(configfile2)

def main(argv):

    parser = argparse.ArgumentParser(description="This script will help with the creation of the public.ini and private.ini files used in Home-Auto. It will create placeholders when necessary.")
    group = parser
    group.add_argument("-w", "--write", action="store_true", help="write the sections/options to file")
    group.add_argument("-pr", "--private", action="store_true", help="test the private.ini file")
    group.add_argument("-pu", "--public", action="store_true", help="test the public.ini file")
    args = parser.parse_args()

    if args.write:
        WRITE = True
    if args.public:
        publicFile()
    if args.private:
        privateFile()

if __name__ == "__main__":
    ret = main(sys.argv)
    if ret is not None:
        sys.exit(ret)


