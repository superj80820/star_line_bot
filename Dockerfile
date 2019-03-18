FROM python:3.6

#==================================
# Workspace
#==================================
ADD . /app
WORKDIR /app

#==================================
# Install python lib
#==================================
RUN pip install -r requirements.txt

CMD ["python", "__init__.py"]
