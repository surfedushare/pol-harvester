#################################################
# BUILD
#################################################

FROM node:10 AS builder

RUN mkdir -p /usr/src/rateapp
WORKDIR /usr/src/rateapp
COPY rateapp /usr/src/rateapp

RUN npm install && npm run build


#################################################
# SERVICE
#################################################

FROM python:3.6-stretch

RUN apt-get update && apt-get install -y less vim ffmpeg \
    time dialog sox subversion build-essential zlib1g-dev automake autoconf libtool libatlas3-base
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

# Python dependencies
COPY harvester/requirements.txt /usr/src/app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY harvester /usr/src/app
RUN mkdir -p /usr/src/rateapp
COPY --from=builder /usr/src/rateapp/dist /usr/src/rateapp/dist

# Entrypoint sets our environment correctly
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]

# The default command is to start a uWSGI server
CMD ["uwsgi", "--ini", "/usr/src/app/uwsgi.ini"]

# EXPOSE port 8000 to allow communication to/from server
EXPOSE 8000
