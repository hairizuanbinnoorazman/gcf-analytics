from google.cloud import storage
import pandas as pd
import logging
import json

import slack
import analytics_check


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
    else:
        slack.send_text_to_channel(slack_token, channel_id, "All good")
