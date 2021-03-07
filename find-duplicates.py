import requests, hashlib, dbm, json, os, sys, getopt
from PIL import Image


key = sys.argv[1]

print("Authorization? Remove the Bearer part")
authorization = input()

headers = {
    'authority': 'content-photoslibrary.googleapis.com',
    'x-goog-encode-response-if-executable': 'base64',
    'x-origin': 'https://explorer.apis.google.com',
    'x-clientdetails': 'appVersion=5.0%20(Macintosh%3B%20Intel%20Mac%20OS%20X%2010_15_6)%20AppleWebKit%2F537.36%20(KHTML%2C%20like%20Gecko)%20Chrome%2F85.0.4183.83%20Safari%2F537.36&platform=MacIntel&userAgent=Mozilla%2F5.0%20(Macintosh%3B%20Intel%20Mac%20OS%20X%2010_15_6)%20AppleWebKit%2F537.36%20(KHTML%2C%20like%20Gecko)%20Chrome%2F85.0.4183.83%20Safari%2F537.36',
    'authorization': 'Bearer ' + authorization,
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36',
    'x-requested-with': 'XMLHttpRequest',
    'x-javascript-user-agent': 'apix/3.0.0 google-api-javascript-client/1.1.0',
    'x-referer': 'https://explorer.apis.google.com',
    'accept': '*/*',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-mode': 'cors',
    'sec-fetch-dest': 'empty',
    'accept-language': 'en-US,en;q=0.9',
}



def compare_media_item(media_item):

    with dbm.open('history_store.db', 'c') as db:
        if media_item['id'] in db:
            print("Already compared " + media_item['id'] + " (" + media_item['mediaMetadata']['creationTime'] + ")")
            return
        else:
            db[media_item['id']] = json.dumps(media_item)

    filename = media_item['filename']
    baseUrl = media_item['baseUrl'] + "=w" + media_item['mediaMetadata']['width'] + "-h" + media_item['mediaMetadata']['height']

    path = "tmp/" + filename

    if os.path.isfile(path):
        return

    r = requests.get(baseUrl)
    open(path, 'wb').write(r.content)

    # no need to convert HEIC to JPG as PIL supports HEIC
    md5hash = hashlib.md5(Image.open(path).tobytes())
    hash = md5hash.hexdigest()

    print("Saved " + media_item['id'] + " -> md5 " + hash + " @ " + media_item['mediaMetadata']['creationTime'])

    with dbm.open('hash_store.db', 'c') as db:
        if hash in db:
            print("")
            print("DUPLICATE found!")
            print(json.dumps(media_item))
            print("")
            print("Duplicate info: " + str(db[hash]))
            print("")
            with dbm.open('duplicate_store.db', 'c') as duplicate_db:
                duplicate_db[media_item['id']] = json.dumps(media_item)
        else:
            db[hash] = json.dumps(media_item)

    if os.path.exists(path):
        os.remove(path)

def main():
    params = (
        ('key', key),
    )

    ### ITERATE THROUGH FILES
    next_page_token = ""
    page_count = 1
    while True:
        params = {
            'key': key,
            'pageToken': next_page_token,
            'pageSize': 100
        }

        json = {
            'filters': {
                "dateFilter": {
                    "ranges": [
                        {
                            "endDate": {
                                "year": 2005
                            },
                            "startDate": {
                                "year": 2004
                            }
                        }
                    ]
                }
            }
        }

        response = requests.post('https://content-photoslibrary.googleapis.com/v1/mediaItems:search', headers=headers, params=params, json=json)
        # print(response.content)

        json = response.json()
        media_items = json['mediaItems']
        for media_item in media_items:
            if media_item['mimeType'] == "image/jpeg" or media_item['mimeType'] == "image/heif":
                compare_media_item(media_item)

        if "nextPageToken" in json:
            next_page_token = json['nextPageToken']
            print("Page " + str(page_count) + "...")
            page_count += 1
        else:
            break


if __name__ == "__main__":
    main()