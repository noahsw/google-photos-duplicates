import dbm, sys, json, os, requests, hashlib
from PIL import Image

def main():
    path = sys.argv[1]

    md5hash = hashlib.md5(Image.open(path).tobytes())
    hash = md5hash.hexdigest()

    print(str(hash))

    with dbm.open('hash_store.db', 'r') as db:
        media_item = json.loads(db[hash])

    print("DUPLICATE:")    
    print(media_item)


if __name__ == "__main__":
    main()