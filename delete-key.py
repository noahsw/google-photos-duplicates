import dbm, sys, json

def main():
    key = sys.argv[1]
    print(key)
    with dbm.open('duplicate_store.db', 'c') as db:
        k = db.firstkey()
        while k != None:
            try:
                media_item = json.loads(db[k])
            except:
                k = db.nextkey(k)
                continue
            if media_item['id'] == key:
                db[k] = ""
                print("Key deleted!")
                break
            k = db.nextkey(k)



if __name__ == "__main__":
    main()