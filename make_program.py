import yaml
import os


template = """
---
layout: paper
id: {id}
slides_live_id: 38915748
rocket_id: {rocket_id}
meeting_url: 
authors: "{authors}"
camera_ready: {camera_ready}
cmt_id: {cmt_id}
kind: {kind}
session_id: {session_id}
session_title: "{session_title}"
title: "{title}"
track: {track}
live: {live}
---
""".strip()


files = os.listdir("program")
for file in files:
	os.remove(os.path.join("program", file))


with open("_data/sessions.yml", "r") as fh:
	sessions = yaml.load(fh)

for session in sessions:
	for paper in session["papers"]:
		print(paper["id"])
		paper["camera_ready"] = str(paper["camera_ready"]).lower()
		paper["session_id"] = session["id"]
		paper["session_title"] = session["title"]
		paper["title"] = paper["title"].replace("\"", "\\\"")
		if paper["id"] > 0:
			paper["rocket_id"] = "baics_channel_{:02d}".format(paper["id"])
		else:
			paper["rocket_id"] = "baics_channel_{}".format(paper["id"])
		paper["live"] = "false"

		html = template.format(**paper)

		path = "program/baics_{}.html".format(paper["id"])
		assert not os.path.exists(path)
		with open(path, "w") as fh:
			fh.write(html)


with open("_data/speakers.yml", "r") as fh:
	speakers = yaml.load(fh)

for speaker in speakers:
	print(speaker["id"])
	speaker["camera_ready"] = "false"
	speaker["session_id"] = 0
	speaker["session_title"] = speaker["kind"]
	speaker["title"] = speaker["title"].replace("\"", "\\\"")
	speaker["cmt_id"] = -1
	speaker["track"] = speaker["kind"]
	speaker["rocket_id"] = "baics_channel_{:02d}".format(speaker["id"])
	speaker["live"] = str(speaker.get("live", False)).lower()

	html = template.format(**speaker)

	path = "program/baics_{}.html".format(speaker["id"])
	assert not os.path.exists(path)
	with open(path, "w") as fh:
		fh.write(html)