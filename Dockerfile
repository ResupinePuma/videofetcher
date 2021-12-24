FROM ubuntu:latest
WORKDIR /code
ENV DEBIAN_FRONTEND noninteractive 
ENV TZ=Europe/Moscow
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN apt-get update && apt-get install -y python3-pip ffmpeg gcc

ADD ./videofetcher /code
RUN cd /code && pip3 install -r requirements.txt

CMD ["python3", "main.py"]
