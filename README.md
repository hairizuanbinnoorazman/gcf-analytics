# gcf-analytics

Using google cloud functions to run analytics functions

The following project has been set up with continuous deployment in mind. This would automatically deploy the code to Google Cloud Functions immdiately.

# Deploying

- Upload the configuration file to GCS bucket via the following command

```bash
gsutil cp ./config.json gs://gcf-test-analytics/config/config.json
```

- Convert `pipfile` dependencies to `requirements.txt` file

```bash
pipenv lock --requirements > requirements.txt
```

- Currently, only the master is being used to deploy a new version of the application to production.
  Do deploy the latest change meant to be put to production:

```bash
git push -f google alt_branch:master
```

# Quick test

One of the initial functions that is needed to be used for this is the capability to ping Google Cloud Storage and that being able to trigger analytics functions.

```bash
# Copy files over to Google Cloud Storage
gsutil cp ./test.json gs://gcf-test-analytics

# Remove file from google cloud storage
gsutil rm gs://gcf-test-analytics/test.json
```

Sending over the correct/incorrect datasets

```bash
# Send over correctly formatted csv data
gsutil cp ./test_correct_data.csv gs://gcf-test-analytics

# Send over incorrectly formatted csv data
gsutil cp ./test_incorrect_data.csv gs://gcf-test-analytics
```
