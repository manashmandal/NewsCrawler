import os
import requests
import shutil

BUFFER = 1024

# Default ".//"
DOWNLOAD_PATH_PREFIX = "..//downloaded_images//"


def download_image(news_item):
    url = news_item['images']
    # moveto = DOWNLOAD_PATH_PREFIX + \
        # news_item['newspaper_name'] + '//' + str(news_item['_id'])
    moveto = DOWNLOAD_PATH_PREFIX + str(news_item['_id'])

    filename = url.split('/')[-1]
    # Check if needed
    filename = filename.split('?')[0]
    r = requests.get(url, stream=True)

    with open(filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=BUFFER):
            if chunk:
                f.write(chunk)

    if not os.path.exists(moveto):
        os.makedirs(moveto)
    # move file after downloading
    try:
        shutil.move('./' + filename, moveto)
    except:
        print "Download error or file already exists"


def download_multiple_image(news_item):
    # moveto = DOWNLOAD_PATH_PREFIX + \
        # news_item['newspaper_name'] + '//' + str(news_item['_id'])
    moveto = DOWNLOAD_PATH_PREFIX + news_item['_id']

    for url in news_item['images']:
        r = requests.get(url, stream=True)
        filename = url.split('/')[-1]
        filename = filename.split('?')[0]
        print "IMAGE FILE: ", filename

        with open(filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=BUFFER):
                if chunk:
                    f.write(chunk)

        if not os.path.exists(moveto):
            os.makedirs(moveto)
        # Moving the file after downloading
        try:
            shutil.move('./' + filename, moveto)
        except:
            print "Download error or file already exists"
