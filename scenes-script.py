
import myhouse
import os, sys, ast, time, datetime
import logging

def main(argv):

  now = datetime.datetime.now()
  home = myhouse.Home()

  scenesFile = "/var/www/html/home-auto/scenes/scenes.txt"

  # read the scene name form the file
  if os.path.isfile(scenesFile):
    with file(scenesFile) as f:
      s = f.readline().rstrip()
      current_status = home.public.get('light_scenes',s)
      if current_status == 'on':
        home.public.set("light_scenes", s, 'off')
        home.playScene(home.private.get('Scenes', 'temp_scene'), home.private.get('Groups', s))
      else:
        logging.info('triggering '+s+' scene')
        home.public.set("light_scenes", s, 'on')
        home.saveLightState(home.private.get('Scenes', 'temp_scene'))

        # switch case for custom scenes
        home.playScene(home.private.get('Scenes', s), home.private.get('Groups',s))

  # save new settings
  home.saveSettings()

  # remove file that triggered script
  if os.path.isfile(scenesFile):
    os.remove(scenesFile)
    logging.debug('removeing '+scenesFile)

  end = datetime.datetime.now()
  logging.debug('play scenes finished '+str(end-now))

if __name__ == "__main__":
  main(sys.argv[1:])

