from fastapi import FastAPI
from pydantic import BaseModel
import psycopg2
import uvicorn
import os
from dotenv import load_dotenv


load_dotenv()
# Connection to the database
host = os.getenv('host')
database = os.getenv('database')
user = os.getenv('user')
password = os.getenv('password')


conn = psycopg2.connect(
        host=host,
        database=database,
        user=user,
        password=password
    )

class Transaction(BaseModel):
    user_id: int
    amount: float
    from_user_id: int
    to_user_id: int

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post('/deposit')
def deposit_funds(transaction: Transaction):
    # Создание курсора
    cursor = conn.cursor()

    try:
        # Проверка наличия пользователя с заданным user_id
        cursor.execute("""
            SELECT COUNT(*) FROM user_balance WHERE user_id = %s
        """, (transaction.user_id,))
        user_exists = cursor.fetchone()[0] > 0

        if user_exists:
            # Выполнение SQL-запроса для начисления средств на баланс пользователя
            cursor.execute("""
                UPDATE user_balance
                SET amount = amount + %s
                WHERE user_id = %s
            """, (transaction.amount, transaction.user_id))
            return "Создан пользователь с ID {transaction.user_id}. Средства зачислены"
        else:
            # Выполнение SQL-запроса для создания новой записи пользователя
            cursor.execute("""
                INSERT INTO user_balance (user_id, amount)
                VALUES (%s, %s)
            """, (transaction.user_id, transaction.amount))

        # Подтверждение изменений
        conn.commit()

        print(f"Средства успешно зачислены на баланс пользователя с ID {transaction.user_id}.")

    except psycopg2.Error as e:
        # Обработка ошибок
        conn.rollback()
        print("Произошла ошибка при начислении средств на баланс пользователя.")
        print(e)


@app.post('/withdraw')
def withdraw_funds(transaction: Transaction):
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE user_balance SET amount = amount - %s WHERE user_id = %s;", (transaction.amount, transaction.user_id))
        conn.commit()
        return {'message': 'Средства успешно сняты с баланса пользователя с ID {transaction.user_id}.'}
    except psycopg2.Error:
        return {'message': 'Ошибка при снятии с баланса пользователя с ID {transaction.user_id}.'}
    finally:
        cursor.close()


@app.post('/transfer')
def transfer_funds(transaction: Transaction):
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE user_balance SET amount = amount - %s WHERE user_id = %s;", (transaction.amount, transaction.from_user_id))
        cursor.execute("UPDATE user_balance SET amount = amount + %s WHERE user_id = %s;", (transaction.amount, transaction.to_user_id))
        conn.commit()
        return {'message': 'Funds transferred successfully'}
    except psycopg2.Error:
        return {'message': 'Error transferring funds'}
    finally:
        cursor.close()


@app.get('/balance/{user_id}')
def get_balance(user_id: int):
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT amount FROM user_balance WHERE user_id = %s;", (user_id,))
        balance = cursor.fetchone()[0]
        return {'balance': balance}
    except psycopg2.Error:
        return {'message': 'Error retrieving balance'}
    finally:
        cursor.close()


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)