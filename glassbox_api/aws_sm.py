
import json
import boto3
from botocore.exceptions import ClientError
def get_secrets():
    # Retrieve the secret value from AWS Secrets Manager
    secret_name = "dev/bdnt/opt"

    # Create a Boto3 session without specifying the profile or region
    session = boto3.session.Session()

    # Create a Secrets Manager client using the default session
    client = session.client(service_name='secretsmanager')

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        print(f"Unable to retrieve secret: {e}")
        raise

    # Parse and extract the database configuration values
    secret= get_secret_value_response['SecretString']
    return json.loads(secret)

secrets = get_secrets()

