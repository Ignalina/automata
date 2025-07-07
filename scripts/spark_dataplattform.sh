#rm -rf ~/vms/virsh/images
#rm -rf ~/vms/virsh/xml
#rm -rf ~/vms/virsh/init

#os_version=ubi_9_5
os_version=ubuntu_24_04


./kvm_nuke_all.sh ${os_version}
./airgap_media.sh ${os_version}


./iso_create.sh ${os_version} 3 spark x14.se
./kvm_initiate.sh ${os_version} 3 spark x14.se
./kvm_cluster.sh ${os_version} 3 spark x14.se

