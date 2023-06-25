import boto3
import json
import urllib.parse

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table("dna-hpc-user-table")

s3 = boto3.client('s3')
bucket_name = "dna-hpc-frontend-html"
success_object = "success.html"
failure_object = "error.html"

health = "/health"
user = "/user"

def lambda_handler(event, context):
    http_method = event['httpMethod']
    event_path = event['path']

    if http_method == 'GET' and event_path == health:
        body = "<!DOCTYPE html><html><head><title>Health Check Page</title></head><body><h1>Health OK</h1></body></html>"
        response = build_response(200, body)
    
    elif http_method == 'GET' and event_path == user:
        pass
    
    elif http_method == 'POST' and event_path == user:
        #response = create_user(json.loads(event['body']))
        params = convert_str_to_dict(event['body'])
        response = create_user(params)
    
    elif http_method == 'PATCH' and event_path == user:
        response = update_user(json.loads(event['body']))

    elif http_method == 'DELETE' and event_path == user:
        response = delete_user(json.loads(event['body']))

    else:
        response = build_response(404)
    
    return response

def convert_str_to_dict(message):
    param_dict = {}
    for param in message.split('&'):
        key, value = param.split('=')
        param_dict[key] = value
    param_dict['email'] = urllib.parse.unquote(param_dict.get('email'))
    return param_dict
    
def build_response(status_code, body=None):
    return {
        "statusCode" : status_code,
        "headers" : {
            "Content-Type" : "text/html"
        },
        "body" : str(body)
    }

def create_user(request_body):
    print("Create User")
    table_response = table.put_item(Item = request_body)
    return_code = table_response['ResponseMetadata']['HTTPStatusCode']
    message_body = None
    if return_code == 200:
        response = s3.get_object(Bucket=bucket_name, Key=success_object)
        message_body = response['Body'].read().decode('utf-8')
        print("message_body")
        print(message_body)
    else:
        response = s3.get_object(Bucket=bucket_name, Key=failure_object)
        message_body = response['Body'].read().decode('utf-8')

    response = build_response(return_code, message_body)
    return response
    
def update_user(request_body):
    print("Update User")
    table_response = table.put_item(Item = request_body)
    return_code = table_response['ResponseMetadata']['HTTPStatusCode']
    message_body = {
        "Operation" : "Update User",
        "Message" : "Success",
        "Item" : request_body
            }
    response = build_response(return_code, message_body)
    return response

def delete_user(key):
    print("Delete User")
    table_response = table.get_item(Key = key)
    item = table_response['Item']
    table_response = table.delete_item(Key = key)
    print("Table Response")
    print(table_response)
    return_code = table_response['ResponseMetadata']['HTTPStatusCode']
    message_body = {
        "Operation" : "Delete User",
        "Message" : "Success",
        "Item" : item
            }
    response = build_response(return_code, message_body)
    return response

def get_user(key):
    print("Get User")
    table_response = table.get_item(Key = key)
    return_code = table_response['ResponseMetadata']['HTTPStatusCode']
    item = table_response['Item']
    message_body = {
        "Operation" : "Get User",
        "Message" : "Success",
        "Item" : item
            }
    response = build_response(return_code, message_body)
    return response