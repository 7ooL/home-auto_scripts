import myhouse
import os, sys, ast, datetime, subprocess
import logging

def main(argv):

  now = datetime.datetime.now()
  home = myhouse.Home(); 

  logging.debug('Running movie script')

  movieFile = sys.argv[1]
  movieFile2 = "/var/www/html/home-auto/movie/movie.txt"

  if home.public.getboolean('settings', 'movie'):
    logging.info('Movie mode toggled off') 
    home.public.set('settings','movie', 'off')
    cs = home.public.get('auto','currentscene')
    home.public.set('auto', 'previousscene', cs)
    logging.debug('previous scene set to'+cs) 
    home.public.set('auto', 'currentscene', 'null')
    logging.debug('current scene set to Null') 
    if home.private.get("Movie","settings") != "Null":
      settings = ast.literal_eval(home.private.get("Movie","settings"))
      logging.debug("restoring: "+str(settings))
      home.public.set("settings","evening", settings['evening'])
      home.public.set("settings","morning", settings['morning'])
      home.public.set("settings","autorun", settings['autorun'])
      home.private.set('Movie','settings', 'Null' )
    # put the lights to the last ,lightState before movie was triggered
    home.playScene(home.private.get('Scenes', 'temp_scene'), home.private.get('HueGroups', 'main_floor'))
    home.public.set('extra','light_state','null')

  else:
    logging.info('Movie mode toggled on') 
    currentSettings={"autorun": home.public.get("settings", "autorun"), "morning": home.public.get("settings", "morning"), "evening": home.public.get("settings", "evening")}
    logging.debug('saving: '+str(currentSettings))
    home.private.set('Movie','settings', currentSettings )
    # save the current light states to temp_scene
    home.saveLightState(home.private.get('HueScenes', 'temp_scene'))
    home.public.set('settings','movie', 'on')
    home.public.set('settings','autorun', 'off')
    logging.debug('autoRun turned off') 
    home.public.set('auto', 'previousscene', home.public.get('auto','currentscene'))
    logging.debug('previous scene set to '+str(home.public.get('auto','currentscene'))) 
    home.public.set('auto','currentscene','movie')
    logging.debug('currenty scene set to movie') 
    home.setTransTimeOfScene( home.private.get('HueScenes', 'movie'), 100)
    home.playScene( home.private.get('HueScenes', 'movie'), home.private.get('HueGroups', 'main_floor'))
    proc = subprocess.Popen(['/usr/local/bin/wemo switch "wemo im home" off'], stdout=subprocess.PIPE, shell=True )
    (out, err) = proc.communicate()
    logging.info('wemo im home turned off')



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
    logging.error("No input file provided")
  elif not os.path.isfile(sys.argv[1]):
    logging.error("Input file does not exist")
  else:
    with open(sys.argv[1]) as f:
      if not f.readline().rstrip():
        logging.error("Input file is empty")
      else:
        main(sys.argv[1])
