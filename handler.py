import json
import os
import base64
import boto3


def create_uule_parameter(canonical_name):
    """
    creates uule parameter based on given canonical_name of location
    """
    uule_start = 'w+CAIQICI'
    secret_key_dict = json.load(
        open(os.path.join("data", "uule_secret_key.json"), encoding="utf-8"))

    b64 = base64.b64encode(canonical_name.encode("utf-8")).decode("utf-8")
    secret_key = secret_key_dict[str(len(canonical_name))]
    uule = uule_start + secret_key + b64

    return uule


def write_uule_to_dynamo(canonical_name, uule, table_name='cities'):
    # auf cities table ausgelegt
    # Get the service resource.
    dynamodb = boto3.resource('dynamodb', region_name='us-west-2')

    table = dynamodb.Table(table_name)
    print(table)

    response = table.update_item(
        Key={
            'canonicalName': canonical_name
        },
        UpdateExpression="set uule = :u",
        ExpressionAttributeValues={
            ':u': uule,
        },
        ReturnValues="UPDATED_NEW"
    )
    if (response["ResponseMetadata"]["HTTPStatusCode"] == 200):
        print('updated uule parameter')
    else:
        print('updated uule failed')

    return response['Attributes']


def get_uule(event, context):
    data = json.loads(event['body'])
    canonicalName = data['canonicalName']
    # create uule parameter
    uule = create_uule_parameter(canonicalName)
    # update database with new uule parameter
    result = write_uule_to_dynamo(canonicalName,uule)

    response = {
        "statusCode": 200,
        "headers": {
        "Access-Control-Allow-Origin" : "*"
        },
        "body": json.dumps(result)
    }
    return response

