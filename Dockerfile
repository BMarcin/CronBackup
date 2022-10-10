FROM python:3.10

# install cron
RUN apt-get update && apt-get install -y cron

# run main.py every minute
RUN echo "* * * * * poetry run python /app/main.py" > /etc/cron.d/main-cron
RUN chmod 0644 /etc/cron.d/main-cron

# crontab install
RUN crontab /etc/cron.d/main-cron

# install poetry
RUN pip install -U pip setuptools
RUN pip install -U poetry

# copy lib files
WORKDIR /app
COPY poetry.lock pyproject.toml ./

# install dependencies
RUN poetry install --no-dev

# copy project files
COPY . .
CMD ["cron", "-f", "-l", "2"]
