FROM python:3.11-slim

WORKDIR /app

# Install dependencies from the root build context
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire repository into /app
# This includes schemas/, data/, and backend/
COPY . .

# Change workdir to backend so uvicorn finds the app module
WORKDIR /app/backend

# Expose port
EXPOSE 8000

# Start FastAPI server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
