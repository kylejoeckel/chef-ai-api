import os
import openai
import json
from flask import Flask
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('usersTable')
app = Flask(__name__)
openai.api_key = os.environ['OPEN_API']


@app.route("/update-recipe", methods=['PUT'])
def update_recipe(event, context):
    user = json.loads(event['body'])
    try:
        updated = table.update_item(
            Key={
                'email': user['email']
            },
            UpdateExpression="set recipe_book = :r",
            ExpressionAttributeValues={
                ':r': user['recipe_book'],
            },
            ReturnValues="UPDATED_NEW"
        )
        print(updated)
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json",
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Credentials': True},
            "body": json.dumps(updated['Attributes'])
        }
    except Exception as err:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json",
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Credentials': True},
            "body": json.dumps(err)
        }


@app.route("/sign-up", methods=["POST"])
def sign_up(event, context):
    print(event)
    user = json.loads(event['body'])
    print(user)
    try:
        existingUser = response = table.get_item(
            Key={
                'email': user['email'].lower(),
            }
        )
        if 'Item' in existingUser:
            existingUser['Item']['password'] = None
            existingUser['Item']['credits'] = int(
                existingUser['Item']['credits'])
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json",
                            'Access-Control-Allow-Origin': '*',
                            'Access-Control-Allow-Credentials': True},
                "body": json.dumps(existingUser['Item'])
            }
        else:
            user["credits"] = 10
            table.put_item(Item=user)
            newUser = response = table.get_item(
                Key={
                    'email': user['email'].lower(),
                }
            )
            if 'Item' in newUser:
                newUser['Item']['password'] = None
                newUser['Item']['credits'] = int(newUser['Item']['credits'])
                return {
                    "statusCode": 200,
                    "headers": {"Content-Type": "application/json",
                                                'Access-Control-Allow-Origin': '*',
                                                'Access-Control-Allow-Credentials': True},
                    "body": json.dumps(newUser['Item'])
                }
            else:
                return {
                    "statusCode": 400,
                    "headers": {"Content-Type": "application/json",
                                'Access-Control-Allow-Origin': '*',
                                'Access-Control-Allow-Credentials': True},
                }
    except Exception as err:
        print(err)
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json",
                                        'Access-Control-Allow-Origin': '*',
                                        'Access-Control-Allow-Credentials': True},
            "body": json.dumps(err)
        }


@app.route("/log-in", methods=["POST"])
def log_in(event, context):
    print(event)
    try:
        user = json.loads(event['body'])
        currentUser = response = table.get_item(
            Key={
                'email': user['email'].lower(),
            }
        )
        if 'Item' in currentUser:
            currentUser['Item']['credits'] = int(
                currentUser['Item']['credits'])
            if user['password'] == currentUser['Item']['password']:
                return {
                    "statusCode": 200,
                    "headers": {"Content-Type": "application/json",
                                'Access-Control-Allow-Origin': '*',
                                'Access-Control-Allow-Credentials': True},
                    "body": json.dumps(currentUser['Item'])
                }
            else:
                return {
                    "statusCode": 400,
                    "headers": {"Content-Type": "application/json",
                                'Access-Control-Allow-Origin': '*',
                                'Access-Control-Allow-Credentials': True},
                }
        else:
            return {
                "statusCode": 500,
                "headers": {"Content-Type": "application/json",
                            'Access-Control-Allow-Origin': '*',
                            'Access-Control-Allow-Credentials': True},
            }

    except Exception as err:
        print(err)
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json",
                                        'Access-Control-Allow-Origin': '*',
                                        'Access-Control-Allow-Credentials': True},
            "body": json.dumps(err)
        }
