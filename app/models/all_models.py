from app import db

class Train(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    train_number = db.Column(db.String(50), unique=True, nullable=False)
    departure_time = db.Column(db.DateTime, nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    available_seats = db.Column(db.Integer, nullable=False, default=capacity)
    waiting_list = db.Column(db.Integer, nullable=False, default=0)
    tatkal_seats = db.Column(db.Integer, nullable=False, default=capacity//10)  # New field for Tatkal reserved seats
    tickets = db.relationship('Ticket', backref='train', lazy=True)


    def __repr__(self):
        return f"Train(train_number={self.train_number}, departure_time={self.departure_time}, capacity={self.capacity})"

class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    train_id = db.Column(db.Integer, db.ForeignKey('train.id'), nullable=False)
    passenger_name = db.Column(db.String(100), nullable=False)
    passenger_email = db.Column(db.String(100), nullable=False)
    seat_number = db.Column(db.Integer, nullable=True, unique=True)

    def __repr__(self):
        return f"Ticket(passenger_name={self.passenger_name}, passenger_email={self.passenger_email}, seat_number={self.seat_number})"
