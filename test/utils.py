import csv
import json


def csv_to_json(path):
  with open(path, 'r') as f:
    return list(csv.DictReader(f))
