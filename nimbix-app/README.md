## Introduction
This is an example of using a docker image to provision a job in Nimbix - https://www.nimbix.net/
leveraging the Nimbix CLI.
Read more about Nimbix CLI here -  https://www.nimbix.net/jarvice-quick-start-guide/

There are two Dockerfiles. 
Dockerfile.base - Used to build the docker image to spawn a job in Nimbix. 
It uses certain environment variables to specific the required details.

Dockerfile.app - Used to build an example docker image that can be run either in the local cluster
or Nimbix. Nimbix expects a specific layout of the application environment in the docker image and hence a specific base 
image needs to be used. 
In the example we have used a Power LE (ppc64le) powerai Nimbix base image. You can use your own base image depending on your
requirements. 

You can read more about creating docker images for Nimbix here - http://jarvice.readthedocs.io/en/latest/cicd/

## Build Docker Image

```bash
$ sudo docker build -t nimbix -f Dockerfile.base .
```

```bash
$ sudo docker build -t ppc64le/powerai -f Dockerfile.app .
```


## Example Runs
### Submit a Job and wait for the job to finish/terminate

The following command will provision a job in Nimbix cluster

```bash
$ sudo docker run -it \ 
            -e USERNAME=USERNAME \
            -e APIKEY=123456abcdefgh2974 \
            -e APP_NAME=my_app \
            -e APP_COMMAND=run \
	    -e APP_COMMAND_ARGS="/run_trainig.sh"\
            -e REMOTE=1\
            -e ARCH=POWER \
            -e NUM_CPUS=60 \
            -e NUM_GPUS=2 \
nimbix
```

The following command will run the job in your local cluster

```bash
sudo docker run -it \
            -e "USERNAME=user" \
            -e "APIKEY=123456789"\
            -e "APP_NAME=power8-ubuntu-mldl"\
            -e "APP_COMMAND=run"\
            -e "APP_COMMAND_ARGS='source /opt/DL/bazel/bin/bazel-activate && source /opt/DL/tensorflow/bin/tensorflow-activate && tensorflow-test'" \
ppc64le/powerai
```
