#!/usr/bin/env bash
kill -9 $(ps aux | grep celery | awk '{print $2}')
invoke-rc.d rabbitmq-server restart
