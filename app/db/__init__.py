from datetime import datetime

import peewee

from flask import Flask

app = Flask(__name__)

db = peewee.SqliteDatabase("./link-cleaner.db")


@app.before_request
def _db_connect():
    db.connect()


@app.teardown_request
def _db_close(exc):
    if not db.is_closed():
        db.close()


class BaseModel(peewee.Model):
    class Meta:
        database = db


class CleanedLink(BaseModel):
    original_url = peewee.CharField()
    cleaned_url = peewee.CharField(null=True)
    netloc = peewee.CharField(index=True)
    success = peewee.BooleanField(null=True)
    elapsed_time = peewee.FloatField(null=True)
    created_at = peewee.DateTimeField(default=datetime.utcnow)
