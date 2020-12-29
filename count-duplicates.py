import dbm, sys, json

def count_history():
    with dbm.open('history_store.db', 'r') as db:
        k = db.firstkey()
        total = 0
        while k != None:
            total += 1
            k = db.nextkey(k)
    return total

def main():
    history_count = count_history()

    with dbm.open('duplicate_store.db', 'r') as db:
        k = db.firstkey()
        total = 0
        remaining = 0
        while k != None:
            total += 1
            if len(db[k]) > 0:
                remaining += 1
            k = db.nextkey(k)
    print(str(remaining) + " duplicates remaining out of " + str(total) + " (total history: " + str(history_count) + ")")



if __name__ == "__main__":
    main()