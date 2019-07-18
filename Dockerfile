#################################################
# BUILD
#################################################

FROM node:10

RUN mkdir -p /usr/src/build
WORKDIR /usr/src/build
COPY rateapp /usr/src/build

RUN npm install && npm run build


#################################################
# SERVICE
#################################################

FROM python:3.6-stretch

RUN apt-get update && apt-get install -y ffmpeg

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

# Python dependencies
COPY harvester/requirements.txt /usr/src/app/
RUN pip install --no-cache-dir -r requirements.txt

# Frontend application
COPY harvester /usr/src/app
COPY --from=0 /usr/src/build/dist /usr/src/app/search/static

# Entrypoint sets our environment correctly
ENTRYPOINT [ "/usr/src/app/entrypoint.sh" ]

# The default command is to start a uWSGI server
CMD ["uwsgi", "--ini", "/usr/src/app/uwsgi.ini"]

# EXPOSE port 8000 to allow communication to/from server
EXPOSE 8000
