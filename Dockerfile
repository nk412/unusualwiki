FROM python:3.10-slim-bullseye
WORKDIR /app
RUN pip install flask gunicorn
COPY oddipedia.py dataset.json wsgi.py index.html .
CMD ["gunicorn", "-w", "4", "--bind", "0.0.0.0:5000", "wsgi:app"]
EXPOSE 5000
