t# base docker image that we will build on
FROM python:3.13.11-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/

# set up a working directory inside the container
WORKDIR /app

COPY pipeline/pipeline.py pipeline.py


ENV PATH="/app/.venv/bin:$PATH"
# copy the script to the container

COPY "pyproject.toml" "uv.lock" ".python-version" ./

# Install dependencies from lock file (ensures reproducible builds)
RUN uv sync --locked

# define what to do first when the container run
ENTRYPOINT ["python", "pipeline.py"]