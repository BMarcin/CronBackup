FROM python:3.10

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
CMD ["python", "main.py"]
