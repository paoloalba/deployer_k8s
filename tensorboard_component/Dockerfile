FROM python:3.8-slim
# FROM tensorflow/tensorflow:latest-gpu

RUN pip install tensorboard

COPY run.sh run.sh

RUN chmod +x ./run.sh

ENTRYPOINT ["./run.sh"]