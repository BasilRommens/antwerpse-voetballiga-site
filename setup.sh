#!/bin/bash

sudo docker-compose -f docker-compose-dev.yml up -d --build
sudo docker-compose -f docker-compose-dev.yml run database python manage.py recreate-db
sudo docker-compose -f docker-compose-dev.yml run database python manage.py seed-db
xdg-open 'http://0.0.0.0:5004/'
