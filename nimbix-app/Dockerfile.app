FROM jarvice/powerai

RUN apt-get update && apt-get install -y \
    libffi-dev
RUN pip install jarviceclient
RUN pip install jinja2

ADD jarvice_submit.py /
ADD job_template.json /

WORKDIR /

ENTRYPOINT ["python", "/jarvice_submit.py"]
