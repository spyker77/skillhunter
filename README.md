# SkillHunter

[![Build Status](https://app.travis-ci.com/spyker77/skillhunter.svg?branch=main)](https://app.travis-ci.com/github/spyker77/skillhunter)
[![codecov](https://codecov.io/gh/spyker77/skillhunter/branch/main/graph/badge.svg?token=BBTT6UO39V)](https://codecov.io/gh/spyker77/skillhunter)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/111702284f88482bbc4b64d2b6d169c5)](https://www.codacy.com/gh/spyker77/skillhunter/dashboard)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-2.0-4baaaa.svg)](CODE_OF_CONDUCT.md)

SkillHunter is all about helping you and your mates identify the most in-demand skills in the job market in order to find a new position as soon as possible. Cut the bullshit and prepare yourself in the most efficient way, no need to learn everything!

What if you asked yourself the wrong question: "What do I need to learn?" Whereas a better one could be: "What I don't need to learn?" The latter helps you save a ton of time by avoiding unnecessary work when time is the most valuable – at the very beginning of unknown – that's where the SkillHunter really shines.

## Installation

Download this project and run [Docker Compose](https://docs.docker.com/compose/install/) on your machine:

```bash
git clone https://github.com/spyker77/skillhunter.git
```

## Usage

Update environment variables inside the docker-compose.yml and run the following bash commands inside downloaded project's folder – this will launch the process of building the image (if it doesn't exist), create and start containers in a detached mode.

**Note** ⚠️

Due to a forced HTTPS in production, it might be a good idea to start with **ENVIRONMENT=development** in .env file – this will allow you to avoid SSL related errors.

```bash
docker compose up -d
```

On the first run you need to apply migrations to the fresh database:

```bash
docker compose exec -u root web python manage.py migrate
```

Note that in order to see the work in full color, you also need to fill the database once by loading the list of job titles to parse and skills to identify...

```bash
docker compose exec web python manage.py loaddata jobs.json
docker compose exec web python manage.py loaddata skills.json
```

...and run scrapers to collect initial data on available vacancies...

```bash
docker compose exec web python manage.py scrape_hh
docker compose exec web python manage.py scrape_indeed
docker compose exec web python manage.py scrape_sh
```

...or run scrapers periodically using **cron** and additionally cleaning the database from outdated records:

```bash
docker compose exec web python manage.py purge_db
```

**Tada** 🎉

By now you should be up and running. Try to reach the <http://localhost> in your browser. In order to run tests, try this:

```bash
docker compose exec web pytest -n auto --cov="." --cov-report=term-missing
```

## Tech Stack

- Python
- Docker
- Django
- Django REST framework
- Swagger UI
- FastAPI
- PostgreSQL
- Redis
- NGINX
- Tailwind CSS
- Jinja
- Beautiful Soup
- Selenium WebDriver
- AIOHTTP
- Pytest
- Travis CI
- AWS

## Contributing

Pull requests are really welcome. For major changes, please open an issue first to discuss what you would like to change.

Also, make sure to update tests as appropriate 🙏

## License

This project is licensed under the terms of the [MIT](https://github.com/spyker77/skillhunter/blob/main/LICENSE) license.
