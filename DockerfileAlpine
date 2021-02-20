FROM python:3.9.1-alpine
# Update & Install dependencies
RUN apk add --no-cache --update \
    openssl \
    ca-certificates \
    bzip2-dev \
    zlib-dev \
    readline-dev \
    build-base \
    linux-headers \
    gcc \
    libgcc \
    cmake \
    hdf5 \
    hdf5-dev
RUN python -m pip install --upgrade pip
COPY ./requirements.txt requirements.txt
RUN python -m pip install -r requirements.txt
WORKDIR app
COPY idea idea
# Expose the Dask port
EXPOSE 8050
ENTRYPOINT [ "python", "-m", "idea.app.main"]
