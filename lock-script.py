import myhouse
import os, sys, datetime
import logging

def main(argv):

  now = datetime.datetime.now()
  home = myhouse.Home(); 

  logging.debug('Running lock script')

  if home.private.getboolean('Devices', 'kevo'):

    lockFile = sys.argv[1]
    logging.debug("lockFile: "+lockFile)

    lockState = home.public.get('lock', 'status')

    # toggle the lock state
    if lockState == "Unlocked":
       logging.info('Locked Door')
       home.kevo("lock")
       home.public.set('lock', 'status', "Locked") #  auto-run will query state every 5 mintes, set now to update web-interface
    else:
       logging.info('Unlocked Door')
       home.kevo("unlock")
       home.public.set('lock', 'status', "Unlocked")

    home.saveSettings()

  else:
    logging.warning('kevo use not enabled')



  if os.path.isfile(lockFile):
    os.remove(lockFile)
    logging.debug('removeing '+lockFile)

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

