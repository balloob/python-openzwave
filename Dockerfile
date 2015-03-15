FROM buildpack-deps:jessie
MAINTAINER Paulus Schoutsen <Paulus@PaulusSchoutsen.nl>

# First install command is common packages, 2nd is Python 2 specific.
RUN apt-get update && \
    apt-get install -y libudev-dev cython3 && \
    apt-get install -y python-dev python-pip && \
    pip install cython && \
    apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

CMD [ "/bin/bash" ]
