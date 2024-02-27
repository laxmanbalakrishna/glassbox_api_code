from hashlib import sha256
import boto3
from botocore.exceptions import NoCredentialsError
from django.core.mail import send_mail
from glassbox_api.aws_sm import get_secrets
secrets = get_secrets()

def get_masked_pan(pan_number):

    return pan_number[:2] + '*' * (len(pan_number) - 4) + pan_number[-2:]

def hash_pan(pan_number):
    sha256_hash = sha256()
    sha256_hash.update(pan_number.encode('utf-8'))

    return sha256_hash.hexdigest()

def get_serilizer_errors(serializer):
    error_str = ""
    for key, value in serializer.errors.items():
        error_str += key + " : " + value[0] + ","
    return error_str[:-1]

def send_verification_message(identifier, otp):
    # Check if the identifier is an email or a phone number
    is_email = '@' in identifier

    if is_email:
        # Send email using Amazon SES
        send_email(identifier, otp)
    else:
        # Send SMS using Amazon SNS
        send_sms(identifier, otp)



def send_email(email, otp):
    # Set up the SES client
    ses_client = boto3.client('ses')

    # Specify the subject and body of the email
    subject = 'Verification Code'
    body = f'Your verification code is: {otp}'

    # Specify the sender email address
    sender_email = 'support@bbsi.in'

    # Specify the recipient email address
    recipient_email = email

    try:
        # Send the email using Amazon SES
        response = ses_client.send_email(
            Source=sender_email,
            Destination={'ToAddresses': [recipient_email]},
            Message={
                'Subject': {'Data': subject},
                'Body': {'Text': {'Data': body}}
            }
        )

        print(f"Email sent successfully. Message ID: {response['MessageId']}")
    except NoCredentialsError:
        print("AWS credentials not available or incorrect.")
    except Exception as e:
        print(f"Error sending email: {e}")

def send_sms(phone_number, otp):
    # Set up the SNS client
    sns_client = boto3.client('sns')

    # Check if the phone number includes the country code
    if not phone_number.startswith('+91'):
        # If not, add the country code
        phone_number = '+91' + phone_number

    # Specify the message for the SMS
    message = f'Your verification code is: {otp}'

    try:
        # Send the SMS
        sns_client.publish(PhoneNumber=phone_number, Message=message)

        print(f"SMS sent successfully.")
    except NoCredentialsError:
        print("AWS credentials not available or incorrect.")
    except Exception as e:
        print(f"Error sending SMS: {e}")