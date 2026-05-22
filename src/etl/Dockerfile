FROM python:3.11-slim

WORKDIR /app

# Instalar dependências de sistema
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copiar requisitos e instalar
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fonte
COPY src/ /app/src/

# Configurar PYTHONPATH para encontrar os módulos em src/
ENV PYTHONPATH=/app/src

CMD ["python", "src/batch_manager.py"]
