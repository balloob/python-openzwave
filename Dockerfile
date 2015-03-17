FROM buildpack-deps:jessie
MAINTAINER Paulus Schoutsen <Paulus@PaulusSchoutsen.nl>

# First install command is common packages, Python 2, Python 3.
RUN apt-get update && \
    apt-get install -y libudev-dev cython3 && \
    apt-get install -y python-dev python-pip && \
    apt-get install -y python3-setuptools python3-pip && \
    pip install cython && \
    apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

CMD [ "/bin/bash" ]
