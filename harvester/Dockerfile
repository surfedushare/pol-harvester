FROM python:3.6-onbuild

RUN apt-get install ffmpeg

# Entrypoint sets our environment correctly
ENTRYPOINT [ "/usr/src/app/entrypoint.sh" ]

# The default command is to start a uWSGI server
CMD ["uwsgi", "--ini", "/usr/src/app/uwsgi.ini"]

# EXPOSE port 8000 to allow communication to/from server
EXPOSE 8000
