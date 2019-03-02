import myhouse
import os, sys, datetime
import logging

def main(argv):

  now = datetime.datetime.now()
  home = myhouse.Home(); 

  logging.debug('Running vacation script') 

  vacationFile = sys.argv[1]
  logging.debug("vacationFile: "+vacationFile)

  home.public.set('settings','autorun', 'true')

  if home.public.getboolean('settings', 'vacation'):
    logging.info('Vacation mode toggled OFF') 
    home.public.set('settings','vacation', 'false')
    home.public.set('settings','morning', 'true')
  else:
    logging.info('Vacation mode toggled ON') 
    home.public.set('settings','vacation', 'true')
    home.public.set('settings','morning', 'false')

  home.saveSettings()

  if os.path.isfile(vacationFile):
    os.remove(vacationFile)
    logging.debug('removeing '+vacationFile)

  end = datetime.datetime.now()
  logging.debug('finished '+str(end-now))

if __name__ == "__main__":
  if len(sys.argv) == 1:
    logging.error("No input file provided")
  elif not os.path.isfile(sys.argv[1]):
    logging.error("Input file does not exist")
  else:
    main(sys.argv[1])


