import os
import openai
import json
from flask import Flask

app = Flask(__name__)
openai.api_key = os.environ['OPEN_API']


@app.route("/save-recipe", methods=['POST'])
def save_recipe(event, context):
    import boto3
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('recipesTable')
    recipe = json.loads(event['body'])
    saved_recipe = table.put_item(Item=recipe)
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json",
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Credentials': True},
        "body": json.dumps({"recipe": "saved"})
    }


@app.route("/get-recipe", methods=["GET"])
def get_recipe(event, context):
    food = event['queryStringParameters']['food']
    # email = event['queryStringParameters']['email']
    try:
        if check_if_exists(food):
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json",
                                            'Access-Control-Allow-Origin': '*',
                                            'Access-Control-Allow-Credentials': True},
                "body": json.dumps({"recipe": check_if_exists(food), "img": ""})
            }
        check_is_food(food)
        if check_is_food(food):
            # img_url = generate_photo(food)
            recipe = generate_recipe(food)
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json",
                                            'Access-Control-Allow-Origin': '*',
                                            'Access-Control-Allow-Credentials': True},
                "body": json.dumps({"recipe": recipe, "img": ""})
            }
        else:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json",
                                            'Access-Control-Allow-Origin': '*',
                                            'Access-Control-Allow-Credentials': True},
                "body": json.dumps("Not a food")
            }
    except Exception:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json",
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Credentials': True},
            "body": json.dumps("Try again!")
        }


def generate_photo(food):
    response = openai.Image.create(
        prompt="a picture of " + food + " from chefai.reipes",
        n=1,
        size="512x512"
    )
    image_url = response['data'][0]['url']
    return image_url


def generate_recipe_prompt(food):
    return """List steps for cooking {} and include ingredients """.format(
        food.capitalize(), food.capitalize()
    )


def generate_food_check_prompt(food):
    return """Is {} considered food?""".format(
        food.capitalize()
    )


def check_is_food(food):
    is_food = openai.Completion.create(
        model="text-davinci-003",
        prompt=generate_food_check_prompt(food),
        temperature=0,
        max_tokens=4
    )
    return 'Yes' in is_food.choices[0].text


def generate_recipe(food):
    recipe = openai.Completion.create(
        model="text-davinci-003",
        prompt=generate_recipe_prompt(food),
        temperature=0,
        max_tokens=2048
    )
    return recipe.choices[0].text


def check_if_exists(food):
    import boto3
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('recipesTable')
    recipe = response = table.get_item(
        Key={
            'title': food,
        }
    )
    if 'Item' in recipe:
        return recipe['Item']
    else:
        return False


def redeem_credits(email):
    import boto3
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('usersTable')
    user = response = table.get_item(
        Key={
            'email': email,
        }
    )
    if 'Item' in user and user['Item']['credits'] > 0:
        table.update_item(
            Key={
                'email': email
            },
            UpdateExpression="set credits = :r",
            ExpressionAttributeValues={
                ':r': user['Item']['credits'] - 1,
            },
            ReturnValues="UPDATED_NEW"
        )
    updatedUser = response = table.get_item(
        Key={
            'email': user['Item']['email'],
        }
    )
    return updatedUser['Item']['credits'] != user['Item']['credits']
