import requests, imagehash, dbm, json, os, sys, getopt
from PIL import Image


key = ""
authorization = ""

try:
    opts, args = getopt.getopt(sys.argv[1:] , "", ["key=","authorization="])
except getopt.GetoptError:
    print("find-duplicates.py --key=<key> --authorizaton=<authorization>")
    sys.exit(2)
for opt, arg in opts:
    if opt == '-h':
        print("find-duplicates.py --key=<key> --authorizaton=<authorization>")
        sys.exit()
    elif opt in ("--authorization"):
        authorization = arg
    elif opt in ("--key"):
        key = arg


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
            print("Skipping " + media_item['id'] + " because we've already downloaded it!")
            return
        else:
            db[media_item['id']] = "1"

    filename = media_item['filename']
    baseUrl = media_item['baseUrl'] + "=w640-h480"

    path = "tmp/" + filename

    if os.path.isfile(path):
        return

    r = requests.get(baseUrl)
    open(path, 'wb').write(r.content)

    hash = str(imagehash.average_hash(Image.open(path)))

    print("Saved " + media_item['id'] + " to " + path + " w/ hash " + hash)

    with dbm.open('hash_store.db', 'c') as db:
        if hash in db:
            print("DUPLICATE found!")
            with dbm.open('duplicate_store.db', 'c') as duplicate_db:
                print(json.dumps(media_item))
                duplicate_db[media_item['id']] = json.dumps(media_item)
            # add_media_time_to_album(media_item, album_id)
        else:
            db[hash] = json.dumps(media_item)

    if os.path.exists(path):
        os.remove(path)


def add_media_time_to_album(media_item, album_id):
    data = (
        ('key', key),
        ("mediaItemIds", [media_item['id']])
    )

    response = requests.post("https://content-photoslibrary.googleapis.com/v1/albums/" + album_id + ":batchAddMediaItems", headers=headers, data=data)




def main():
    params = (
        ('key', key),
    )

    """

    response = requests.post('https://photoslibrary.googleapis.com/v1/albums', headers=headers, data=data)


    response = requests.get('https://content-photoslibrary.googleapis.com/v1/albums?pageSize=50', headers=headers, params=params)
    albums = response.json()['albums']

    i = 0
    for album in albums:
        i += 1
        print(str(i) + ". " + album['title'])

    print("")
    print("Which album to store duplicates?")
    album_index = int(input())

    album = albums[album_index - 1]
    album_id = album['id']
    album_name = album['title']
    """


    ### ITERATE THROUGH FILES
    next_page_token = ""
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
        else:
            break


if __name__ == "__main__":
    main()