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
            print(f"Средства успешно зачислены на баланс пользователя с ID {transaction.user_id}.")
            return {'Зачислены пользователю с ID': transaction.user_id}
        else:
            # Выполнение SQL-запроса для создания новой записи пользователя
            cursor.execute("""
                INSERT INTO user_balance (user_id, amount)
                VALUES (%s, %s)
            """, (transaction.user_id, transaction.amount))
        # Подтверждение изменений
        conn.commit()

        print(f"Пользователь создан. Средства  зачислены на баланс пользователя с ID {transaction.user_id}.")
        return {'Зачислены пользователю с ID': transaction.user_id,
                'Зачисленная сумма'          : transaction.amount
                 }
    except psycopg2.Error as e:
        # Обработка ошибок
        conn.rollback()
        print("Произошла ошибка при начислении средств на баланс пользователя.")
        print(e)


@app.post('/withdraw')
def withdraw_funds(transaction: Transaction):
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT amount FROM user_balance WHERE user_id = %s;", (transaction.user_id,))
        current_balance = cursor.fetchone()[0]
        
        if current_balance >= transaction.amount:
            cursor.execute("UPDATE user_balance SET amount = amount - %s WHERE user_id = %s;", (transaction.amount, transaction.user_id))
            conn.commit()
            return {'Средства сняты ID': transaction.user_id}
        else:
            return {'message': 'Ошибка: Недостаточно средств на балансе пользователя.'}
    except psycopg2.Error:
        return {'Ошибка при снятии с ID': transaction.user_id}
    finally:
        cursor.close()


@app.post('/transfer')
def transfer_funds(transfer: Transfer):
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT amount FROM user_balance WHERE user_id = %s;", (transfer.from_user_id,))
        current_balance = cursor.fetchone()[0]
        
        if current_balance >= transfer.amount:
            cursor.execute("UPDATE user_balance SET amount = amount - %s WHERE user_id = %s;", (transfer.amount, transfer.from_user_id))
            cursor.execute("UPDATE user_balance SET amount = amount + %s WHERE user_id = %s;", (transfer.amount, transfer.to_user_id))
            conn.commit()
            return {'message': 'Funds transferred successfully'}
        else:
            return {'message': 'Ошибка: Недостаточно средств на балансе пользователя для перевода.'}
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