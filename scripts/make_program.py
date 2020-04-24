import yaml
import os
import pandas as pd

import zoom


INCLUDE_MEETING_URLS = False
TEMPLATE = """
---
layout: paper
id: {unique_id}
slides_live_id: {slides_live_id}
rocket_id: {rocket_id}
meeting_url: {meeting_url}
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


def format_authors(x):
  authors = x.split(";")
  for i in range(len(authors)):
    author = authors[i]
    author = author.strip()
    last, first = author.split(",")
    first = first.strip()
    last = last.strip()
    author = "{} {}".format(first, last)
    authors[i] = author

  if len(authors) == 1:
    x = authors[0]
  elif len(authors) == 2:
    x = "{} and {}".format(*authors)
  else:
    first = ", ".join(authors[:-1])
    last = authors[-1]
    x = "{}, and {}".format(first, last)
  
  return x


def load_presentation_data():
    data = pd.read_csv("scripts/data/presentations.csv")
    data["session_title"] = data["session"].replace({
        "invited": "Invited Talk",
        "opening": "Opening Remarks",
        "2-3 pm GMT": "Session 1 (2-3pm GMT)",
        "9-10 pm GMT": "Session 2 (9-10pm GMT)",
    })
    data["session_id"] = data["session"].replace({
        "invited": 0,
        "opening": 0,
        "2-3 pm GMT": 1,
        "9-10 pm GMT": 2,
    })
    data = data.drop(columns=["session"])
    data["authors"] = data["authors"].apply(format_authors)
    return data


def make_jekyll_data():
    data = load_presentation_data()
    data = data.sort_values(by="authors")
    data = data.rename(columns={
        "session_id": "session",
        "unique_id": "id"
    })
    data = data.drop(columns=[
        "presenter_email",
        "presenter_name",
        "slides_live_id",
        "live",
    ])

    # Process sessions.
    sessions = []
    for session in [1, 2]:
        session_data = data.query("session == {}".format(session))
        session_title, = session_data["session_title"].unique()
        session_data = pd.concat([
            session_data.query("kind == 'oral'"),
            session_data.query("kind == 'spotlight'"),
            session_data.query("kind == 'poster'"),
        ])
        session_data = session_data.drop(columns=["session_title"])
        sessions.append({
            "id": session,
            "title": session_title,
            "papers": session_data.to_dict(orient="records")
        })
    with open("_data/sessions.yml", "w") as fh:
        yaml.dump(sessions, fh)

    # Process speakers.
    speakers = data.query("session == 0")
    speakers = speakers.sort_values(by="id")
    speakers = speakers.drop(columns=[
        "cmt_id",
        "camera_ready",
        "session",
        "session_title",
        "track",
    ])
    speakers = speakers.to_dict(orient="records")
    with open("_data/speakers.yml", "w") as fh:
        yaml.dump(speakers, fh)


def make_program():
    # Delete existing files.
    files = os.listdir("program")
    for file in files:
        os.remove(os.path.join("program", file))

    all_data = load_presentation_data().to_dict(orient="records")
    for data in all_data:
        print(data["unique_id"])

        if INCLUDE_MEETING_URLS:
            meeting_id = "BAICS_{}".format(data["unique_id"])
            try:
                meeting = zoom.read_json(meeting_id)
                data["meeting_url"] = meeting["join_url"]
            except FileNotFoundError:
                print("No meeting '{}'".format(meeting_id))
                data["meeting_url"] = ""
        else:
            data["meeting_url"] = ""

        data["camera_ready"] = str(data["camera_ready"]).lower()
        data["title"] = data["title"].replace("\"", "\\\"")
        data["rocket_id"] = "baics_channel_{:02d}".format(data["unique_id"])
        data["live"] = str(data["live"]).lower()

        html = TEMPLATE.format(**data)

        path = "program/baics_{}.html".format(data["unique_id"])
        assert not os.path.exists(path)
        with open(path, "w") as fh:
            fh.write(html)


if __name__ == "__main__":
    make_jekyll_data()
    make_program()
