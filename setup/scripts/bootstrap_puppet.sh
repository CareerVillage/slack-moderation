#!/bin/bash

if [ ! -e /tmp/puppet-updated ]; then
  wget -O /tmp/puppetlabs-release-trusty.deb http://apt.puppetlabs.com/puppetlabs-release-trusty.deb
  dpkg -i /tmp/puppetlabs-release-trusty.deb
  apt-get update
  apt-get --assume-yes install puppet
  touch /tmp/puppet-updated
fi

export FACTER_moderation_secret_key="3$6=m!!*ow9r4z4ci#s)k^4pcb+@*2t@i$m(_%0)0bm7k&z33+"