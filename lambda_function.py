import json
import boto3
import logging

# Initialize logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

ENDPOINT_NAME = "jumpstart-dft-meta-textgeneration-llama-3-2-1b"
runtime = boto3.client("runtime.sagemaker")

def lambda_handler(event, context):

    # Log the event at INFO level
    logger.info("Received Event: %s", json.dumps(event, indent=2))

    # Parse the input JSON body
    if "body" in event:
        body = json.loads(event["body"])
    else:
        logger.info("No request body found in the event.")
        body = event

    # Extract the input payload for the SageMaker endpoint
    if "inputs" not in body or "parameters" not in body:
        logger.info("Invalid input format. Expected 'inputs' and 'parameters' keys.")

    try:
        
        # Convert the input data to JSON string
        payload_json = json.dumps(body)

        # Invoke SageMaker endpoint
        response = runtime.invoke_endpoint(
            EndpointName=ENDPOINT_NAME,
            ContentType='application/json',
            Body=json.dumps(body),
            CustomAttributes="accept_eula=true"
        )
        
        # Parse the response
        response_content = response['Body'].read().decode()
        logger.info(f"SageMaker response: {response_content}")

        return {
            'statusCode': 200,
            'body': response_content
        }
    
    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        return {
            'statusCode': 500,
            'body': f'Error occurred: {str(e)}'
        }