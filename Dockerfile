# ---- Base ----
# ---- Python ----
FROM python:3 AS build
MAINTAINER "DeltaML dev@deltaml.com"
COPY requirements.txt .
# install app dependencies
RUN pip install  --user -r requirements.txt

FROM python:stretch AS release
WORKDIR /app
COPY --from=build /root/.local /root/.local
ADD /commons /app/commons
ADD /data_owner /app/data_owner
ENV PATH=/root/.local/bin:$PAT
ENV ENV_PROD=1
EXPOSE 5000
CMD [ "gunicorn", "-b", "0.0.0.0:5000", "wsgi:app", "--chdir", "data_owner/", "--preload"]
