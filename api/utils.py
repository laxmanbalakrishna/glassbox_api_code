import os

from django.core.mail import EmailMultiAlternatives
from django.template import loader

from glassbox_api import settings, constants
from api.models import GSTinDetails
import re
import requests
import  json
from datetime import datetime

def send_mail_to_user(data, temp_pwd):
    try:
        user_email = data['email']
        user_password = temp_pwd
        user_name = data['first_name'] + ' ' + data.get('last_name','')

        settings_dir = os.path.dirname(__file__)
        PROJECT_ROOT = os.path.abspath(os.path.dirname(settings_dir))
        HTML_FILE = os.path.join(PROJECT_ROOT, 'static/email_templates/user_registration_email.html')
        html_message = loader.render_to_string(
            HTML_FILE,
            {
                'email': user_email,
                'password': user_password,
                'username': user_name,
            }
        )
        subject, from_email = 'Glassbox - Credentials', settings.DEFAULT_FROM_EMAIL,
        msg = EmailMultiAlternatives(subject, constants.THIS_IS_AN_IMPORTANT_MESSAGE, from_email,
                                     [user_email])
        msg.attach_alternative(html_message, constants.CONTENT_TYPE_HTML)
        print(msg)

        msg.send()
        return True, "Success"
    except Exception as e:
        return False, str(e)



def fetch_and_save_gstin_details(search_key):
    try:
        # Check if GSTinDetails already exist in the database

        # GSTin details do not exist, fetch from the GST API
        api_url = f"https://commonapi.mastersindia.co/commonapis/searchgstin?gstin={search_key}"
        headers = {
            'Content-type': "application/json",
            "client_id": settings.MASTER_INDIA_CLIENT_ID,
            "mode": "no-cors",
            "Authorization": f'Bearer {settings.MASTER_INDIA_CLIENT_TOKEN}'
        }

        response = requests.get(api_url, headers=headers)

        if response.status_code == 200:
            response_data = response.json()

            if not response_data.get('error', False):
                # Check the status of GST
                if response_data['data']['sts'] == 'Active':
                    # Convert the date to the correct format
                    incorporation_date = datetime.strptime(response_data['data']['rgdt'], "%d/%m/%Y").date()

                    extracted_data = {
                        "incorporation_date": incorporation_date,
                        "company": response_data['data']['ctb'],
                        "gstin": response_data['data']['gstin'],
                        "state": response_data['data']['pradr']['addr']['stcd'],
                        "pincode": response_data['data']['pradr']['addr']['pncd'],
                        "city": response_data['data']['pradr']['addr']['loc'],
                        "district": response_data['data']['pradr']['addr']['dst'],
                        "business_name": response_data['data']['tradeNam'],
                        "fullname": response_data['data']['lgnm'],
                        "industry": response_data['data']['nba']
                    }

                    return True, extracted_data
                else:
                    return False, 'Your GST is not active. Please register with the PAN number.'
            else:
                return False, 'Error in API response: ' + response_data['message']
        else:
            return False, 'Failed to fetch GST details. HTTP Status Code: ' + str(response.status_code)

    except Exception as e:
        return False, 'An error occurred: ' + str(e)
        # Handle the case where GSTIN details are not found in the API response

def is_valid_phone_number(phone_number):
    pattern = re.compile(r'^\d{10}$')
    return bool(pattern.match(phone_number))
