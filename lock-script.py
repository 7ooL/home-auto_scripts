import myhouse
import os, sys, datetime
import logging

def main(argv):

  now = datetime.datetime.now()
  home = myhouse.Home(); 

  lockFile = home.private.get('Path','ifttt')+"/lock/lock.txt"
  lockFile2 = "/var/www/html/home-auto/lock/lock.txt"

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

  if os.path.isfile(lockFile):
    os.remove(lockFile)
    logging.debug('lock-script: removeing '+lockFile)
  if os.path.isfile(lockFile2):
    os.remove(lockFile2)
    logging.debug('lock-script: removeing '+lockFile2)

  end = datetime.datetime.now()
  logging.debug('finished '+str(end-now))

if __name__ == "__main__":
  main(sys.argv[1:])
