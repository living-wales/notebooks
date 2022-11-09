FROM jupyter/minimal-notebook

# Run apt update (need to do this as root)
USER root
RUN apt-get update && apt-get install gcc g++ libgdal-dev vim wget htop rsync -y
RUN apt-get update && apt-get install iproute2 iputils-ping and netcat-openbsd -y

# Copy code into the container
COPY . /code

# Install some notebook plugins
RUN pip install jupyterlab-system-monitor

# Install requirements
RUN pip install -r /code/requirements.txt 

# Install LCCS code
RUN pip3 install git+https://bitbucket.org/au-eoed/livingearth_lccs.git

# Link notebooks to /notebooks
RUN mkdir -p /notebooks && \
    ln -s /code/Beginners_guide /notebooks/ && \
    ln -s /code/Case_Studies /notebooks/ && \
    ln -s /code/img /notebooks/ && \
    ln -s /code/Vectors /notebooks && \
    ln -s /code/wales_utils /notebooks

# Switch back to jovyan 
USER ${NB_UID}
COPY .datacube.conf /home/jovyan

CMD ["jupyter", "lab", \
     "--ip=0.0.0.0", \
     "--port=9988", \
     "--no-browser"]

