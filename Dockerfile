FROM python:3.10-slim

ENV APP_HOME=/app

WORKDIR $APP_HOME

RUN pip install --no-cache-dir poetry

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

COPY main.py ./
COPY index.html ./templates
COPY pyproject.toml ./static

EXPOSE 8080

CMD ["python3", "main.py"]