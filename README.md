# Demonstrating Cloud Bursting using a Custom Kubernetes Scheduler.
This is an example demonstrating how to create a custom Kubernetes scheduler.
The custom scheduler modifies the Kubernetes default scheduler so that a GPU
related job can be provisioned in [Nimbix cloud](https://www.nimbix.net/) if the
local cluster is unable to satisfy the GPU resource requests.

### Project Organization
nimbix-app: Base image to be used for building application docker images
scheduler: Custom K8s scheduler files for Kubernetes version - 1.8.3
deploy: Sample deployment files

### How to build the custom scheduler.
```bash
git clone https://github.com/IBM/k8s-custom-scheduler.git
cd k8s-custom-scheduler/scheduler
docker build -t nimbix-sched .
```
### Deploy Nimbix scheduler on IBM Cloud Private (ICP)
While these instructions are specific for
[ICP](https://www.ibm.com/cloud-computing/products/ibm-cloud-private/), it
should apply for any Kubernetes setup with minor modifications

1.**Create a secret for the certificate files to access apiserver over https**<br>

In ICP, certificates file reside on /etc/cfc/conf in master node. Use the following command to create the secret
```bash
kubectl create secret generic certs --from-file=kube-scheduler-config.yaml --from-file=kube-scheduler.crt --from-file=kube-scheduler.key
```
2.**Build the images for custom scheduler and sample nimbix job**<br>

Use the Dockerfiles in **scheduler** and **nimbix-app** directory

3.**Deploy the scheduler**<br>

Example deployment yaml is available at deploy/k8s-custom-sched.yaml. Update the yaml file with the MASTER_IP
```bash
kubectl create -f k8s-custom-sched.yaml
```

4.**Create appropriate role binding so that custom scheduler from system:kube-scheduler can modify pods from default namespace**<br>

```bash
kubectl create rolebinding someRole --clusterrole=admin --user=system:kube-scheduler --namespace=default
```
5.**Deploy a sample GPU job using the custom scheduler**<br>

Example yaml is available at deploy/sample-job.yaml. Update the yaml with your Nimbix USERNAME and APIKEY.
The job will be provisioned to Nimbix cloud if resource requirement is not met in the local cluster
```bash
kubectl create -f sample-job.yaml
```
### Authors
Abhishek Dasgupta (abdasgupta@in.ibm.com)<br>
Pradipta Kumar Banerjee (bpradipt@in.ibm.com)
