# Build stage
FROM python:3.11 AS build

# Fetch uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

# Fetch necessary binaries
RUN curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
RUN wget -O /usr/local/bin/hdarctl https://gitlab.eclipse.org/eclipse-research-labs/nephele-project/nephele-development-sandbox/-/raw/main/tools/hdarctl \
    && chmod +x /usr/local/bin/hdarctl

# Install dependencies and then the SMO project
WORKDIR /app
COPY pyproject.toml uv.lock /app/
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-install-project --no-dev
COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev


# Final image
FROM python:3.11-slim
RUN adduser python
USER python

COPY --from=build --chown=python:python /app /app
COPY --from=build /usr/local/bin/helm /usr/local/bin/helm
COPY --from=build /usr/local/bin/hdarctl /usr/local/bin/hdarctl

WORKDIR /app/src

ENV PATH="/app/.venv/bin:$PATH"

ENV FLASK_RUN_PORT=8000
EXPOSE 8000

CMD ["flask", "run", "--host", "0.0.0.0", "--debug"]
