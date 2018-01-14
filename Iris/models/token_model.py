from Iris import db


class RevokedTokens(db.Model):
    """This class stores the revoked tokens 
    """
    __tablename__ = 'revoked_tokens'
    id = db.Column(db.Integer, primary_key=True)
    revoked_token = db.Column(db.Text)

    def save(self):  # pragma: no cover
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return "<Revoked token: {}".format(self.revoked_tokens)
