#!/bin/bash

python3 /home/app/tests/functional/utils/wait_for_auth.py \
  && python3 /home/app/tests/functional/utils/wait_for_redis.py
pytest .