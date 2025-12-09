FROM python:3.12-slim

ENV MNSET_IP_Address=0.0.0.0
ENV MNSET_NBAPI_Port=9080
ENV MNSET_Fusion6B_Array_Name=Fusion6B
ENV MNSET_Fusion3B_Array_Name=Fusion3B

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "web_server.py"]
