#!/usr/bin/env sh

tensorboard --logdir=${EVENTS_DIR} --host 0.0.0.0
