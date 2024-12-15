FROM python:3.11

WORKDIR /household_account_book

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./household_account_book .

CMD ["gunicorn", "household_account_book:app", "--bind", "0.0.0.0:8000"]
