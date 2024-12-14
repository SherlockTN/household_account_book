FROM python:3.11

WORKDIR /家計簿

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./家計簿 .

CMD ["gunicorn", "household_account_book:app", "--bind", "0.0.0.0:8000"]