# Automata
Create clusters for distributed software

Automata does this by Generate OS iso's and fire them up on hosts (kvm or redfish)

1) Factory your media ,one for each node in cluster.  

iso_factory.sh <osversion> <nodes> <nodename> <domain>  

For example , to create 4 isos with hostnames {spark1.x14.se, spark2.x14.se, spark3.x14.se}  
```bash
iso_create.sh fedora_41 4 spark x14.se
```

2) Initate your hosts   (DISCLAIMER WARNING WILL DESTROY / FORMAT / DELETE your hosts)  
initate  osversion nodes nodename domain  

using local kvm  
```bash
kvm_initiate.sh fedora_41 4 spark x14.se
```
or redfish  where you must set ip1...ip4 to your hardwares BMC.  
```bash
redfish_initiate.sh fedora_41 4 spark x14.se  {ip1,ip2,ip3,ip4}
```


3) Fire up your cluster by installing iso's on hosts  

kvm_cluster.sh <osversion> <nodes> <nodename> <domain>   
redfish_cluster.sh <osversion> <nodes> <nodename> <domain>  

```bash
kvm_cluster.sh fedora_41 4 spark x14.se
```

a small cluster json vill be created with IP'setc..  

4) Use your cluster  
Its up and running and you have an cluster.json with ip's etc  



# CREDITS!  
To myself Rickard Ernst Björn Lundin on behalf of Swedish X14 AB and Danish Ignalina APS  
KVM parts are partly copied and inspired from from Earl C. Ruby III https://github.com/earlruby/create-vm  
![alt text]([(https://en.wikipedia.org/wiki/Digesting_Duck#/media/File:Digesting_Duck.jpg](https://en.wikipedia.org/wiki/Digesting_Duck#/media/File:Digesting_Duck.jpg))

