from sqlalchemy import (create_engine, MetaData, Integer)
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
import app
db = SQLAlchemy()

class BaseModel(object):
    @classmethod
    def new(cls, **kwargs):
        obj = cls(**kwargs)
        db.session.add(obj)
        db.session.commit()
        return obj

    @classmethod
    def get(cls, **kwargs):
        result = cls.query.filter_by(**kwargs).first()
        return result

    @classmethod
    def get_all(cls, **kwargs):
        result = cls.query.filter_by(**kwargs).all()
        return result

    def update(self, **kwargs):
        for column, value in kwargs.items():
            setattr(self, column, value)

        db.session.add(self)
        db.session.commit()
        return self

    def __repr__(self):
        columns = dict((column.name, getattr(self, column.name)) for column in self.__table__.columns)
        
        column_strings = []
        for column, value in columns.items():
            column_strings.append(f'{column}: {value}')

        repr = f"<{self.__class__.__name__} {', '.join(column_strings)}>"
        return repr


class Soccer_standings(BaseModel, db.Model):
    __tablename__ = 'soccer_standings'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    league_name = db.Column(db.String(255))
    league_code = db.Column(db.String(255))
    season_year = db.Column(db.Integer)
    team_name =db.Column(db.String(255))
    gp = db.Column(db.Integer)
    w = db.Column(db.Integer)
    d = db.Column(db.Integer)
    l = db.Column(db.Integer)
    f = db.Column(db.Integer)
    a = db.Column(db.Integer)
    gd = db.Column(db.Integer)  	
    p = db.Column(db.Integer)  
