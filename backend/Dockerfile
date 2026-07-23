FROM python:3.11-slim

WORKDIR /app

# Copy only requirements first, dependency installs get cached as a
# separate layer and only re-run when requirements.txt actually changes.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Now copy the rest of the code
COPY . .

EXPOSE 10000
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
