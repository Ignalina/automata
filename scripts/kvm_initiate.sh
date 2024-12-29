#!/bin/bash

source core


os_version=$1
machines=$2
host_name=$3

nuke_all_vm

for (( i=1; i<${machines}; ++i)); do
    create_kvm_node_image $os_version machine${i}.${host_name}
done


