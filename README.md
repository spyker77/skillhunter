[![Build Status](https://travis-ci.com/spyker77/skillhunter.svg?branch=main)](https://travis-ci.com/spyker77/skillhunter)
[![codecov](https://codecov.io/gh/spyker77/skillhunter/branch/main/graph/badge.svg)](https://codecov.io/gh/spyker77/skillhunter)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/dd29d17237e14749a0c502e6820bdb75)](https://www.codacy.com/manual/spyker77/skillhunter)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

# SkillHunter

SkillHunter is all about helping you and your mates identify the most in-demand skills in the job market in order to find a new position as soon as possible. Cut the bullshit and prepare yourself in the most efficient way, no need to learn everything!

What if you asked yourself the wrong question: "What do I need to learn?" Whereas a better one could be: "What I don't need to learn?" The latter helps you save a ton of time by avoiding unnecessary work when time is the most valuable – at the very beginning of unknown – that's where the SkillHunter really shines.

## Installation

Download this project and run [Docker Compose](https://docs.docker.com/compose/install/) on your machine:

```bash
git clone https://github.com/spyker77/skillhunter.git
```

## Usage

Update environment variables inside docker-compose.yml and run the following bash command inside downloaded project's folder – that will launch the process of building the image (if it doesn't exist), create and start containers in detached mode.

**Note** ⚠️ 

Due to forced HTTPS in production, it might be a good idea to use "ENVIRONMENT=development" first – this will allow you to avoid SSL related errors in the local browser.

```bash
docker-compose up -d
```

On the first run you may also need to apply migrations to the fresh database:
```bash
docker-compose exec web python manage.py migrate
```

In order to run tests, try this:
```bash
docker-compose exec web pytest --cov --cov-report=term-missing
```

**Tada** 🎉

By now you should be up and running. Try to reach the http://localhost:8000 in your browser. Note that in order to see the work in full color, you need to fill the database once...
```bash
docker-compose exec web python manage.py scrape_hh
docker-compose exec web python manage.py scrape_indeed
docker-compose exec web python manage.py scrape_sh
```
... or periodically using **cron** and additionally cleaning the database from outdated records:
```bash
docker-compose exec web python manage.py purge_db
```

## Tech Stack
-  Docker
-  Python
-  Django
-  PostgreSQL
-  Redis
-  Tailwind CSS
-  Jinja
-  Beautiful Soup
-  aiohttp
-  Pytest
-  Travis CI

## Contributing
Pull requests are really welcome. For major changes, please open an issue first to discuss what you would like to change.

Also, make sure to update tests as appropriate 🙏

## License
This project is licensed under the terms of the [MIT](https://github.com/spyker77/skillhunter/blob/main/LICENSE) license.