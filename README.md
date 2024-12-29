<img src="https://github.com/user-attachments/assets/d1918dcb-8de1-428e-87aa-7ff05ac45ab9" width="400" height="400">

# Automata
Create and maintain airgaped clusters for distributed software

Automata does this by Generate OS iso's and fire them up on hosts (kvm or redfish)

0) airgap your target os media on an internet enabled server.
**syntax** airgap_img.sh osversion_
For example , fedora_41 os
```bash
airgap_media.sh fedora_41 
```
For a quick test continue with step nr 2 below on same server. But for production you need transfer airgaped media files to non internet enabled machines.

 A future update needs to run the below command and again transfer the packages to non internet enabled machine/s
```bash
airgap_update.sh fedora_41 
```

2) Factory your media ,One iso for each node in cluster will be created

**syntax** iso_factory.sh osversion_ nodes_ nodename_ domain_  

For example , to create 4 isos with hostnames {spark1.x14.se, spark2.x14.se, spark3.x14.se}  
```bash
iso_create.sh fedora_41 4 spark x14.se
```

2) Initate your hosts   (DISCLAIMER WARNING WILL DESTROY / FORMAT / DELETE your hosts)  
**syntax** [kvm/redfish]_initate.sh  osversion_ nodes_ nodename_ domain_  

using local kvm  
```bash
kvm_initiate.sh fedora_41 4 spark x14.se
```
or redfish  where you must set ip1...ip4 to your hardwares BMC.  
```bash
redfish_initiate.sh fedora_41 4 spark x14.se  {ip1,ip2,ip3,ip4}
```


3) Fire up your cluster by installing iso's on hosts  

**syntax** kvm_cluster.sh osversion_ nodes_ nodename_ domain_   
**syntax** redfish_cluster.sh osversion_ nodes_ nodename_ domain_  {ip1,ip2,..}_

```bash
kvm_cluster.sh fedora_41 4 spark x14.se
```

a small cluster json vill be created with IP'setc..  

4) Use your cluster  
Its up and running and you have an cluster.json with ip's etc  



# CREDITS!  
To myself Rickard Ernst Björn Lundin on behalf of Swedish X14 AB and Danish Ignalina APS  
KVM parts are partly copied and inspired from from Earl C. Ruby III https://github.com/earlruby/create-vm  
Wikipedia image of Automata  

