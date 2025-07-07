#rm -rf ~/vms/virsh/images
#rm -rf ~/vms/virsh/xml
#rm -rf ~/vms/virsh/init

#os_version=ubi_9_5
os_version=ubuntu_24_04
export CLOUDINIT="cloudinit25"
export PUBLIC_KEY=$(< ~/.ssh/id_ed25519.pub)
export VM_IMAGE_DIR="/mnt/md0/vms/virsh"


./kvm_nuke_all.sh ${os_version}
./airgap_media.sh ${os_version}


./iso_create.sh ${os_version} 3 spark x14.se
./kvm_initiate.sh ${os_version} 3 spark x14.se
./kvm_cluster.sh ${os_version} 3 spark x14.se

