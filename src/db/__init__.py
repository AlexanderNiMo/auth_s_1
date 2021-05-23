from .postgres import db
from .postgres import init_db
from .base import FastDB
from .redis import create_fast_db

fast_db: FastDB = None

