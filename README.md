# google-photos-duplicates

I created this because when I moved my photo library to Google Photos, I ended up with duplicates for most photos. One photo was imported by Google Drive and the duplicate was imported by Backup and Sync. Google Photos has no mechanism to delete these for me so I built this tool to do it.

```python
pipenv install
pipenv run python3 find-duplicates.py --key=<key> --authorization=<authorization without "Bearer">
pipenv run python3 delete-duplicates.py
```
