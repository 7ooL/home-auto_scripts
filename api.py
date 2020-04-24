from flask import Flask, jsonify

import configparser
import json, os, random, subprocess
import myhouse
import configparser

app = Flask(__name__)
#CORS(app)
# unable to use global configparser myhouse.home as it reamined static for the life of the app

@app.route("/")
def default():
  moddate = os.path.getmtime(RootPATH+'public.ini')
  return jsonify({'lastModifed':moddate})

@app.route("/people", methods=["GET"])
def getPeople():
  public = configparser.RawConfigParser()
  public.read(RootPATH+'public.ini')
  people = []
  for person, value in public.items("people_home"):
    people.append({'name':person, 'home':value})
  return jsonify(people)

@app.route("/people/<name>", methods=["GET"])
def getPerson(name):
  try:
    public = configparser.RawConfigParser()
    public.read(RootPATH+'public.ini')
    person = {'home':public.getboolean("people_home",name)}
    return jsonify(person)
  except configparser.NoOptionError:
    return not_found(name)

@app.route("/people", methods=["POST"])
def togglePerson():
  if request.data is None:
    return jsonify({"result":"bad rquest"},400)
  try:
    person = request.json['name']
    status = json.loads(getPerson(person).data.decode('utf8'))
    private = configparser.RawConfigParser()
    private.read(RootPATH+'private.ini')
    if status['home']:
      filename = "API-leave-"+str(random.randint(1,21))
      os.system("echo " +person+" > "+filename)
      os.system("mv "+filename+" "+private.get('Path','watch_dir')+'/leave')
      return jsonify({"result":person+" set as away"})

    else:
      filename = "API-arrive-"+str(random.randint(1,21))
      os.system("echo " +person+" > "+filename)
      os.system("mv "+filename+" "+private.get('Path','watch_dir')+'/arrive')
      return jsonify({"result":person+" set as home"})

  except KeyError:
    return not_found(request.json['name'])


@app.route("/log", methods=["GET"])
def getLog():
  f = subprocess.Popen(['tail','-n 1','home-auto.log'],\
        stdout=subprocess.PIPE,stderr=subprocess.PIPE)
  log = {'log':f.stdout}
  print(log)
#  return log


@app.errorhandler(404)
def not_found(thing, error=None):
    message = {
            'status': 404,
            'message': 'Not Found: ' + str(thing)
    }
    resp = jsonify(message)
    resp.status_code = 404

    return resp

if __name__ == '__main__':

  home = myhouse.Home()
  RootPATH = home.private.get('Path','scriptroot')+'/'

  app.run(
	debug=True,
	host=home.private.get('Server','host'),
	port=home.private.get('Server','port')
	)


