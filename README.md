# Information on web files for the Genetic Links to Health project
___

This repository is for the website at [http://www.genediseaselink.com](http://www.genediseaselink.com).

The website is a heroku app that uses Python 3 and the [flask framework](http://flask.pocoo.org/). Flask uses a Python WSGI library to ensure the app and webserver communicate smoothly and jinja to create webpage templates. Deployment on Heroku uses a git-based interface for convenience.

Important files:

* Application dependencies are stored in `requirements.txt`.

* The `Procfile` sends a command to the heroku server to start a web dyno and the name of the web app to run.

* `app.py` contains the python script where the flask framework is created and the visualizations are processed.

* Folders `templates` and `static` contain html, css, images and other media to be displayed on the website.
