rm -rf ~/vms/virsh/images
rm -rf ~/vms/virsh/xml
rm -rf ~/vms/virsh/init

./airgap_media.sh fedora_41
./iso_create.sh fedora_41 5 spark x14.se
./kvm_initiate.sh fedora_41 5 spark x14.se
./kvm_cluster.sh fedora_41 5 spark x14.se
