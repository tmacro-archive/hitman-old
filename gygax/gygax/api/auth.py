import json
import requests
from flask import Blueprint, request, url_for, session, redirect
from ..app import db
from ..util.config import config
from ..util.log import getLogger

_log = getLogger('api.auth')
