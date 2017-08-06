import myhouse
import pyInfinitude.pyInfinitude
import os, sys, datetime, time
import logging
import os

def main(argv):

  now = datetime.datetime.now()
  logging.info('Running set-morn script')

  home = myhouse.Home()

  home.public.set("mornings","updating", "yes")
  home.saveSettings()

  end = datetime.datetime.now()
  logging.debug('finished '+str(end-now))

if __name__ == "__main__":
  main(sys.argv[1:])


