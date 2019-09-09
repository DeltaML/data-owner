# ---- Base ----
# ---- Python ----
FROM python:3 AS build
MAINTAINER "DeltaML dev@deltaml.com"
COPY requirements.txt .
# install app dependencies
RUN pip install  --user -r requirements.txt

FROM nikolaik/python-nodejs AS release
WORKDIR /app

RUN npm install -g node-fetch express express-fileupload express-form-data multer body-parser form-data
COPY --from=build /root/.local /root/.local

ADD /data_owner /app/data_owner
ADD /node-server /app/node-server
ADD /scripts /app

RUN mkdir -p /app/db

ENV PATH=/root/.local/bin:$PATH
ENV ENV_PROD=1
#
EXPOSE 5000
EXPOSE 4000
RUN chmod +x run.sh
CMD ["/bin/bash", "run.sh"]
