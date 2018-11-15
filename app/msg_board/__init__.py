# -*- coding: utf-8 -*-

from flask import Blueprint


msg = Blueprint('msg', __name__)

from . import views