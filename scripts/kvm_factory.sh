#!/bin/bash

# CREDITS! Parts of this script are directly copied & inspired from from Earl C. Ruby III https://github.com/earlruby/create-vm


VM_IMAGE_DIR=${VM_IMAGE_DIR:-"${HOME}/vms/virsh"}

declare -A imagefile
imagefile[ubuntu_22_04]=${VM_IMAGE_DIR}/base/ubuntu22.04/jammy-server-cloudimg-amd64.img
imagefile[ubuntu_24_10]=${VM_IMAGE_DIR}/base/ubuntu24.10/oracular-server-cloudimg-amd64.img
imagefile[rocky_9_4]=${VM_IMAGE_DIR}/base/rocky9.4/Rocky-9-GenericCloud.latest.x86_64.qcow2
imagefile[rocky_9_5]=${VM_IMAGE_DIR}/base/rocky9.5/Rocky-9-GenericCloud.latest.x86_64.qcow2
imagefile[fedora_40]=${VM_IMAGE_DIR}/base/fedora40/Fedora-Cloud-Base-Generic.x86_64-40-1.14.qcow2
imagefile[fedora_41]=${VM_IMAGE_DIR}/base/fedora41/Fedora-Cloud-Base-Generic-41-1.4.x86_64.qcow2

declare -A operator_groups
operator_groups[ubuntu_22_04]=sudo
operator_groups[rocky_9_4]=users,wheel,adm,systemd-journal
operator_groups[rocky_9_4]=operator_groups[rocky_9_4]

operator_groups[fedora_40]=users,wheel,adm,systemd-journal
operator_groups[fedora_41]=operator_groups[fedora_40]


declare -A post_command
post_command[ubuntu_22_04]="echo  nop"
post_command[rocky_9_4]="setenforce 0"
post_command[rocky_9_5]=post_command[rocky_9_4]
post_command[fedora_40]="setenforce 0"
post_command[fedora_40]=post_command[fedora_41]


function nuke_all_vm {

virsh list --all --name | xargs -r -I % sh -c 'virsh shutdown %'
sleep 30
virsh list --state-shutoff --name | xargs -r  -I % sh -c 'virsh undefine --domain % --remove-all-storage --managed-save'
sleep 10
virsh list --all --name | xargs -r -I % sh -c 'virsh destroy %'
virsh list --all --name | xargs -r -I % sh -c 'virsh undefine --domain % --remove-all-storage --managed-save'

}

function load_img_cache {
 mkdir -p ~/vms/virsh/base
 pushd ~/vms/virsh/base
 mkdir -p ubuntu22.04;pushd ubuntu22.04;wget -N http://cloud-images.ubuntu.com/jammy/current/jammy-server-cloudimg-amd64.img; popd
 mkdir -p ubuntu24.10;pushd ubuntu24.10;wget -N http://cloud-images.ubuntu.com/oracular/current/oracular-server-cloudimg-amd64.img; popd
 
 mkdir -p rocky9.4;pushd rocky9.4; wget -N https://download.rockylinux.org/pub/rocky/9.4/images/x86_64/Rocky-9-GenericCloud.latest.x86_64.qcow2 ; popd
 mkdir -p rocky9.5;pushd rocky9.5; wget -N https://download.rockylinux.org/pub/rocky/9.5/images/x86_64/Rocky-9-GenericCloud.latest.x86_64.qcow2 ; popd

 mkdir -p rocky40; pushd 40;wget -N https://download.fedoraproject.org/pub/fedora/linux/releases/40/Cloud/x86_64/images/Fedora-Cloud-Base-Generic.x86_64-40-1.14.qcow2;popd
 mkdir -p rocky41; pushd 41;wget -N https://mirror.accum.se/mirror/fedora/linux/releases/41/Cloud/x86_64/images/Fedora-Cloud-Base-Generic-41-1.4.x86_64.qcow2;popd

 popd
}

function get_vm_ip {
 MAC=$(virsh domiflist $HOSTNAME | awk '{ print $5 }' | tail -2 | head -1)
 arp -a | grep $MAC | awk '{ print $2 }' | sed 's/[()]//g'
}

function beginswith() { case $2 in "$1"*) true;; *) false;; esac; }


function create_node {
 osversion=$1
 HOSTNAME=$2
 RAM=6144
 VCPUS=4
 IMG_FQN=${imagefile[$osversion]}
 STORAGE=80
 BRIDGE=virbr0


 echo "proceding startup vm:s "
 echo "OS=$osversion"
 echo "CLOUD IMAGE FILE=${IMG_FQN}"


 mkdir -p "$VM_IMAGE_DIR"/{images,xml,init,base}

 echo "Creating a qcow2 image file ${VM_IMAGE_DIR}/images/${HOSTNAME}.img that uses the cloud image file ${IMG_FQN} as its base"
 qemu-img create -b "${IMG_FQN}" -f qcow2 -F qcow2 "${VM_IMAGE_DIR}/images/${HOSTNAME}.img" "${STORAGE}G"

 echo "Creating meta-data file $VM_IMAGE_DIR/init/meta-data"
 cat > "$VM_IMAGE_DIR/init/meta-data" << EOF
instance-id: ${HOSTNAME}
local-hostname: ${HOSTNAME}
EOF

 echo "Creating user-data file $VM_IMAGE_DIR/init/user-data"
 cat > "$VM_IMAGE_DIR/init/user-data" << EOF
#cloud-config

users:
  - default
  - name: ansible
    selinux-user: staff_u
    sudo: ["ALL=(ALL) NOPASSWD:ALL"]
    groups: ${operator_groups[$osversion]}
    shell: /bin/bash
    homedir: /var/ansible
    ssh_pwauth: True
    ssh_authorized_keys:
EOF

 key=$(< ~/.ssh/id_rsa.pub)
 echo "     -" $key >> $VM_IMAGE_DIR/init/user-data 
# echo "Adding keys from the public key file $AUTH_KEYS_FQN to the user-data file"
# while IFS= read -r key; do
#     echo "      - $key" >> "$VM_IMAGE_DIR/init/user-data"
# done < <(grep -v '^ *#' < "$AUTH_KEYS_FQN")

 cat >> "$VM_IMAGE_DIR/init/user-data" << EOF
chpasswd:
  list: |
    root:password
    ansible:ansible
  expire: False
ssh_pwauth: True
runcmd:
- ${post_command[$osversion]}
EOF





 echo "Generating the cidata ISO file $VM_IMAGE_DIR/images/${HOSTNAME}-cidata.iso"
(
    cd "$VM_IMAGE_DIR/init/"
    genisoimage \
        -output "$VM_IMAGE_DIR/images/${HOSTNAME}-cidata.img" \
        -volid cidata \
        -rational-rock \
        -joliet \
        user-data meta-data
)

 MACCMD=
 if [[ -n $MAC ]]; then
     MACCMD="--mac=${MAC}"
 fi


 virt-install \
    --name="${HOSTNAME}" \
    --network "bridge=${BRIDGE},model=virtio" $MACCMD \
    --import \
    --disk "path=${VM_IMAGE_DIR}/images/${HOSTNAME}.img,format=qcow2" \
    --disk "path=$VM_IMAGE_DIR/images/${HOSTNAME}-cidata.img,device=cdrom" \
    --ram="${RAM}" \
    --vcpus="${VCPUS}" \
    --autostart \
    --hvm \
    --arch x86_64 \
    --accelerate \
    --check-cpu \
    --osinfo detect=on,require=off \
    --force \
    --watchdog=default \
    --graphics vnc,listen=0.0.0.0 \
    --noautoconsole \
    --debug

# Make a backup of the VM's XML definition file
virsh dumpxml "${HOSTNAME}" > "${VM_IMAGE_DIR}/xml/${HOSTNAME}.xml"

}



os_version=$1
host_name=$2
config_file=$3
inject_script=$4

source $config_file

nuke_all_vm
load_img_cache
#while wait -n; do : ; done;

virsh list --all

create_node $os_version $host_name
virsh list --all

echo "wait until network setup ready AND ssh server up for ${target_ip} "
while ! [[ $(get_vm_ip ${host_name}) ]]; do  sleep 1; done ;
export target_ip=$(get_vm_ip ${host_name})

while ! ssh -o StrictHostKeyChecking=no ansible@$target_ip 'sleep 5'; do  sleep 5; done ;


source $inject_script;


#create-vm/delete-vm node1
#nuke_all_vm
