import myhouse
import os, sys, datetime
import logging

def main(argv):

  now = datetime.datetime.now()
  home = myhouse.Home();

  logging.debug('Running arrive script')

  arriveFile = "/home/host/Dropbox/IFTTT/arrive/arrive_home.txt"

  run=False

  # check and see if any one is home, if they are dont change anthing
#  for section in home.public.sections():
#    if section == "people_home":
#      for person, value in home.public.items(section):
#        if value == 'yes':
#          run=False
#          logging.info(person+' already home')


  # set the person who triggered the script as home
  if os.path.isfile(arriveFile):
    with file(arriveFile) as f:
      s = f.readline().rstrip()
      current_status = home.public.get('people_home',s)
      if current_status == 'yes':
        logging.info(s+' arrived, but is already home')
      else:
        logging.info('marking '+s+' as home')
        home.public.set("people_home", s,"yes")
        home.saveSettings()
        run=True



  if run:
    logging.info('Executing RUN()')
    home.public.set('settings','autorun', 'on')
    # dont play home if in movie mode
    if home.public.get('settings','movie') == 'off':
      home.playScene(home.private.get('Scenes', 'home'), home.private.get('Groups','main_floor')) 
      home.public.set('auto', 'currentscene', 'home')
      home.saveSettings()

  # remove file that triggered script
  if os.path.isfile(arriveFile):
    logging.debug('removeing '+arriveFile)
    os.remove(arriveFile)

  end = datetime.datetime.now()
  logging.debug('finished '+str(end-now))

if __name__ == "__main__":
  main(sys.argv[1:])
