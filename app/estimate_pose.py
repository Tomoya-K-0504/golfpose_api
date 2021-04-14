import requests
import pprint
from pathlib import Path
import datetime as dt
from typing import Dict, List
import pandas as pd
import json
import argparse
from io import StringIO, BytesIO
import os
import yaml
from typing import Union
from pathlib import Path
import cv2

from google.cloud import storage

import posenet      # importに5.5秒かかってる
import process_video


GCP_CREDENTIAL = Path(__file__).resolve().parent / 'gcp_all.json'
# BUCKET_NAME = 'tuto1'
# PROJECT_ID = 'sonorous-cacao-310307'
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = str(GCP_CREDENTIAL)


# REGION=asia-northeast1
# BUCKET_NAME=pose_ai_platform1
# gsutil mb -l $REGION gs://$BUCKET_NAME


def read_video_from_gcs(file_path) -> Union[pd.DataFrame, None]:
    bucket_name = file_path.replace('gs://', '').split('/')[0]
    file_name = file_path.replace(f'gs://{bucket_name}/', '')

    blob = storage.Client().bucket(bucket_name).blob(file_name)
    if blob.exists():
        blob.download_to_filename(file_name)
        return bucket_name, file_name
    else:
        return False


def estimate(file_path):
    bucket_name, video_path = read_video_from_gcs(file_path)
    feature_path = process_video.process(video_path)
    return feature_path
    # return f'gs://{bucket_name}/{feature_path}'


if __name__ == '__main__':
    file_path = 'gs://tuto1/short_video.mp4'
    print(estimate(file_path))