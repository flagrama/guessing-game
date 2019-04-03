from datetime import datetime, timezone

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
    participants = db.relationship("Participant")
    results = db.relationship("Result")

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

    def count_user_guessables(self):
        return len(self.guessables)

    def get_user_guessable(self, uuid):
        return Guessable.get_guessable_by_uuid(uuid, self.id)

    def get_user_guessables(self):
        return self.guessables[:30]

    def get_all_user_guessables(self):
        return self.guessables

    def get_user_results(self):
        self.results.sort(reverse=True, key=lambda r: r.datetime)
        return self.results

    def get_user_result(self, uuid):
        return Result.get_result_by_uuid(uuid, self.id)

    @staticmethod
    def get_user_by_twitch_login_name(twitch_login_name):
        return User.query.filter_by(twitch_login_name=twitch_login_name).first()

    @staticmethod
    def get_user_by_twitch_id(twitch_id):
        return User.query.filter_by(twitch_id=twitch_id).first()

    @staticmethod
    def get_user_by_id(user_id):
        return User.query.filter_by(id=user_id).first()

    @staticmethod
    def get_all_users_with_bot_enabled():
        return User.query.filter_by(bot_enabled=True).all()


class Participant(db.Model):
    from sqlalchemy.dialects.postgresql import UUID
    from uuid import uuid4

    __tablename__ = 'participants'

    uuid = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = db.Column(db.String)
    twitch_id = db.Column(db.Integer)
    points = db.Column(db.Integer, default=0)
    current_points = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def create_participant(self, name, twitch_id, user_id):
        self.name = name
        self.twitch_id = twitch_id
        self.user_id = user_id
        db.session.add(self)
        db.session.commit()

    def add_points(self, n):
        self.points += n
        db.session.commit()

    @staticmethod
    def get_participant_by_twitch_ids(user_twitch_id, participant_twitch_id):
        return Participant.query.join(User).filter(
            User.twitch_id == user_twitch_id).filter(Participant.twitch_id == participant_twitch_id).first()

    @staticmethod
    def get_participant_points_by_twitch_ids(user_twitch_id, participant_twitch_id):
        return Participant.query.join(User).with_entities(Participant.points).filter(
            User.twitch_id == user_twitch_id).filter(Participant.twitch_id == participant_twitch_id).first()[0]


class Result(db.Model):
    from sqlalchemy.dialects.postgresql import UUID, JSONB
    from uuid import uuid4

    __tablename__ = 'results'

    uuid = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    datetime = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    results = db.Column(JSONB)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def create_result(self, results, user_id):
        self.results = results
        self.user_id = user_id
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_result_by_uuid(uuid, user_id):
        return Result.query.filter_by(uuid=uuid, user_id=user_id).first()


class Guessable(db.Model):
    from sqlalchemy.dialects.postgresql import UUID, JSONB
    from uuid import uuid4

    __tablename__ = 'guessables'

    uuid = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = db.Column(db.String)
    variations = db.Column(JSONB)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return f'<guessable uuid: {self.uuid}>'

    def create_guessable(self, name, variations, user_id):
        self.name = name
        self.variations = variations
        self.user_id = user_id
        db.session.add(self)
        db.session.commit()

    def update_guessable(self, name, variations):
        self.name = name
        self.variations = variations
        db.session.commit()

    def delete_guessable(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def get_guessable_by_uuid(uuid, user_id):
        return Guessable.query.filter_by(uuid=uuid, user_id=user_id).first()

    @staticmethod
    def get_all_users_variations(twitch_id):
        return Guessable.query.with_entities(Guessable.variations).join(User).filter_by(twitch_id=twitch_id).all()
