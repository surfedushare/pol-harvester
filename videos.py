# TO RUN THIS CODE
# cp .env.development .env
# docker-compose run harvester python manage.py shell
# copy paste code into the terminal

import os
import json
from shutil import copy2

from django.db.models import Q

from pol_harvester.models import Freeze, YouTubeDLResource


freeze = Freeze.objects.last()
targets = []


youtube_url = Q(properties__url__startswith="https://www.youtube.com")
vimeo_url = Q(properties__url__startswith="https://vimeo")
lecturenet_url = Q(properties__url__startswith="https://lecturenet")
ou_url = Q(properties__url__startswith="https://player.ou.nl")
leraar24 = Q(collection__name="leraar24")
video_type = Q(properties__mime_type__startswith="video")


videos = freeze.documents.filter(youtube_url | vimeo_url | lecturenet_url | ou_url | leraar24 | video_type) \
    .filter(properties__text__isnull=False)
print(videos.count())

english = videos.filter(properties__language__from_title="en")
print(english.count())

dutch = videos.filter(properties__language__from_title="nl")
print(dutch.count())


hbovpk_en = english.filter(collection__name="hbovpk")
print(hbovpk_en.count())
hbovpk_nl = dutch.filter(collection__name="hbovpk")
print(hbovpk_nl.count())
for d in hbovpk_en.order_by("?")[:20]:
    targets.append(d)
for d in hbovpk_nl.order_by("?")[:20]:
    targets.append(d)

leraar24_nl = dutch.filter(collection__name="leraar24")
print(leraar24_nl.count())
for d in leraar24_nl.order_by("?")[:20]:
    targets.append(d)

surf_en = english.filter(collection__name="stimuleringsregeling")
print(surf_en.count())
surf_nl = dutch.filter(collection__name="stimuleringsregeling")
print(surf_nl.count())
for d in surf_en.order_by("?")[:55]:
    targets.append(d)
for d in surf_nl.order_by("?")[:20]:
    targets.append(d)


DEST = "../media/audio/gold-transcriptions"
selection = []

for target in targets:
    url = target.properties["url"]
    yt = YouTubeDLResource(config={"fetch_only": True}).run(url)
    if not yt.success:
        print("Problem with YoutubeDL: {} {} {}".format(target.id, yt.id, url))
        continue
    _, file_paths = yt.content
    file_path = file_paths[0]
    tail, head = os.path.split(file_path)
    copy2(file_path.replace("/data/", "../"), os.path.join(DEST, head))
    doc = target.content
    doc["file"] = head
    selection.append(doc)

with open("gold-transcriptions-documents.json", "w") as json_file:
    json.dump(selection, json_file, indent=4)
