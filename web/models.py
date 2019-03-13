from web import db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    twitch_id = db.Column(db.Integer)
    twitch_login_name = db.Column(db.String())
    twitch_display_name = db.Column(db.String())

    def __init__(self, twitch_id, twitch_login_name, twitch_display_name):
        self.twitch_id = twitch_id
        self.twitch_login_name = twitch_login_name
        self.twitch_display_name = twitch_display_name

    def __repr__(self):
        return f'<id: {self.id} login: {self.twitch_login_name}>'

    @staticmethod
    def get_user_by_twitch_id(twitch_id):
        return User.query.filter_by(twitch_id=twitch_id).first()
