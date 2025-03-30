#rm -rf ~/vms/virsh/images
#rm -rf ~/vms/virsh/xml
#rm -rf ~/vms/virsh/init

os_version=ubi_9_5


#./kvm_nuke_all.sh ${os_version}
#./airgap_media.sh ${os_version}
#./iso_create.sh ${os_version} 1 spark x14.se
./redfish_initiate.sh ${os_version} 1 spark x14.se 10.1.1.204 10.1.1.205
#./kvm_cluster.sh ${os_version} 6 spark x14.se
