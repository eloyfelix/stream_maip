# Use the official Python image as the base image
FROM python:3.12

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Streamlit app files into the container
COPY pages/ pages/
COPY MAIP.py .

# Expose the port that Streamlit runs on (default is 8501)
EXPOSE 8501

# Set the command to run the Streamlit app
CMD ["streamlit", "run", "MAIP.py"]
