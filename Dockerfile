FROM ubuntu:16.04

RUN apt-get update && apt-get install -y python-pip git
RUN pip install dicom six Cython scipy
RUN git clone https://github.com/nipy/nibabel.git /nibabel
RUN cd /nibabel && python setup.py build_ext --inplace
RUN git clone https://github.com/nipy/dipy.git /dipy
RUN cd /dipy && PYTHONPATH=/nibabel python setup.py build_ext --inplace

RUN mkdir /app
COPY main.py /app

RUN mkdir /output
WORKDIR /output

ENV PYTHONPATH /dipy:$PYTHONPATH
ENV PYTHONPATH /nibabel:$PYTHONPATH

#CMD python /app/main.py

ENTRYPOINT ["/usr/bin/python", "/app/main.py"]
