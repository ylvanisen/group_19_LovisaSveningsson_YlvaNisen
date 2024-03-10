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
    if response.status_code == 200:
        with open("movies.csv", "wb") as file:
            file.write(response.content)
        print("Download success")
    else:
        pass

    with open("movies.csv", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        data: list[dict[str, str]] = list(reader)
        dataset_base: list[Movies] = []
        for row in data:
            try:
                runtime = int(row["runtime"])
                score = float(row["score"])
            except ValueError:
                print(f"Invalid score: {row['score']}. Skipping movie {row['title']}.")
                continue
            movies = Movies(
                id=int(uuid.uuid4().hex, 16),
                title=row["title"],
                genres=row["genres"].split(","),
                runtime=runtime,
                release_date=datetime.strptime(row["release_date"], "%Y-%m-%d"),
                budget=int(row["budget"]),
                score=score,
            )

            db.rpush("dataset_list", pickle.dumps(movies))
            dataset_base.append(movies)

    return dataset_base


def calculate_statistics(dataset: list[Movies]) -> dict[int | str, float]:
    years: dict[datetime, list[float]] = {}

    for i in dataset:
        if "Science Fiction" in i.genres:
            release_date = i.release_date
            release_datetime = datetime.combine(release_date, datetime.min.time())
            years.setdefault(release_datetime, []).append(float(i.score))

    score_average: dict[int | str, float] = {}

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
