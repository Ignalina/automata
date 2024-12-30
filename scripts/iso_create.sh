#!/bin/bash

source core


os_version=$1
machines=$2

node_name=$3
domain_name=$4



for (( i=1; i<${machines}; ++i)); do
    create_kvm_node_iso $os_version ${node_name}${i}.${domain_name}
done
