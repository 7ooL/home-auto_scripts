import myhouse
import os, sys, datetime, time
import logging
import os

def main(argv):

  now = datetime.datetime.now()
  logging.debug('Running updater script')

  home = myhouse.Home()

  if home.public.get('mornings', 'updating') == 'yes':

    logging.debug('updating was yes')
    file = open('/var/www/html/home-auto/morn/set_morn.txt','r')
    words = file.readline()
    file.close()
    line = words.split(",")
    cd = line[0]
    day = line[1]
    until = line[2]
    logging.debug('date: '+cd+' day: '+day+' time: '+until)
    home.public.set('mornings', day+'_morning', until+":00");
    home.public.set('mornings', 'updating', 'no')
    home.saveSettings();

  end = datetime.datetime.now()
  logging.debug('finished '+str(end-now))

if __name__ == "__main__":
  main(sys.argv[1:])


