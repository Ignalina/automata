#!/bin/bash

source core


os_version=$1
machines=$2
host_name=$3
bmcs=$4

all=( ${@} )
IFS=','
bmcs="${all[*]:4}"
bmcs=(${bmcs}) 

 
for (( i=1; i<=${machines}; ++i)); do
    create_redfish_node_image $os_version ${node_name}${i}.${domain_name} ${bmcs[i-1]}
done


