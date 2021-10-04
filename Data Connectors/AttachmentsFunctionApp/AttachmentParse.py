import logging
import azure.functions as func
from azure.storage.blob import BlobClient
from zipfile import ZipFile
import requests
from io import BytesIO
import datetime
import hashlib
import hmac
import base64
import json

log_type = 'AttachmentLogs'

def build_signature(customer_id, shared_key, date, content_length, method, content_type, resource):
    x_headers = 'x-ms-date:' + date
    string_to_hash = method + "\n" + str(content_length) + "\n" + content_type + "\n" + x_headers + "\n" + resource
    bytes_to_hash = bytes(string_to_hash, encoding="utf-8")
    decoded_key = base64.b64decode(shared_key)
    encoded_hash = base64.b64encode(hmac.new(decoded_key, bytes_to_hash, digestmod=hashlib.sha256).digest()).decode()
    authorization = "SharedKey {}:{}".format(customer_id,encoded_hash)
    return authorization

def post_data(customer_id, shared_key, body, log_type):
    method = 'POST'
    content_type = 'application/json'
    resource = '/api/logs'
    rfc1123date = datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
    content_length = len(body)
    signature = build_signature(customer_id, shared_key, rfc1123date, content_length, method, content_type, resource)
    uri = 'https://' + customer_id + '.ods.opinsights.azure.com' + resource + '?api-version=2016-04-01'

    headers = {
        'content-type': content_type,
        'Authorization': signature,
        'Log-Type': log_type,
        'x-ms-date': rfc1123date
    }

    response = requests.post(uri,data=body, headers=headers)
    if (response.status_code >= 200 and response.status_code <= 299):
        print('Accepted')
    else:
        print("Response code: {}".format(response.status_code))


def extract_zip(cdn_url, req_body):
    if cdn_url[0:4] == "http":
        get_zip = requests.get(cdn_url).content
    else:
        get_zip = cdn_url
    file = ZipFile(BytesIO(get_zip))
    for filename in file.namelist():
        # file_info = file.getinfo(filename)
        name = filename.rsplit('/',1)[-1]
        if name == "":
            continue
        elif name.split(".")[1] == "zip":
            extract_zip(file.open(filename).read(), req_body)
        elif name.split(".")[1] not in req_body.get('extensions'):
        # else:
            post_data(
                req_body.get("customer_id"),
                req_body.get('shared_key'),
                json.dumps(
                    {
                        "content": req_body.get('content'),
                        "author": req_body.get('author'), 
                        "channelid": req_body.get('channelid'),
                        "channel": req_body.get('channel'),
                        "content_type": name.split(".")[1],
                        "attachmentid": req_body.get('attachmentid'),
                        "filesize": file.getinfo(filename).file_size,
                        "filename": req_body.get('attachmentid') + name
                    }),
                log_type)
            blob = BlobClient.from_connection_string(
                conn_str = req_body.get("filestorage"),
                container_name="discord-attachments",
                blob_name = req_body.get('attachmentid') + name)
            blob.upload_blob(file.open(filename).read())

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    cdn_url = req.params.get('cdn_url')
    req_body = req.get_json()
    if cdn_url:
        filename = cdn_url.rsplit('/', 1)[-1]
        extension = filename.split(".")[1]
        if extension == "zip":
            extract_zip(cdn_url, req_body)
        elif extension not in req_body.get('extensions'):
        # else:
            post_data(
                req_body.get("customer_id"),
                req_body.get('shared_key'),
                json.dumps(
                    {
                        "content": req_body.get('content'),
                        "author": req_body.get('author'), 
                        "channelid": req_body.get('channel'),
                        "content_type": req_body.get('content_type'),
                        "attachmentid": req_body.get('attachmentid'),
                        "filesize": req_body.get('filesize'),
                        "filename": req_body.get('attachmentid') + filename
                    }),
                log_type)
            blob = BlobClient.from_connection_string(
                conn_str = req_body.get("filestorage"), 
                container_name="discord-attachments", 
                blob_name = req_body.get('attachmentid') + filename)
            blob.upload_blob_from_url(cdn_url)
    return func.HttpResponse(f"test")