import praw_config, praw, re, os
from dlr_helper import scrape_album_links, download_pics
from load_to_firebase import upload_to_storage_db

dir = "C:\\Users\\wazih\\Desktop\\courses\\Images"

reddit = praw.Reddit(client_id=praw_config.client_id, 
                     client_secret=praw_config.client_secret, 
                     user_agent=praw_config.user_agent)


urls = []
for submissions in reddit.subreddit('iWallpaper').new(limit=250):
    urls = urls + [submissions.url]


imgur_regex = re.compile(r'((https|http)://imgur.com/a/\w+)|((https|http)://imgur.com/gallery/\w+)')

album_urls = []
pic_urls = []

for url in urls:
    try:
        mo = imgur_regex.search(url)
        album_urls = album_urls + [mo.group()]
    except AttributeError:
        pic_urls = pic_urls + [url]


download_pics(pic_urls)

print("\nDone with part 1")

scrape_album_links(album_urls, "links")

print("\n now chuncking...")

# print("\nuploading to firebase")

# upload_to_storage_db()
