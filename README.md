# Ticket Booking System 
This project contains the API of a Ticket Booking System built using Flask. It has features like: 
1. Admin can add the trains with departure time and capacity (number of seats).
2. User can check all the available trains and can book the ticket by providing the train number.
3. There is a tatkal window, that gets opened 2hrs before the departure time of the train and remains opened for 10 minutes. 
4. Users also get a reminder email 30 minutes before the departure time of the train. 


## Installation 
Install all the dependencies in a virtual environment.
```
pip3 install -r requirements.txt
```

## How to use 
Once done with the installation of dependencies, run the application and celery by following commands. 
```
python3 run.py
celery -A run.celery_app worker --loglevel=info
```

## Note
Provide the details of your email sender like port, server, username and password in .env file.