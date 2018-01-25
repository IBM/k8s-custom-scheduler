FROM python:2.7

RUN pip install jarviceclient
RUN pip install jinja2

ADD jarvice_submit.py /
ADD job_template.json /
ENTRYPOINT ["python", "/jarvice_submit.py"]
