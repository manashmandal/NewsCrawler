import os
import requests
import shutil

BUFFER = 1024


def download_image(news_item):
    url = news_item['images']
    moveto = ".//" + news_item['newspaper_name'] + '//' + str(news_item['_id'])
    filename = url.split('/')[-1]
    r = requests.get(url, stream=True)
    with open(filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=BUFFER):
            if chunk:
                f.write(chunk)
    if not os.path.exists(moveto):
        os.makedirs(moveto)
    shutil.move('./' + filename, moveto)