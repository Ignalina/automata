os_version=ubi_9_6
#os_version=ubuntu_22_04
export CLOUDINIT="cloudinit"
export PUBLIC_KEY=$(< ~/.ssh/id_ed25519.pub)
export VM_IMAGE_DIR="~/automata/virsh"


./kvm_nuke_all.sh ${os_version}
./airgap_media.sh ${os_version}

./iso_create.sh ${os_version} 1 3 spark x14.se
./kvm_initiate.sh ${os_version} 1 3 spark x14.se
./kvm_cluster.sh ${os_version} 1 3 spark x14.se

