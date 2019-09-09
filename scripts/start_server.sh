#!/usr/bin/env bash
gunicorn -b 0.0.0.0:5000 -b 0.0.0.0:5555 wsgi:app --chdir data_owner/ --preload