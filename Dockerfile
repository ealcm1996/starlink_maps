FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Exponer el puerto que usa Flask
EXPOSE 5000

# Variable de entorno para indicar que estamos en Render
ENV IS_RENDER=true

CMD ["python", "starlink_map.py"]
