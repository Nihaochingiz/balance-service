from fastapi import FastAPI
from pydantic import BaseModel
import psycopg2
import uvicorn
import os
from dotenv import load_dotenv

#load_dotenv()
#host = os.getenv('DB_HOST')
#database = os.getenv('DB_DATABASE')
#user = os.getenv('DB_USER')
#password = os.getenv('DB_PASSWORD')
host = 'db'
database = 'nudges'
user = 'username'
password = 'password'

conn = psycopg2.connect(
        host = host,
        database=database,
        user=user,
        password=password
    )

class Transaction(BaseModel):
    user_id: int
    amount: float

class Transfer(BaseModel):
    from_user_id: int
    to_user_id: int
    amount: float

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post('/deposit')
def deposit_funds(transaction: Transaction):
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT COUNT(*) FROM user_balance WHERE user_id = %s", (transaction.user_id,))
        user_exists = cursor.fetchone()[0] > 0

        if user_exists:
            cursor.execute("UPDATE user_balance SET amount = amount + %s WHERE user_id = %s", (transaction.amount, transaction.user_id))
            print(f"Funds successfully deposited to the user with ID {transaction.user_id}.")
            return {'Deposited to user with ID': transaction.user_id}
        else:
            cursor.execute("INSERT INTO user_balance (user_id, amount) VALUES (%s, %s)", (transaction.user_id, transaction.amount))
        conn.commit()

        print(f"User created. Funds deposited to the user with ID {transaction.user_id}.")
        return {'Deposited to user with ID': transaction.user_id, 'Deposited amount': transaction.amount}
    except psycopg2.Error as e:
        conn.rollback()
        print("An error occurred while depositing funds to user's balance.")
        print(e)

@app.post('/withdraw')
def withdraw_funds(transaction: Transaction):
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT amount FROM user_balance WHERE user_id = %s", (transaction.user_id,))
        current_balance = cursor.fetchone()[0]
        
        if current_balance >= transaction.amount:
            cursor.execute("UPDATE user_balance SET amount = amount - %s WHERE user_id = %s", (transaction.amount, transaction.user_id))
            conn.commit()
            return {'Funds withdrawn user ID': transaction.user_id}
        else:
            return {'message': 'Error: Insufficient funds in user balance.'}
    except psycopg2.Error:
        return {'Error withdrawing from ID': transaction.user_id}
    finally:
        cursor.close()

@app.post('/transfer')
def transfer_funds(transfer: Transfer):
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT amount FROM user_balance WHERE user_id = %s", (transfer.from_user_id,))
        current_balance = cursor.fetchone()[0]
        
        if current_balance >= transfer.amount:
            cursor.execute("UPDATE user_balance SET amount = amount - %s WHERE user_id = %s", (transfer.amount, transfer.from_user_id))
            cursor.execute("UPDATE user_balance SET amount = amount + %s WHERE user_id = %s", (transfer.amount, transfer.to_user_id))
            conn.commit()
            return {'message': 'Funds transferred successfully'}
        else:
            return {'message': 'Error: Insufficient funds in user balance for transfer.'}
    except psycopg2.Error:
        return {'message': 'Error transferring funds'}
    finally:
        cursor.close()

@app.get('/balance/{user_id}')
def get_balance(user_id: int):
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT amount FROM user_balance WHERE user_id = %s", (user_id,))
        balance = cursor.fetchone()[0]
        return {'balance': balance}
    except psycopg2.Error:
        return {'message': 'Error retrieving balance'}
    finally:
        cursor.close()

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)