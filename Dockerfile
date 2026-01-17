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
RUN mkdir -p /app/data /app/final_model /app/templates /app/monitoring/reports /app/prefect_flows

# Make startup script executable
RUN chmod +x /app/startup.sh

# run the load_data_to_sqlite.py script to initialize the database
RUN python load_data_to_sqlite.py

# Run cloud configuration check (non-blocking)
RUN python cloud_config.py || echo "Cloud config check completed"

# Expose port 7860 (HF Space requirement)
EXPOSE 7860

# Use startup script to initialize cloud services, then start app
ENTRYPOINT ["/app/startup.sh"]
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]