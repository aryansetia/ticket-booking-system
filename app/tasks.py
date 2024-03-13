from celery import shared_task
from flask_mailman import EmailMessage

@shared_task(ignore_result=True)
def send_reminder_email(passenger_name, passenger_email, seat_number, departure_time):
    # Construct the email message
    msg = EmailMessage(
        "Reminder: Your train is departing soon!",
        f"Hi {passenger_name}, this is a reminder that your train is departing in 30 minutes. Your seat number is {seat_number}.",
        "ticket_booking@fastmail.com",
        [passenger_email]
    )

    # Send the email
    msg.send()