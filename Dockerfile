# ---- Base ----
# ---- Python ----
FROM python:3.6 AS build
MAINTAINER "DeltaML dev@deltaml.com"
COPY requirements.txt .
# install app dependencies
RUN pip install  --user -r requirements.txt

FROM nikolaik/python-nodejs:python3.6-nodejs10 AS release
WORKDIR /app

COPY --from=build /root/.local /root/.local

ADD /data_owner /app/data_owner
ADD /node-server /app/node-server
ADAD /node-server/static /app/node-server/static/
COPY /node-server/package.json .
RUN npm install
ADD /scripts /app

RUN mkdir -p /app/db

ENV PATH=/root/.local/bin:$PATH
ENV ENV_PROD=1
#
EXPOSE 5000
EXPOSE 4000
RUN chmod +x run.sh
CMD ["/bin/bash", "run.sh"]
