import myhouse
import os, sys, datetime
import logging

def main(argv):

  now = datetime.datetime.now()
  home = myhouse.Home();

  logging.debug('Running arrive script')

  arriveFile = "/home/host/Dropbox/IFTTT/arrive/arrive_home.txt"

  run='True'
  # check and see if any one is home, if they are dont change anthing

# comment out this 10/1/2017
# if any one comes home set the home scene. this may be helpful with more than one person

#  for section in home.public.sections():
#    if section == "people_home":
#      for person, value in home.public.items(section):
#        if value == 'yes':
#          run=False
#          logging.debug(person+' already home')

  # set the person who triggered the script as home
  if os.path.isfile(arriveFile):
    with file(arriveFile) as f:
      s = f.readline().rstrip()
      logging.info('marking '+s+' as home')
      home.public.set("people_home", s,"yes")
      home.saveSettings()

  if run:
    logging.debug('Executing RUN()')
    home.public.set('settings','autorun', 'on')
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
