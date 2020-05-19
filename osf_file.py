import os

import requests

API_ENDPOINT = "https://api.osf.io/v2/files"
VIEW_ONLY_KEY = "1c79efb782e54b05acd3b1aa2dd375fd"


def retrieve_file(url):
    guid = os.path.split(url)[-1]
    r = requests.get(
        os.path.join(API_ENDPOINT, guid, "?view_only=" + VIEW_ONLY_KEY))
    url_download = r.json()['data']['links']['download']
    r = requests.get(url_download)
    return r.content


"""Test script."""

TEST_URL_XML = "https://osf.io/5wqsg/files/osfstorage/5cf1d30223fec40017f187ca"
TEST_URL_PDF = "https://osf.io/hcxdq/files/osfstorage/5cf1c86b2a50c4001880bd77"

f = retrieve_file(TEST_URL_PDF)
