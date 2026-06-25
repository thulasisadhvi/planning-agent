# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies required for some Python packages (like pdfplumber)
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Keep the container alive or run the default command
CMD ["python", "main.py", "--transcript", "./data/sample_transcript.pdf", "--goal", "Plan my next two semesters."]