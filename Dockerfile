FROM python:3.13-slim@sha256:751d8bece269ba9e672b3f2226050e7e6fb3f3da3408b5dcb5d415a054fcb061

# Define Git SHA build argument for Sentry
ARG git_sha="development"
ENV GIT_SHA=$git_sha

WORKDIR /app

RUN python -m pip install --no-cache-dir -U pip setuptools wheel
RUN python -m pip install --no-cache-dir pdm

COPY pyproject.toml pdm.lock ./
RUN pdm export --prod -o requirements.txt && python -m pip install --no-cache-dir -r requirements.txt

COPY src/ src/
RUN python -m pip install --no-cache-dir .

RUN useradd --no-create-home --shell=/bin/bash loader
USER loader

CMD [ "python", "-m", "loader" ]
