FROM python:3.6-stretch

RUN apt-get update && apt-get install -y ffmpeg

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /usr/src/app

# Entrypoint sets our environment correctly
ENTRYPOINT [ "/usr/src/app/entrypoint.sh" ]

# The default command is to start a uWSGI server
CMD ["uwsgi", "--ini", "/usr/src/app/uwsgi.ini"]

# EXPOSE port 8000 to allow communication to/from server
EXPOSE 8000
