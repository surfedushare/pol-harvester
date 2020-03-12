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

# Create the app environment
RUN mkdir -p /usr/src/app
RUN mkdir -p /usr/src/rateapp
RUN mkdir -p /usr/src/logs
WORKDIR /usr/src/app
RUN groupadd -r app -g 1001 && useradd app -u 1001 -r -g app
RUN chown -R app:app /usr/local
RUN chown app:app /usr/src/app
RUN chown app:app /usr/src/rateapp
RUN chown app:app /usr/src/logs
RUN chown -R app:app /usr/local/lib/python3.6/site-packages
USER app:app

# Python dependencies
COPY harvester/requirements.txt /usr/src/app/
RUN pip install -U pip && pip install uwsgi==2.0.18
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY harvester /usr/src/app
COPY --from=builder /usr/src/rateapp/dist /usr/src/rateapp/dist

# Entrypoint sets our environment correctly
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]

# The default command is to start a uWSGI server
CMD ["uwsgi", "--ini", "/usr/src/app/uwsgi.ini"]

# EXPOSE port 8000 to allow communication to/from server
EXPOSE 8000
