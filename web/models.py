from flask_login import UserMixin

from web import db


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    twitch_id = db.Column(db.Integer)
    twitch_login_name = db.Column(db.String)
    twitch_display_name = db.Column(db.String)
    bot_enabled = db.Column(db.Boolean, nullable=False)
    guessables = db.relationship("Guessable")

    def __init__(self, twitch_id, twitch_login_name, twitch_display_name):
        self.twitch_id = twitch_id
        self.twitch_login_name = twitch_login_name
        self.twitch_display_name = twitch_display_name
        self.bot_enabled = False

    def __repr__(self):
        return f'<id: {self.id} login: {self.twitch_login_name}>'

    def get_bot_enabled(self):
        return self.bot_enabled

    def get_id(self):
        return self.id

    def change_bot_enabled(self):
        self.bot_enabled = not self.bot_enabled
        db.session.commit()
        return self.bot_enabled

    @staticmethod
    def get_user_by_twitch_id(twitch_id):
        return User.query.filter_by(twitch_id=twitch_id).first()

    @staticmethod
    def get_user_by_id(id):
        return User.query.filter_by(id=id).first()


class Guessable(db.Model):
    from sqlalchemy.dialects.postgresql import UUID
    from uuid import uuid4

    __tablename__ = 'guessables'

    uuid = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = db.Column(db.String)
    variations = db.Column(db.PickleType)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __init__(self, name, variations):
        self.name = name
        self.varations = variations

    def __repr__(self):
        return f'<guessable uuid: {self.uuid}>'
