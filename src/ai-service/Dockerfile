# Use the official Python image as the base image
FROM python:3.11.1-slim-buster

# Set the working directory to /app
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

#Create openai-key as ARG and ENV

ARG OPENAI_API_KEY=${OPENAI_API_KEY}
ARG OPENAI_ORG_ID=${OPENAI_ORG_ID}
ARG USE_AZURE_OPENAI=${USE_AZURE_OPENAI}

ENV OPENAI_API_KEY=${OPENAI_API_KEY}
ENV OPENAI_ORG_ID=${OPENAI_ORG_ID}
ENV USE_AZURE_OPENAI=${USE_AZURE_OPENAI}


# Copy the rest of the application code into the container
COPY . .

# Expose port 5001 for the FastAPI application
EXPOSE 5001

# Start the FastAPI application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5001"]