from web import db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    twitch_id = db.Column(db.Integer)
    twitch_login_name = db.Column(db.String())
    twitch_display_name = db.Column(db.String())
    bot_enabled = db.Column(db.Boolean())

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
