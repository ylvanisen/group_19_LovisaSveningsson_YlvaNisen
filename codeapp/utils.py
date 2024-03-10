# built-in imports
# standard library imports
import csv
import pickle
import uuid
from datetime import datetime

import requests

# external imports
from flask import current_app

# internal imports
from codeapp import db
from codeapp.models import Movies


def get_data_list() -> list[Movies]:
    if db.exists("dataset_list") > 0:
        current_app.logger.info("Dataset already downloaded.")
        dataset_stored: list[Movies] = []
        raw_dataset: list[bytes] = db.lrange("dataset_list", 0, -1)
        for item in raw_dataset:
            dataset_stored.append(pickle.loads(item))
        return dataset_stored

    url = "https://onu1.s2.chalmers.se/datasets/tmdb_5000_movies.csv"
    response = requests.get(url, timeout=20)
    with open("movies.csv", "wb") as file:
        file.write(response.content)
    print("Download success")

    with open("movies.csv", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        data: list[dict[str, str]] = list(reader)
        dataset_base: list[Movies] = []
        for row in data:
            movies = Movies(
                id=uuid.uuid4().hex,
                title=row["title"],
                genres=row["genres"],
                runtime=row["runtime"],
                release_date=row["release_date"],
                budget=row["budget"],
                score=row["score"],
            )
            db.rpush("dataset_list", pickle.dumps(movies))
            dataset_base.append(movies)

    return dataset_base


def calculate_statistics(dataset: list[Movies]) -> dict[int | str, float]:

    """
    Receives the dataset in the form of a list of Python objects, and calculates the
    statistics necessary.
    """
    years: dict[str, float] = {}

    for i in dataset:
        if "Science Fiction" in i.genres:
            release_date = datetime.strptime(i.release_date, "%Y-%m-%d")
            years.setdefault(release_date, []).append(float(i.score))

    score_average = {}

    for key, values in years.items():
        key_sum = sum(values)
        score_average[key.year] = key_sum / len(values)

    return score_average


def prepare_figure(input_figure: str) -> str:
    """
    Method that removes limits to the width and height of the figure. This method must
    not be changed by the students.
    """
    output_figure = input_figure.replace('height="345.6pt"', "").replace(
        'width="460.8pt"', 'width="100%"'
    )
    return output_figure
