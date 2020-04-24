import pandas as pd
import os
import json


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


def meeting_json_exists(name):
    path = os.path.join("scripts/data/meetings", "{}.json".format(name))
    return os.path.exists(path)


def save_meeting_json(name, data):
    path = os.path.join("scripts/data/meetings", "{}.json".format(name))
    if not os.path.exists("scripts/data/meetings"):
        os.makedirs("scripts/data/meetings")
    with open(path, "w") as fh:
        json.dump(data, fh)


def read_meeting_json(name):
    path = os.path.join("scripts/data/meetings", "{}.json".format(name))
    with open(path, "r") as fh:
        return json.load(fh)

