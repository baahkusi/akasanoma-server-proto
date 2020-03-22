import os
import random
from hashlib import sha1
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from .config import SENDGRID_API_KEY


def handle_requests(actions, req, payload):

    """
    This method takes a reqest format :payload: and returns
    a response format.
    ===============
    Request Format
    ===============
    {
        "request_id" : { 
        "action_name" : {"parameter":value, ...]},
        "000" : ["action_name" ...,]
        ...
        },
        ...,
        "000" : ["request_id" ...,],
        ...
    }


    ================
    Response Format
    ================
    {
        "request_id" : { 
        "action_name" : response = {'status': True | False, 'data': ...},
        ...
        },
        ...,
    }
    """
    
    response = {}
    for request_id in payload["000"]:
        request = payload[request_id]
        response[request_id] = {}
        for action in request["000"]:
            if action in actions.keys():
                response[request_id][action] = actions[action](req, **request[action])
            else:
                response[request_id][action] = {'status':False, 'data':'Invalid Action'}
    return response


def send_email(to_email, message):

    message = Mail(
        from_email='akasanoma@example.com',
        to_emails=to_email,
        subject='Login Pin',
        html_content=message)

    sg = SendGridAPIClient(SENDGRID_API_KEY)
    response = sg.send(message)
    return response


def pay_user(amount, payment_data):
    """
    Makes the required money transfer to the user
    """
    return True


def fresh_pin():
    """
    Generate a random 5 digit pin
    """
    return ''.join([str(random.randint(0,9)) for n in range(5)])


def token(email, pin):
    """
    Generate a SHA1 Encoded String as token
    """
    return sha1(f"{pin},{email}".encode()).hexdigest()


def get_data(resource, data_def):
    """
    Return data as defined in data_def
    from resource
    """
    data = {}
    for ddef in data_def.keys():
        if hasattr(resource, ddef):
            data[ddef] = data_def[ddef]
        else:
            data[ddef] = None
    return data


def points_to_amount(points):
    """
    Converts the user's points to amount to be paid by user in Ghana Cedis
    """

    rate = 0.1/100
    return rate * points
