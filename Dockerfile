# Usa un'immagine base Python ufficiale
FROM python:3.12

# Imposta la directory di lavoro nel container
WORKDIR /app

# Installa le dipendenze di sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copia il resto del codice dell'applicazione
COPY infra_utils infra_utils

# Copia i file di requirements prima per sfruttare la cache di Docker
COPY requirements.txt .

# Installa le dipendenze Python
RUN pip install --no-cache-dir infra_utils/v2.0/dist/infra_utils_sqlalchemy_2.0-0.0.2-py3-none-any.whl -r requirements.txt

# Copia il resto del codice dell'applicazione
COPY src src

# Copia il resto del codice dell'applicazione
COPY env env

#logs
RUN mkdir logs

COPY run.py .

# Esponi la porta su cui gira l'applicazione
EXPOSE 5000

# Variabili di ambiente
ENV FLASK_APP=run.py
ENV FLASK_RUN_HOST=0.0.0.0
#ENV PYTHONPATH="/app/src/"
# Comando per avviare l'applicazione
CMD ["flask", "run"]
#CMD ["ls", "-Rlas", "/app/src"]