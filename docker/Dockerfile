FROM ubuntu:20.04
ENV DEBIAN_FRONTEND=noninteractive
ENV DEBCONF_NOWARNINGS yes

ARG uid
ARG http_proxy
ARG https_proxy
ARG no_proxy

RUN apt-get update --fix-missing && apt-get -y upgrade --fix-missing

RUN apt-get install --fix-missing -y \
  gawk \
  wget \
  git-core \
  diffstat \
  unzip \
  texinfo \
  gcc-multilib \
  build-essential \
  chrpath \
  socat \
  cpio \
  python2 \
  python3 \
  python3-pip \
  python3-pexpect \
  python3-debian \
  xz-utils \
  debianutils \
  iputils-ping \
  libsdl1.2-dev \
  xterm \
  tmux \
  python3-git \
  python3-jinja2 \
  libegl1-mesa \
  libssl-dev \
  libncurses-dev \
  rsync \
  sudo \
  vim \
  less \
  file \
  locales \
  iptables \
  iproute2 \
  openssh-server \
  openjdk-11-jdk-headless \
  python-is-python3 \
  python3-yaml \
  python3-html5lib \
  python3-requests

RUN useradd -s /bin/bash -m build -u $uid
RUN echo "build ALL=(ALL) NOPASSWD: ALL" | tee -a /etc/sudoers
RUN echo  "Defaults env_keep += \" http_proxy https_proxy no_proxy\"" | tee -a /etc/sudoers

RUN locale-gen en_US.UTF-8
RUN update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8

ENV LC_ALL en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US.UTF-8

ADD gitproxy /usr/bin
RUN chmod +x /usr/bin/gitproxy

USER build
WORKDIR /home/build

RUN bash -c 'if test -n "$http_proxy"; then git config --global http.proxy "$http_proxy"; \
                                            git config --global core.gitproxy "/usr/bin/gitproxy"; fi'
RUN bash -c 'if test -n "$https_proxy"; then git config --global https.proxy "$https_proxy"; fi'
RUN bash -c 'if test -n "$no_proxy"; then git config --global core.noproxy "$no_proxy"; fi'

RUN mkdir work
WORKDIR /home/build/work
