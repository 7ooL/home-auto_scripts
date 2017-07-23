import myhouse
import os, ast
import sys, getopt
import logging
import ConfigParser

public = ConfigParser.RawConfigParser()
public.read('/home/host/home_auto_scripts/public.ini')

private = ConfigParser.RawConfigParser()
private.read('/home/host/home_auto_scripts/private.ini')

movieFile = "/home/host/Dropbox/IFTTT/movie/movie.txt"
movieFile2 = "/var/www/html/home-auto/movie/movie.txt"


def saveSettings():
  with open(r'/home/host/home_auto_scripts/public.ini', 'wb') as configfile:
    public.write(configfile)
  with open(r'/home/host/home_auto_scripts/private.ini', 'wb') as configfile:
    private.write(configfile)

def writeCurrentSettings():
  currentSettings={"autorun": public.get("settings", "autorun"), "morning":public.get("settings", "morning"), "evening":public.get("settings", "evening")}
  logging.debug('movie-script.writeCurrentSettings: '+str(currentSettings))
  private.set('Movie','settings', currentSettings )

def setPreviousSettings():
  if private.get("Movie","settings") != "Null":
    settings = ast.literal_eval(private.get("Movie","settings"))
    public.set("settings","evening", settings['evening'])
    public.set("settings","morning", settings['morning'])
    public.set("settings","autorun", settings['autorun'])
    private.set('Movie','settings', 'Null' )
    logging.debug('movie-script.setPreviousSettings: '+str(settings))
  else:
    logging.info('movie-script.setPreviousSettings: Already NULL')


def main(argv):

  home = myhouse.Home(); 

  if public.getboolean('settings', 'movie'):
    logging.info('movie-script: Deactivated') 
    logging.debug('movie-script.py: movie mode toggled off') 
    public.set('settings','movie', 'off')
    cs = public.get('auto','currentscene')
    public.set('auto', 'previousscene', cs)
    logging.debug('movie-script.py: previous scene set to'+cs) 
    public.set('auto', 'currentscene', 'null')
    logging.debug('movie-script.py: previous scene set to Null') 
    setPreviousSettings()
    # put the lights to the last ,lightState before movie was triggered
    home.playScene(private.get('Scenes', 'temp_scene'), private.get('Groups', 'main_floor'))
    public.set('extra','light_state','null')
  else:
    logging.info('movie-script: Activated') 
    writeCurrentSettings()
    # save the current light states to temp_scene
    home.saveLightState(private.get('Scenes', 'temp_scene'))
    public.set('settings','movie', 'on')
    logging.debug('movie-script.py: movie mode toggled on') 
    public.set('settings','autorun', 'off')
    logging.debug('movie-script.py: autoRun turned off') 
    public.set('auto', 'previousscene', public.get('auto','currentscene'))
    logging.debug('movie-script.py: previous scene set to'+str(public.get('auto','currentscene'))) 
    public.set('auto','currentscene','movie')
    logging.debug('movie-script.py: currenty scene set to movie') 
    home.setTransTimeOfScene( private.get('Scenes', 'movie'), 100)
    home.playScene( private.get('Scenes', 'movie'), private.get('Groups', 'main_floor'))

  saveSettings()

  if os.path.isfile(movieFile):
    os.remove(movieFile)
    logging.debug('movie-script: removeing '+movieFile)
  if os.path.isfile(movieFile2):
    os.remove(movieFile2)
    logging.debug('movie-script: removeing '+movieFile2)

  logging.debug('movie-script.py: END') 

if __name__ == "__main__":
  main(sys.argv[1:])
