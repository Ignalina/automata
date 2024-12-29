#!/bin/bash

source core


os_version=$1
machines=$2
host_name=$3

config_file=$4
inject_script=$5



for (( i=1; i<${machines}; ++i)); do
    install_node_image $os_version machine${i}.${host_name} &
done


