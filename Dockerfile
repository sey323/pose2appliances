FROM python:3.8

RUN apt-get update -y && apt-get install -y libopencv-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY ./src /src

ENV API_KEY sample_key

ENTRYPOINT ["/bin/sh", "-c", "python src/main.py ${API_KEY}"]