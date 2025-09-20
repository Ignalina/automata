#!/bin/bash

source core
source $CLOUDINIT

os_version=$1
start=$2
machines=$3

node_name=$4
domain_name=$5


for (( i=${start}; i<=${machines}; ++i)); do
    create_kvm_node_image $os_version ${node_name}${i}.${domain_name}
done
