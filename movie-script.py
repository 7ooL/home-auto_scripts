import myhouse
import os, ast, datetime
import sys, getopt
import logging

now = datetime.datetime.now()
movieFile = "/home/host/Dropbox/IFTTT/movie/movie.txt"
movieFile2 = "/var/www/html/home-auto/movie/movie.txt"
home = myhouse.Home(); 

def writeCurrentSettings():
  currentSettings={"autorun": home.public.get("settings", "autorun"), "morning": home.public.get("settings", "morning"), "evening": home.public.get("settings", "evening")}
  logging.debug('movie-script.writeCurrentSettings: '+str(currentSettings))
  home.private.set('Movie','settings', currentSettings )

def setPreviousSettings():
  if home.private.get("Movie","settings") != "Null":
    settings = ast.literal_eval(home.private.get("Movie","settings"))
    home.public.set("settings","evening", settings['evening'])
    home.public.set("settings","morning", settings['morning'])
    home.public.set("settings","autorun", settings['autorun'])
    home.private.set('Movie','settings', 'Null' )
    logging.debug('movie-script.setPreviousSettings: '+str(settings))
  else:
    logging.info('movie-script.setPreviousSettings: Already NULL')


def main(argv):

  if home.public.getboolean('settings', 'movie'):
    logging.info('movie-script: Deactivated') 
    logging.debug('movie-script.py: movie mode toggled off') 
    home.public.set('settings','movie', 'off')
    cs = home.public.get('auto','currentscene')
    home.public.set('auto', 'previousscene', cs)
    logging.debug('movie-script.py: previous scene set to'+cs) 
    home.public.set('auto', 'currentscene', 'null')
    logging.debug('movie-script.py: previous scene set to Null') 
    setPreviousSettings()
    # put the lights to the last ,lightState before movie was triggered
    home.playScene(home.private.get('Scenes', 'temp_scene'), home.private.get('Groups', 'main_floor'))
    home.public.set('extra','light_state','null')
  else:
    logging.info('movie-script: Activated') 
    writeCurrentSettings()
    # save the current light states to temp_scene
    home.saveLightState(home.private.get('Scenes', 'temp_scene'))
    home.public.set('settings','movie', 'on')
    logging.debug('movie-script.py: movie mode toggled on') 
    home.public.set('settings','autorun', 'off')
    logging.debug('movie-script.py: autoRun turned off') 
    home.public.set('auto', 'previousscene', home.public.get('auto','currentscene'))
    logging.debug('movie-script.py: previous scene set to'+str(home.public.get('auto','currentscene'))) 
    home.public.set('auto','currentscene','movie')
    logging.debug('movie-script.py: currenty scene set to movie') 
    home.setTransTimeOfScene( home.private.get('Scenes', 'movie'), 100)
    home.playScene( home.private.get('Scenes', 'movie'), home.private.get('Groups', 'main_floor'))

  home.saveSettings()

  if os.path.isfile(movieFile):
    os.remove(movieFile)
    logging.debug('movie-script: removeing '+movieFile)
  if os.path.isfile(movieFile2):
    os.remove(movieFile2)
    logging.debug('movie-script: removeing '+movieFile2)

  end = datetime.datetime.now()
  logging.debug('finished '+str(end-now))


if __name__ == "__main__":
  main(sys.argv[1:])
