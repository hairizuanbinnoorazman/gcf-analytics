# gcf-analytics

Using google cloud functions to run analytics functions

The following project has been set up with continuous deployment in mind. This would automatically deploy the code to Google Cloud Functions immdiately.

# Quick test

One of the initial functions that is needed to be used for this is the capability to ping Google Cloud Storage and that being able to trigger analytics functions.

```bash
# Copy files over to Google Cloud Storage
gsutil cp ./test.json gs://gcf-test-analytics

# Remove file from google cloud storage
gsutil rm gs://gcf-test-analytics/test.json
```
