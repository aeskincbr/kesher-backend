from http import HTTPStatus
import os
from typing import Dict, Tuple
import requests


from aws_lambda_context import LambdaContext
from aws_lambda_powertools.logging import logger
from aws_lambda_powertools import Logger
import boto3
from botocore.exceptions import ClientError
from pydantic import ValidationError

from kesher_service_cdk.service_stack.email_services.email_services import EMAIL_BUCKET_ENV_VAR


logger = Logger()

@logger.inject_lambda_context(log_event=True)
def admin_submit(event: dict, context: LambdaContext) -> dict:
    try:
        pass
        # kesher_dto: KesherDto = KesherDto.parse_raw(event["body"])
        # now: Decimal = Decimal(datetime.now().timestamp())
        # kesher: Kesher = Kesher(name=kesher_dto.name, created_date=now, updated_date=now)
        # return _build_response(http_status=HTTPStatus.CREATED, body=kesher.json())
    except (ValidationError, TypeError) as err:
        return _build_error_response(err, HTTPStatus.BAD_REQUEST)
    except Exception as err:
        return _build_error_response(err)


@logger.inject_lambda_context(log_event=True)
def teacher_submit(event: dict, context: LambdaContext) -> dict:
    try:
        bucket_name = get_env_var(EMAIL_BUCKET_ENV_VAR)
        sender, presigned_url, attachment_bytes = read_email_content(event)
        
        local_file_name = f'{sender}.kindergarten_ids.csv'
        with open(local_file_name, "wb") as file:
            file.write(attachment_bytes)

        upload_s3_object_presigned(source_file=local_file_name, object_name=local_file_name, bucket_name=bucket_name)
        # by upload using the presigned url, we are in practive validating the expiration and the 
        # tenant identity (we emailed this teached with the link to this specific object in our bucket)
        # If this succeeds using a signed URL, this means that we provided a signed url for this bucket and this file name with the email 
        # Address prefix. this is the user authorization for this (temporary) flow

        # TODO - handle errors - expiration, invalid link etc. 

        # TODO - input validation on data - on error email back with the message id (this can be used for troubleshooting)

        # TODO - read records from file, push to DB
        # make sure that data is inserted into the DB in a secure way to avoid SQL injection

        # Respond to sender with result (do we respond to sender on any error? don't divulge informative errors to rogue senders)


    except (ValidationError, TypeError) as err:
        return _build_error_response(err, HTTPStatus.BAD_REQUEST)
    except Exception as err:
        return _build_error_response(err)


def read_email_content(event: dict) -> Tuple[str, Dict, bytes]:
    # TODO - implement this
    # TODO - read email conteמt
    #   - extract presigned URL, maybe retry once with a short wait - merge code from Alex
    #   - extract attachment bytes

    # Hard code presigned url until url read is implemented 
    # You can generate a presigned URL for upload by calling create_presigned_post below

    # For example:

    #response = create_presigned_post(bucket_name="keshercsvupload-serviceemailkeshercsvuploademails-jbl8wdljx0tt", 
    #                                 object_name="/TeacherSubmissions/email@gmail.com-submission.csv")

    sender = "email@gmail.com" # TODO: Extract sender from event

    # TODO: Buid this from the email context
    presgined_url_dict = {
        'url': 'https://keshercsvupload-serviceemailkeshercsvuploademails-jbl8wdljx0tt.s3.amazonaws.com/',
        'fields': {
            'AWSAccessKeyId': 'ASIAR37OWCTPEKLJW67W', 
            'key': '/TeacherSubmissions/email@gmail.com-submission.csv', 
            'policy': 'eyJleHBpcmF0aW9uIjogIjIwMjEtMDQtMDZUMTI6NTM6MDNaIiwgImNvbmRpdGlvbnMiOiBbeyJidWNrZXQiOiAia2VzaGVyY3N2dXBsb2FkLXNlcnZpY2VlbWFpbGtlc2hlcmNzdnVwbG9hZGVtYWlscy1qYmw4d2RsangwdHQifSwgeyJrZXkiOiAiL1RlYWNoZXJTdWJtaXNzaW9ucy9lbWFpbEBnbWFpbC5jb20tc3VibWlzc2lvbi5jc3YifSwgeyJ4LWFtei1zZWN1cml0eS10b2tlbiI6ICJGd29HWlhJdllYZHpFTlQvLy8vLy8vLy8vd0VhRFBNaVJLdFRUNzVqQVMxWDBDTG5BVHczb00wRStRaFVoaWFOZHRHZDFjRHJIV3FRUWFUZ0puYk1yY1dvVUlwS3gwZTlFL0p3MkJReVVIUE5sVHQ4RVVVa2c5UldzbXFJNVVwZGNSdVVST2FWbkZ2SXhiTm5ZUkpMLzh3dEViM3NsajFSb1hRdnlXbjNta0o2eU95SWNZWmp6WEhqeStvcHRUWkRwK3lwS3VEL2Npcmtya0RacWYrTmhpR20vQm5rd0FpRGo4VkVkdnFmN3RmeW9TbnRlU1orTkVDTlE5QVZadUsyNzg0dEZ4R1Z5bkxZdDVENmFMWlhSRzZKQnZlNEV5Y1NrVTB6bkR0TkR4KzdOaFVSQUZFMXFNdTRyS1BCYmpqQ2R5TFdDSkoxK0lOcml6UDRLU2wxckhZdFlNNGNrSXk3UjJYRzBTaTBxSzJEQmpJck1GS3NYYzdsbDNhMjR4NnRLQzlTb09RL1c1eXJ4clFoU05jczAwdWhmaFZBODk1STZHSTh3cjR5ZHc9PSJ9XX0=', 
            'signature': 'zyu7yeGEH3ZvGPs+7JPgs2W3Kss=', 
            'x-amz-security-token': 'FwoGZXIvYXdzENT//////////wEaDPMiRKtTT75jAS1X0CLnATw3oM0E+QhUhiaNdtGd1cDrHWqQQaTgJnbMrcWoUIpKx0e9E/Jw2BQyUHPNlTt8EUUkg9RWsmqI5UpdcRuUROaVnFvIxbNnYRJL/8wtEb3slj1RoXQvyWn3mkJ6yOyIcYZjzXHjy+optTZDp+ypKuD/cirkrkDZqf+NhiGm/BnkwAiDj8VEdvqf7tfyoSnteSZ+NECNQ9AVZuK2784tFxGVynLYt5D6aLZXRG6JBve4EycSkU0znDtNDx+7NhURAFE1qMu4rKPBbjjCdyLWCJJ1+INrizP4KSl1rHYtYM4ckIy7R2XG0Si0qK2DBjIrMFKsXc7ll3a24x6tKC9SoOQ/W5yrxrQhSNcs00uhfhVA895I6GI8wr4ydw=='
        }
    }

    attachment_bytes = b'\xef\xbb\xbf\xd7\x9e\xd7\x96\xd7\x94\xd7\x94 \xd7\x92\xd7\x9f,\xd7\x9e\xd7\xa1\xd7\xa4\xd7\xa8 \xd7\x96\xd7\x94\xd7\x95\xd7\xaa \xd7\x99\xd7\x9c\xd7\x93/\xd7\x94,\xd7\xa9\xd7\x9d \xd7\xa4\xd7\xa8\xd7\x98\xd7\x99 \xd7\x99\xd7\x9c\xd7\x93/\xd7\x94,\xd7\xa9\xd7\x9d \xd7\x9e\xd7\xa9\xd7\xa4\xd7\x97\xd7\x94 \xd7\x99\xd7\x9c\xd7\x93/\xd7\x94,\xd7\xaa\xd7\x90\xd7\xa8\xd7\x99\xd7\x9a \xd7\x9c\xd7\x99\xd7\x93\xd7\x94 \xd7\x99\xd7\x9c\xd7\x93/\xd7\x94,\xd7\x94\xd7\x95\xd7\xa8\xd7\x94 1 \xd7\x9e\xd7\xa1\xd7\xa4\xd7\xa8 \xd7\x96\xd7\x94\xd7\x95\xd7\xaa,\xd7\x94\xd7\x95\xd7\xa8\xd7\x94 1 \xd7\xa9\xd7\x9d \xd7\xa4\xd7\xa8\xd7\x98\xd7\x99,\xd7\x94\xd7\x95\xd7\xa8\xd7\x94 1 \xd7\xa9\xd7\x9d \xd7\x9e\xd7\xa9\xd7\xa4\xd7\x97\xd7\x94,\xd7\x94\xd7\x95\xd7\xa8\xd7\x94 1 \xd7\x90\xd7\x99\xd7\x9e\xd7\x99\xd7\x99\xd7\x9c,\xd7\x94\xd7\x95\xd7\xa8\xd7\x94 2 \xd7\x9e\xd7\xa1\xd7\xa4\xd7\xa8 \xd7\x96\xd7\x94\xd7\x95\xd7\xaa,\xd7\x94\xd7\x95\xd7\xa8\xd7\x94 2 \xd7\xa9\xd7\x9d \xd7\xa4\xd7\xa8\xd7\x98\xd7\x99,\xd7\x94\xd7\x95\xd7\xa8\xd7\x94 2 \xd7\xa9\xd7\x9d \xd7\x9e\xd7\xa9\xd7\xa4\xd7\x97\xd7\x94,\xd7\x94\xd7\x95\xd7\xa8\xd7\x94 2 \xd7\x90\xd7\x99\xd7\x9e\xd7\x99\xd7\x99\xd7\x9c,\xd7\x94\xd7\x90\xd7\x9d \xd7\x9c\xd7\x9e\xd7\x97\xd7\x95\xd7\xa7? (\xd7\x9c\xd7\x9e\xd7\x97\xd7\x99\xd7\xa7\xd7\xaa \xd7\xa8\xd7\xa9\xd7\x95\xd7\x9e\xd7\x94 \xd7\x96\xd7\x95 \xd7\xa1\xd7\x9e\xd7\x9f V)\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,\r\n,,,,,,,,,,,,,'
    return sender, presgined_url_dict, attachment_bytes
    

def _build_response(http_status: HTTPStatus, body: str) -> dict:
    return {'statusCode': http_status, 'headers': {'Content-Type': 'application/json'}, 'body': body}


def _build_error_response(err, status: HTTPStatus = HTTPStatus.INTERNAL_SERVER_ERROR) -> dict:
    logger.error(str(err))
    return {
        'statusCode': status,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': str(err),
    }

def get_env_var(name: str) -> str:
    env_var = os.getenv(name)
    if env_var is None:
        error_message = f'{name} Enviroment Variable is missing for this lambda'
        logger.error(error_message)
        raise Exception(error_message)
    return env_var


def create_presigned_post(bucket_name, object_name, fields=None, conditions=None, expiration=3600):
    """Generate a presigned URL S3 POST request to upload a file

    :param bucket_name: string
    :param object_name: string
    :param fields: Dictionary of prefilled form fields
    :param conditions: List of conditions to include in the policy
    :param expiration: Time in seconds for the presigned URL to remain valid
    :return: Dictionary with the following keys:
        url: URL to post to
        fields: Dictionary of form fields and values to submit with the POST
    :return: None if error.
    """

    # Generate a presigned S3 POST URL
    s3_client = boto3.client('s3')
    try:
        response = s3_client.generate_presigned_post(bucket_name,
                                                     object_name,
                                                     Fields=fields,
                                                     Conditions=conditions,
                                                     ExpiresIn=expiration)
    except ClientError as e:
        logger.error(e)
        return None

    # The response contains the presigned URL and required fields
    return response


def upload_s3_object_presigned(source_file: str, object_name: str, bucket_name: str) -> str:
    response = create_presigned_post(bucket_name, object_name)
    if response is None:
        raise Exception("Error generating presigned url for {object_name=}, {bucket_name=}")

    with open(source_file, 'rb') as f:
        files = {'file': (object_name, f)}
        http_response = requests.post(response['url'], data=response['fields'], files=files)
    
    # If successful, returns HTTP status code 204
    logger.info(f'File upload HTTP status code: {http_response.status_code}')
    if http_response.status_code > 300:
        logger.error(f"Error uploading object with presigned url {http_response.content=}")
        raise Exception(f"Error uploading {object_name=} to {bucket_name=}")

upload_s3_object_presigned("moshe.txt", "the_object", "keshercsvupload-serviceemailkeshercsvuploademails-jbl8wdljx0tt")
