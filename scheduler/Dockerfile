FROM golang:1.8

RUN git clone https://github.com/kubernetes/kubernetes.git
RUN apt-get update && apt-get install -y rsync
ADD scheduler.go factory.go /
RUN cd kubernetes && git checkout -b v1.8.3 v1.8.3 && \
    cp /scheduler.go plugin/pkg/scheduler/scheduler.go && \
    cp /factory.go plugin/pkg/scheduler/factory/factory.go && \
    make all WHAT=plugin/cmd/kube-scheduler/ &&\
    cp _output/bin/kube-scheduler /kube-scheduler-nimbix

FROM debian:jessie
COPY --from=0 /kube-scheduler-nimbix /
CMD ["/kube-scheduler-nimbix"]
