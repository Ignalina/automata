#!/bin/bash

source core


os_version=$1
machines=$2
host_name=$3
bmcs=$4



for (( i=1; i<${machines}; ++i)); do
    create_redfish_node_image $os_version machine${i}.${host_name} ${bmcs}
done


