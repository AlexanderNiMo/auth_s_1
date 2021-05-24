from .base import FastDB
from .postgres import db
from .postgres import init_db
from .redis import create_fast_db

fast_db: FastDB = None
