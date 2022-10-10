FROM python:3.10
RUN pip install -U pip setuptools
RUN pip install -U poetry

WORKDIR /app
COPY poetry.lock ./
RUN poetry install --no-dev

COPY . .
CMD ["poetry", "run", "python", "main.py"]
