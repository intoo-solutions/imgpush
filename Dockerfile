FROM python:3.12.3-slim

RUN apt-get update && \
    apt-get install -y \
    libmagickwand-dev curl \
    nginx && \
    mkdir /files /cache

COPY requirements.txt .
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY ImageMagick-6/policy.xml /etc/ImageMagick-6/policy.xml

COPY app /app

RUN pip install -r requirements.txt && \
    rm -f /app/imgpush.sock

EXPOSE 5000

WORKDIR /app

CMD bash entrypoint.sh
