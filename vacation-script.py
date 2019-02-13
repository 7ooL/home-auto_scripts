import myhouse
import os, sys, datetime
import logging

def main(argv):

  now = datetime.datetime.now()
  home = myhouse.Home(); 

  logging.debug('Running vacation script') 

  vacationFile = home.private.get('Path','ifttt')+"/vacation/vacation.txt"
  vacationFile2 = "/var/www/html/home-auto/vacation/vacation.txt"

  home.public.set('settings','autorun', 'on')

  if home.public.getboolean('settings', 'vacation'):
    logging.info('Vacation mode toggled off') 
    home.public.set('settings','vacation', 'off')
    home.public.set('settings','morning', 'on')
  else:
    logging.info('Vacation mode toggled on') 
    home.public.set('settings','vacation', 'on')
    home.public.set('settings','morning', 'off')

  home.saveSettings()

  if os.path.isfile(vacationFile):
    os.remove(vacationFile)
    logging.debug('removeing '+vacationFile)
  if os.path.isfile(vacationFile2):
    os.remove(vacationFile2)
    logging.debug('removeing '+vacationFile2)

  end = datetime.datetime.now()
  logging.debug('finished '+str(end-now))

if __name__ == "__main__":
  main(sys.argv[1:])
