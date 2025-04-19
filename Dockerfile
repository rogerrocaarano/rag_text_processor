FROM python:3.12

WORKDIR /app


RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential && \
    rm -rf /var/lib/apt/lists/*


RUN pip install --no-cache-dir -U fastapi uvicorn python-multipart

RUN pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir -U sentence-transformers

RUN pip install --no-cache-dir -U pip setuptools wheel
RUN pip install --no-cache-dir -U spacy

RUN pip install --no-cache-dir -U hf_xet

RUN python -m spacy download es_dep_news_trf && \
    python -m spacy validate && \
    python -c "import spacy; spacy.load('es_dep_news_trf')" && \
    rm -rf /root/.cache

COPY . /app

EXPOSE 5000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000"]
