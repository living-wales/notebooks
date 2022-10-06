FROM jupyter/minimal-notebook

# Run apt update (need to do this as root)
USER root
RUN apt-get update && apt-get install gcc g++ libgdal-dev -y

COPY . /code

# Install requirements
RUN pip install -r /code/requirements.txt 

# Install LCCS code
RUN pip3 install git+https://bitbucket.org/au-eoed/livingearth_lccs.git

RUN ln -s /code/LW-notebooks /notebooks

# Switch back to jovyan 
USER ${NB_UID}
COPY .datacube.conf /home/jovyan

ENV PYTHONPATH /code/LW-notebooks:$PYTHONPATH

CMD ["jupyter", "lab", \
"--ip=0.0.0.0", \
"--port=9988", \
"--no-browser"]

