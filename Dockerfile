#ARG IMAGE=intersystemsdc/irishealth-community
#ARG IMAGE=intersystemsdc/iris-community:preview
#ARG IMAGE=intersystemsdc/iris-community
ARG IMAGE=intersystemsdc/iris-community:latest
FROM $IMAGE

WORKDIR /home/irisowner/dev

ARG TESTS=0
ARG MODULE="iris-email-analyzer-app"
ARG NAMESPACE="USER"


# create Python env
## Embedded Python environment
## Python stuff
ENV IRISUSERNAME "SuperUser"
ENV IRISPASSWORD "SYS"
ENV IRISNAMESPACE "USER"
ENV PYTHON_PATH=/usr/irissys/bin/
ENV LD_LIBRARY_PATH=${ISC_PACKAGE_INSTALLDIR}/bin:${LD_LIBRARY_PATH}
ENV PATH "/usr/irissys/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/home/irisowner/bin:/home/irisowner/.local/bin"
ENV FILE_READ_PATH /home/irisowner/dev/input

## Start IRIS
RUN --mount=type=bind,src=.,dst=. \
    pip3 install -r requirements.txt && \
    iris start IRIS && \
    iris merge IRIS merge.cpf && \
    irispython iris_script.py && \
    iris stop IRIS quietly

COPY . .

#ENTRYPOINT [ "irispython", "python/app.py" ]