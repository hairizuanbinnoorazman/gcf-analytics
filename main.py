from google.cloud import storage
from google.cloud import datastore
from google.cloud import pubsub
import pandas as pd
import datetime
import logging
import base64
import json
import uuid


import slack
import analytics_check


# Retrieve configuration files
client = storage.Client()
bucket = client.get_bucket('gcf-test-analytics')
blob = bucket.get_blob('config/config.json')
keys = blob.download_as_string()
keys_json = json.loads(keys)

# Retrieve slack channel id
slack_token = keys_json['slack_token']
slack_channel_name = keys_json['slack_channel_name']
channel_id = slack.get_channel_list(slack_token, slack_channel_name)

# Define datastore
datastore_client = datastore.Client()

# Define pubsub
pubsub_client = pubsub.PublisherClient()


def main(data, context):
    """Background Cloud Function to be triggered by Cloud Storage.
    Args:
         data (dict): The dictionary with data specific to this type of event.
         context (google.cloud.functions.Context): The Cloud Functions
         event metadata.
    """
    bucket_id = data['bucket']
    path = data['name']
    logging.warning(data)

    assert isinstance(bucket_id, str), "Bucket id provided is not a string"
    assert isinstance(path, str), "Filename provided is not a string"

    slack.send_text_to_channel(
        slack_token, channel_id, "Received csv file. Will begin checking")

    # Download file and process it
    data_blob = bucket.blob(path)
    if "/" in path:
        folder_name, file_name = path.split("/", 1)
        # If csv extension not in file_name, its wrong and needs to be returned
        if ".csv" not in file_name:
            logging.error("Excepted csv file but .csv extension not found")
            return
    else:
        file_name = path

    try:
        data_blob.download_to_filename("/tmp/{}".format(file_name))
        data = pd.read_csv("/tmp/{}".format(file_name))
    except Exception as e:
        logging.error(e)
        return

    err_list = analytics_check.run_check(data)
    if len(err_list) > 0:
        error_text = ""
        for item in err_list:
            error_text = "{}\n{}".format(error_text, item)
        slack.send_text_to_channel(
            slack_token, channel_id, error_text)
        return
    else:
        slack.send_text_to_channel(slack_token, channel_id, "All good")

    # Store passed file into datastore
    key = datastore_client.key('ReportSubmission', str(uuid.uuid4()))
    entity = datastore.Entity(key=key)
    entity.update({
        "submission_date": datetime.datetime.now().strftime("%Y-%m-%d"),
        "report_type": folder_name
    })
    datastore_client.put(entity)

    # Query for results
    query = datastore_client.query(kind='ReportSubmission')
    query.add_filter("submission_date", "=",
                     datetime.datetime.now().strftime("%Y-%m-%d"))
    report_items = list(query.fetch())
    report_items = [x['report_type'] for x in report_items]
    expected_items = ['test1', 'test2', 'test3']
    for expected_item in expected_items:
        if expected_item not in report_items:
            logging.warning("Not all reports submitted")
            return
    logging.warning("Can send pubsub report now")

    pub_message = '{"status":"completed"}'.encode("ascii")
    pubsub_client.publish("gcf-test-analytics", base64.b64encode(pub_message))


def pubsubber(data, context):
    pubsub_data = data['data']
    pubsub_data = base64.b64decode(pubsub_data)
    logging.warning(pubsub_data)

    path1 = "test1/test_correct_data.csv"
    path2 = "test2/test_correct_data.csv"
    path3 = "test3/test_correct_data.csv"

    data_blob = bucket.blob(path1)
    data_blob.download_to_filename("/tmp/{}".format("test_correct_data.csv"))
    data = pd.read_csv("/tmp/test_correct_data.csv")

    total_rows = len(data) * 3
    slack.send_text_to_channel(
        slack_token, channel_id, "Number of rows in all datasets is {}".format(total_rows))
