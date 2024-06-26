from google.cloud import storage
import uuid
import io
import os
from urllib.parse import urlparse
import mimetypes
import json
import logging

logger = logging.getLogger(__name__)

def upload_to_gcs(image):
    api_credentials = os.environ.get('IMAGE_ANALYSIS_CREDENTIALS')
    api_credentials = json.loads(api_credentials)
    bucket_name = api_credentials['BUCKET_NAME']

    client = storage.Client()
    bucket = client.bucket(bucket_name)

    try:
    
        # Determine the original format and file extension
        original_format = image.format or 'PNG'
        file_extension = f".{original_format.lower()}"
        content_type = f'image/{original_format.lower()}'
        
        blob_name = f"uploads/{uuid.uuid4()}{file_extension}"
        blob = bucket.blob(blob_name)
        
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format=original_format)
        img_byte_arr = img_byte_arr.getvalue()
        
        blob.upload_from_string(img_byte_arr, content_type=content_type)

    except Exception as e:
        logger.error(f"Failed to upload file from GCS: {str(e)}")
        raise
    
    return f"gs://{bucket_name}/{blob_name}"


def download_from_gcs(gcs_path, local_dir="resources/img", file_prefix=""):
    api_credentials = os.environ.get('IMAGE_ANALYSIS_CREDENTIALS')
    api_credentials = json.loads(api_credentials)
    bucket_name = api_credentials['BUCKET_NAME']

    client = storage.Client()

    # Parse the GCS path
    parsed_path = urlparse(gcs_path)
    blob_name = parsed_path.path.lstrip('/')
    
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    try:
        # Get file extension from the blob name
        _, file_extension = os.path.splitext(blob_name)

        # Determine file name
        if file_prefix:
            local_filename = f"{file_prefix}{file_extension}"
        else:
            local_filename = os.path.basename(blob_name)
    
        # Ensure the local directory exists
        os.makedirs(local_dir, exist_ok=True)
        
        # Construct the full local path
        local_path = os.path.join(local_dir, local_filename)
        
        # Download the blob
        blob.download_to_filename(local_path)

    except Exception as e:
        logger.error(f"Failed to download file from GCS: {str(e)}")
        raise
    
    return local_path