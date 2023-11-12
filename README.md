# SkillHunter

[![CI/CD](https://github.com/spyker77/skillhunter/actions/workflows/main.yml/badge.svg?branch=main)](https://github.com/spyker77/skillhunter/actions/workflows/main.yml)
[![Codecov](https://codecov.io/gh/spyker77/skillhunter/graph/badge.svg?token=BBTT6UO39V)](https://codecov.io/gh/spyker77/skillhunter)
[![Codacy](https://app.codacy.com/project/badge/Grade/111702284f88482bbc4b64d2b6d169c5)](https://app.codacy.com/gh/spyker77/skillhunter/dashboard)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-2.0-4baaaa.svg)](CODE_OF_CONDUCT.md)

SkillHunter is all about helping you and your mates identify the most in-demand skills in the job market in order to find a new position as soon as possible. Cut the bullshit and prepare yourself in the most efficient way, no need to learn everything!

What if you asked yourself the wrong question: "What do I need to learn?" Whereas a better one could be: "What I don't need to learn?" The latter helps you save a ton of time by avoiding unnecessary work when time is the most valuable – at the very beginning of unknown – that's where the SkillHunter really shines.

## Installation

Download this project and run [Docker Compose](https://docs.docker.com/compose/install/) on your machine:

```bash
git clone https://github.com/spyker77/skillhunter.git
cd skillhunter
```

## Usage

Update environment variables inside the docker-compose.yml and run the following bash commands inside downloaded project's folder – this will launch the process of building the image (if it doesn't exist), create and start containers in a detached mode.

1. Due to a forced HTTPS in production, it might be a good idea to start with **ENVIRONMENT=development** in .env file – this will allow you to avoid SSL related errors.

```bash
docker compose up -d
```

2. On the first run you need to apply migrations to the fresh database:

```bash
docker compose exec web python manage.py migrate
```

3. Load the job titles to parse and skills to identify:

```bash
docker compose exec web python manage.py loaddata jobs.json skills.json
```

4. [Optional] Run scrapers to collect initial data on available vacancies:

```bash
docker compose exec worker python manage.py scrape_hh
docker compose exec worker python manage.py scrape_indeed
docker compose exec worker python manage.py scrape_sh
```

...or run scrapers periodically using **cron** and additionally cleaning the database from outdated records:

```bash
docker compose exec web python manage.py purge_db
```

**Tada** 🎉

By now you should be up and running. Try to reach the <http://localhost> in your browser.

In order to prepopulate the database, you can use the test data:

```bash
docker compose exec web python manage.py loaddata scrapers_vacancy.json scrapers_vacancy_part_1.json scrapers_vacancy_part_2.json scrapers_vacancy_part_3.json
```

In order to run tests:

```bash
docker compose exec -e DB_HOST=db web pytest -n auto --cov="."
```

**Note** ⚠️

For the local development you may need to install **poppler** (e.g. using `brew install poppler`) for the **pdftotext** package, and **pg_config** for the **psycopg** (e.g. using `brew install postgresql`).

## Architecture

![SkillHunter's architecture](https://spyker77.notion.site/image/https%3A%2F%2Fs3-us-west-2.amazonaws.com%2Fsecure.notion-static.com%2F24293db7-cf4b-46ca-8a44-e9ac458107f9%2FArchitecture.png?table=block&id=de70516a-c572-4324-8f80-c40b97118997&spaceId=d8f7323e-790b-48e9-8264-b0e2573a22ac&width=2000&userId=&cache=v2)

## Contributing

Pull requests are really welcome. For major changes, please open an issue first to discuss what you would like to change.

Also, make sure to update tests as appropriate 🙏

## License

This project is licensed under the terms of the [MIT](https://github.com/spyker77/skillhunter/blob/main/LICENSE) license.
