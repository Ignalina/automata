#!/bin/bash
os_version=$1
hostname_name=$2
config_file=$3
inject_script=$4

source $config_file

export target_ip=${target_host[${host_name}]}

source $inject_script

