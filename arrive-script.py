import myhouse
import os, sys, datetime, random
import logging

def main(argv):

  now = datetime.datetime.now()
  home = myhouse.Home();

  logging.debug('Running arrive script')

#  arriveFile = home.private.get('Path','ifttt')+"/arrive/arrive_home.txt"
  arriveFile = sys.argv[1]
  logging.debug("arriveFile: "+arriveFile)

  run=False

  # set the person who triggered the script as home
  if os.path.isfile(arriveFile):
    with open(arriveFile) as f:
      s = f.readline().rstrip()
      if home.public.getboolean('people_home',s):
        logging.info(s+' arrived, but is already home')
      else:
        logging.info('marking '+s+' as home')
        home.public.set("people_home", s,"true")
        home.saveSettings()
        run=True


  if run:
    logging.info('Executing RUN()')
    home.public.set('settings','autorun', 'true')
    if home.private.getboolean('Devices','hue'):
      home.playScene(home.private.get('HueScenes', 'home'), home.private.get('HueGroups','main_floor')) 
      home.playScene(home.private.get("HueScenes", "office_"+str(random.randint(1,7))), home.private.get('HueGroups','office'))
      home.playScene(home.private.get("HueScenes", "clean_master"), home.private.get('HueGroups','master_bedroom'))
    if home.private.getboolean('Devices','decora'):
      home.decora(home.private.get('Decora', 'switch_1'), "ON", "75")
      home.decora(home.private.get('Decora', 'switch_4'), "ON", "75")
      home.decora(home.private.get('Decora', 'switch_3'), "ON", "None")

    home.public.set('auto', 'currentscene', 'home')
    home.saveSettings()

  # remove file that triggered script
  if os.path.isfile(arriveFile):
    logging.debug('removeing '+arriveFile)
    os.remove(arriveFile)

  end = datetime.datetime.now()
  logging.debug('finished '+str(end-now))

if __name__ == "__main__":

  if len(sys.argv) == 1:
    logging.error("No input file provided")
  elif not os.path.isfile(sys.argv[1]):
    logging.error("Input file does not exist")
  else:
    with open(sys.argv[1]) as f:
      if not f.readline().rstrip():
        logging.error("Input file is empty")
      else:
        main(sys.argv[1])
