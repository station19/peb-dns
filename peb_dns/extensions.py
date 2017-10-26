# -*- coding: utf-8 -*-

from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

from flask_migrate import Migrate

from flask_mail import Mail
mail = Mail()

from redis import Redis
redis = Redis()
session_redis = Redis()