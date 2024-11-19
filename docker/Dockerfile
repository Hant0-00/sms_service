FROM python:3.10
WORKDIR /app/

RUN apt-get update && \
    apt-get install -y \
    wget \
    ca-certificates \
    fonts-noto \
    libxss1 \
    libappindicator3-1 \
    fonts-liberation \
    xdg-utils \
    gnupg \
    xvfb


RUN DEBIAN_FRONTEND=noninteractive && \
    wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub > /usr/share/keyrings/chrome.pub && \
    echo 'deb [arch=amd64 signed-by=/usr/share/keyrings/chrome.pub] http://dl.google.com/linux/chrome/deb/ stable main' > /etc/apt/sources.list.d/google-chrome.list && \
    apt update -y && \
    apt install -y google-chrome-stable

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


COPY ../requirements.txt /app/requirements.txt

COPY ../ /app/

RUN pip install --no-cache-dir -r requirements.txt
RUN playwright install

EXPOSE 8000

