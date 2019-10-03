import os
import base64
import datetime

from flask import current_app

from notifico.db import db


class Hook(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.TIMESTAMP(), default=datetime.datetime.utcnow)
    key = db.Column(db.String(255), nullable=False)
    service_id = db.Column(db.Integer)
    config = db.Column(db.PickleType)

    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    project = db.relationship('Project', backref=db.backref(
        'hooks', order_by=id, lazy='dynamic', cascade='all, delete-orphan'
    ))

    message_count = db.Column(db.Integer, default=0)

    @classmethod
    def new(cls, service_id, config=None):
        p = cls()
        p.service_id = service_id
        p.key = cls._new_key()
        p.config = config
        return p

    @staticmethod
    def _new_key():
        return base64.urlsafe_b64encode(os.urandom(24))[:24]

    @classmethod
    def by_service_and_project(cls, service_id, project_id):
        return cls.query.filter_by(
            service_id=service_id,
            project_id=project_id
        ).first()

    @property
    def hook(self):
        return current_app.enabled_hooks[self.service_id]

    def absolute_url(self):
        hook = self.hook
        try:
            hook_url = hook.absolute_url(self)
            return hook_url
        except NotImplementedError:
            return None
