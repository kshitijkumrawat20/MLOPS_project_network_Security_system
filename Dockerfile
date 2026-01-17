# for aws 
# FROM python:3.10-slim-buster
# WORKDIR /app
# COPY . /app
# RUN apt update -y && apt install awscli -y 
# RUN apt-get update && pip install -r requirements.txt
# CMD ["python3", "app.py"]
 
FROM python:3.13-slim

RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

WORKDIR /app

# Copy requirements
COPY --chown=user ./requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy all application files
COPY --chown=user . /app

# Create necessary directories
RUN mkdir -p /app/data /app/final_model /app/templates

# run the load_data_to_sqlite.py script to initialize the database
RUN python load_data_to_sqlite.py

# Expose port 7860 (HF Space requirement)
EXPOSE 7860

# Run the application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]