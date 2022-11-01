FROM python:3.10

# install pg_dump
#RUN sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt/ `lsb_release -cs`-pgdg main" >> /etc/apt/sources.list.d/pgdg.list'
#RUN wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -
RUN echo "deb http://apt.postgresql.org/pub/repos/apt/ bullseye-pgdg main" > /etc/apt/sources.list.d/pgdg.list \
  && curl -sSL https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -
RUN apt-get update && apt-get install -y postgresql-client-15

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
CMD ["poetry", "run", "python", "main.py"]
