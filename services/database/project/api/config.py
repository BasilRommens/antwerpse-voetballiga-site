from flask import Blueprint, jsonify, request
from sqlalchemy import exc

from project.api.models import *
from project import db
