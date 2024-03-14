from flask import Blueprint, request, jsonify, current_app, session, redirect, url_for
from app.models.admin import Admin 
from app.models.all_models import Train, Ticket
from app import db 
from datetime import datetime, timedelta
import pytz
from app import mail
from flask_mailman import EmailMessage
from app.celery.tasks import send_reminder_email

main_api = Blueprint('main_api', __name__)

IST = pytz.timezone('Asia/Kolkata')

# Utility functions
# def assign_seat_number(train):
#     if train.available_seats > 0:
#         for i in range(1, train.capacity + 1):
#             if i not in train.assigned_seat_numbers:
#                 train.assigned_seat_numbers.add(i)  # Add the seat number to the set of assigned seat numbers
#                 train.available_seats -= 1
#                 return i
#     else:
#         return None


# def assign_waiting_list_seats(train):
#     # Find the first passenger on the waiting list
#     first_waiting_ticket = Ticket.query.filter_by(train_id=train.id, seat_number=None).order_by(Ticket.id).first()
#     while first_waiting_ticket and train.available_seats > 0:
#         for i in range(1, train.capacity + 1):
#             if i not in train.assigned_seat_numbers:
#                 train.assigned_seat_numbers.add(i)  # Add the seat number to the set of assigned seat numbers
#                 first_waiting_ticket.seat_number = i
#                 train.available_seats -= 1
#                 train.waiting_list -= 1
#                 first_waiting_ticket = Ticket.query.filter_by(train_id=train.id, seat_number=None).order_by(Ticket.id).first()
#                 break

#     db.session.commit()


@main_api.route('/add-train', methods=['POST'])
def add_train():
    # Check if the user is an admin
    if not session.get('admin_logged_in'):
        return jsonify({'message': 'Admin login required'}), 401

    data = request.get_json()

    train_number = data.get('train_number')
    departure_time = data.get('departure_time')  
    capacity = data.get('capacity') # 100
    tatkal_seats = capacity // 10 # capacity // 10 = 10
    available_seats = capacity - tatkal_seats # 90 

    departure_time_ist = datetime.strptime(departure_time, '%Y-%m-%dT%H:%M:%S').replace(tzinfo=IST)

    if not all([train_number, departure_time, capacity]):  # Ensure all fields are provided
        return jsonify({'message': 'Train number, departure time, and capacity are required'}), 400

    # Check if a train with the given train number already exists
    existing_train = Train.query.filter_by(train_number=train_number).first()
    if existing_train:
        return jsonify({'message': 'Train with this number already exists'}), 409

    # Create Train object
    train = Train(train_number=train_number, departure_time=departure_time_ist, capacity=capacity, available_seats=available_seats, tatkal_seats=tatkal_seats)
    db.session.add(train)
    db.session.commit()

    return jsonify({'message': 'Train added successfully'}), 201


@main_api.route('/trains', methods=['GET'])
def get_trains():
    trains = Train.query.all()

    train_data = []
    for train in trains:
        train_info = {
            'train_number': train.train_number,
            'departure_time': train.departure_time.strftime('%Y-%m-%d %H:%M:%S'),  # Format departure time
            'available_seats': train.available_seats,
            'waiting_list': train.waiting_list
        }
        train_data.append(train_info)

    return jsonify(train_data)


@main_api.route('/book-ticket', methods=['POST'])
def book_ticket():
    data = request.get_json()

    train_number = data.get('train_number')
    passenger_name = data.get('name')
    passenger_email = data.get('email')

    if not all([train_number, passenger_name, passenger_email]):
        return jsonify({'message': 'Train number, name, and email are required'}), 400

    train = Train.query.filter_by(train_number=train_number).first()
    if not train:
        return jsonify({'message': 'Train not found'}), 404

    # Check if the user has already booked a ticket for this train
    existing_ticket = Ticket.query.filter_by(train_id=train.id, passenger_email=passenger_email).first()
    if existing_ticket:
        return jsonify({'message': 'You have already booked a ticket for this train'}), 400

    # Assign seat number
    if train.available_seats > 0:
        seat_number = train.capacity - train.available_seats + 1 
        train.available_seats -= 1

        msg = EmailMessage(
        "Your ticket details",
        f"Hi {passenger_name}, your ticket has been booked successfully! Your seat number is {seat_number}.",
        "ticket_booking@fastmail.com", 
        [passenger_email]
    )
    else:
        seat_number = None 

        msg = EmailMessage(
            "Your ticket details",
            f"Hi {passenger_name}, your ticket has been booked successfully! You are added in the waiting list.",
            "ticket_booking@fastmail.com", 
            [passenger_email]
        )
        msg.send()

    # Create and save the ticket
    ticket = Ticket(train_id=train.id, passenger_name=passenger_name, passenger_email=passenger_email, seat_number=seat_number)
    db.session.add(ticket)
    db.session.commit()

    # Scheduling email reminder task
    current_time = datetime.now()
    departure_time = train.departure_time
    reminder_delta = departure_time - current_time - timedelta(minutes=30)
    reminder_delay = max(reminder_delta.total_seconds(), 0)
    print('reminder delay ', reminder_delay, 'current time', current_time, 'departure time', departure_time)
    send_reminder_email.apply_async(args=[passenger_name, passenger_email, seat_number, departure_time], countdown=reminder_delay)

    return jsonify({'message': 'Ticket booked successfully'}), 201


@main_api.route('/cancel-ticket', methods=['POST'])
def cancel_ticket():
    data = request.get_json()

    train_number = data.get('train_number')
    passenger_name = data.get('name')
    passenger_email = data.get('email')

    if not all([train_number, passenger_name, passenger_email]):
        return jsonify({'message': 'Train number, name, and email are required'}), 400

    # Check if the train exists
    train = Train.query.filter_by(train_number=train_number).first()
    if not train:
        return jsonify({'message': 'Train not found'}), 404

    ticket = Ticket.query.filter_by(train_id=train.id, passenger_name=passenger_name, passenger_email=passenger_email).first()
    if not ticket:
        return jsonify({'message': 'Ticket not found for this passenger on the specified train'}), 404

    # Cancel the ticket
    if ticket.seat_number is not None:  
        train.available_seats += 1 
    else:  
        train.waiting_list -= 1 

    db.session.delete(ticket)
    db.session.commit()

    if train.waiting_list > 0:
        first_waiting_ticket = Ticket.query.filter_by(train_id=train.id, seat_number=None).order_by(Ticket.id).first()
        if first_waiting_ticket:
            first_waiting_ticket.seat_number = train.capacity - train.available_seats + 1
            train.available_seats -= 1
            train.waiting_list -= 1

            db.session.commit()

    return jsonify({'message': 'Ticket canceled successfully'}), 200


@main_api.route('/book-tatkal-ticket', methods=['POST'])
def book_tatkal_ticket():
    data = request.get_json()

    # Extract request data
    train_number = data.get('train_number')
    passenger_name = data.get('name')
    passenger_email = data.get('email')

    if not all([train_number, passenger_name, passenger_email]):
        return jsonify({'message': 'Train number, passenger name, and email are required'}), 400

    train = Train.query.filter_by(train_number=train_number).first()
    if not train:
        return jsonify({'message': 'Train not found'}), 404

    # Check if the Tatkal booking window is open
    if is_tatkal_booking_window_open(train.departure_time):
        if train.tatkal_seats > 0:
            seat_number = train.capacity//10 - train.tatkal_tickets + 1
            ticket = Ticket(train_id=train.id, passenger_name=passenger_name, passenger_email=passenger_email, seat_number=seat_number)
            train.tatkal_seats -= 1
            db.session.add(ticket)
            db.session.commit()

            return jsonify({'message': 'Tatkal ticket booked successfully'}), 200
        else:
            # All Tatkal seats are filled, add user to waiting list
            ticket = Ticket(train_id=train.id, passenger_name=passenger_name, passenger_email=passenger_email)
            db.session.add(ticket)
            db.session.commit()

            return jsonify({'message': 'All Tatkal seats are filled. You have been added to the waiting list.'}), 200
    else:
        return jsonify({'message': 'Tatkal booking window is closed right now.'}), 400


def is_tatkal_booking_window_open(departure_time):
    tatkal_booking_start_time = departure_time - timedelta(hours=2)
    # Determine the Tatkal booking window end time (10 minutes after the start time)
    tatkal_booking_end_time = tatkal_booking_start_time + timedelta(minutes=10)
    current_time = datetime.now()

    return tatkal_booking_start_time <= current_time <= tatkal_booking_end_time
