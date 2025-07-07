#!/bin/bash

source core
source $CLOUDINIT

os_version=$1

airgap_media ${os_version}

