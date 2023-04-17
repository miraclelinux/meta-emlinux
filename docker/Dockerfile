FROM debian:bullseye

ARG uid
ARG http_proxy
ARG https_proxy
ARG no_proxy

RUN apt-get update --fix-missing && apt-get -y upgrade --fix-missing

RUN apt-get install --fix-missing -y \
  binfmt-support \
  debootstrap \
  dosfstools \
  dpkg-dev \
  gettext-base \
  git \
  mtools \
  parted \
  python3 \
  quilt \
  qemu \
  qemu-system-x86 \
  qemu-system-arm \
  qemu-user-static \
  seabios \
  reprepro \
  sudo \
  git-buildpackage \
  pristine-tar \
  sbuild \
  schroot \
  zstd \
  python3-distutils \
  python3-yaml \
  python3-html5lib \
  vim \
  screen \
  socat \
  patchelf

RUN useradd -m build -u $uid
RUN gpasswd -a build sbuild
RUN apt-get install -y sudo
RUN echo "build ALL=(ALL) NOPASSWD: ALL" | tee -a /etc/sudoers
RUN echo  "Defaults env_keep += \" http_proxy https_proxy no_proxy\"" | tee -a /etc/sudoers

# Fix error "Please use a locale setting which supports utf-8."
# See https://wiki.yoctoproject.org/wiki/TipsAndTricks/ResolvingLocaleIssues
RUN apt-get install -y locales
RUN sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && \
        echo 'LANG="en_US.UTF-8"'>/etc/default/locale && \
        dpkg-reconfigure --frontend=noninteractive locales && \
        update-locale LANG=en_US.UTF-8

ENV LC_ALL en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US.UTF-8

ADD gitproxy /usr/bin
RUN chmod +x /usr/bin/gitproxy
RUN bash -c 'if test -n "$http_proxy"; then sed -i -e "s#\(http_proxy=\"\).*#\1$http_proxy\"#" /usr/bin/gitproxy; fi'

USER build
WORKDIR /home/build

RUN bash -c 'if test -n "$http_proxy"; then git config --global http.proxy "$http_proxy"; \
                                            git config --global core.gitproxy gitproxy; fi'
RUN bash -c 'if test -n "$https_proxy"; then git config --global https.proxy "$https_proxy"; fi'
RUN bash -c 'if test -n "$no_proxy"; then git config --global core.noproxy "$no_proxy"; fi'

RUN mkdir work
WORKDIR /home/build/work

CMD "/bin/bash"

