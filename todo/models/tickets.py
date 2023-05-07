from . import db


class Ticket(db.Model):
    __tablename__ = 'tickets'

    ticket_id = db.Column(db.String(36), primary_key=True)
    concert_id = db.Column(db.String(36), db.ForeignKey('concerts.id'), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    print_status = db.Column(db.String(20), nullable=False)

    # concert = db.relationship('Concert', backref='tickets')
    # user = db.relationship('User', backref='tickets')
    def to_dict(self):
        return {
            'id': self.ticket_id,
            'concert': {
                'id': self.concert_id,
                'url': f'http://tickets.api.ticketoverflow.com/api/v1/concerts/{self.concert_id}'
            },
            'user': {
                'id': self.user_id,
                'url': f'http://tickets.api.ticketoverflow.com/api/v1/users/{self.user_id}'
            },
            'print_status': self.print_status
        }

    def __repr__(self):
        return f'<Ticket {self.ticket_id} {self.concert_id} {self.user_id}>'
