# use simple kernel recipes instead of linux-yocto
PREFERRED_PROVIDER_virtual/kernel = "linux-k510"
PREFERRED_PROVIDER_linux-libc-headers = "linux-libc-headers-k510"
PREFERRED_PROVIDER_nativesdk-linux-libc-headers = "nativesdk-linux-libc-headers-k510"
PREFERRED_PROVIDER_virtual/crypt ?= "glibc"
PREFERRED_PROVIDER_virtual/nativesdk-crypt ?= "nativesdk-glibc"
