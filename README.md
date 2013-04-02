# MGWebRTC Demo

A simple web application to demonstrate WebRTC video conference. 

## Development

### Prepare environment

    $ git clone git@github.com:Avamagic/mgwebrtc-demo
    $ cd mgwebrtc-demo
    $ virtualenv .venv
    $ source .venv/bin/activate
    $ pip install -r requirements.txt

### Run on local machine

    $ python manager.py runserver --host 0.0.0.0 --threaded

### Unit test

    $ nosetests --with-coverage --cover-package=mgwebrtc
