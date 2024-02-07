Реализация
- [autumn-2021-intern-assignment](https://github.com/avito-tech/autumn-2021-intern-assignment)

Язык программирования Python

### Методы

- Метод начисления средств на баланс. 
Принимает id пользователя и сколько средств зачислить.

- Метод списания средств с баланса. 
Принимает id пользователя и сколько средств списать.

- Метод перевода средств от пользователя к пользователю. 
Принимает id пользователя с которого нужно списать средства, id пользователя которому должны зачислить средства, а также сумму.

- Метод получения текущего баланса пользователя. 
Принимает id пользователя. Баланс всегда в рублях.


### Инструкция по запуску 

- git clone данный репозиторий
- cd в созданный репозиторий
- pip install -r requirements.txt
- В env поставьте ваши данные по подключение к БД
- запустите скрипт create_db_script.sql
- uvicorn main:app --host localhost
- Заходите на http://localhost:8000/docs


### API Documentation

This document provides an overview of the functionality and endpoints of the API developed in the provided Python code that interacts with a PostgreSQL database for managing user balances.

#### Base URL
The base URL for the API is `http://localhost:8000`.

#### Endpoints

##### `GET /`
- Description: Returns a simple greeting message.
- Response:
    ```
    {
        "message": "Hello World"
    }
    ```

##### `POST /deposit`
- Description: Deposits funds to a user's balance.
- Request Body:
    ```json
    {
        "user_id": integer,
        "amount": float
    }
    ```
- Response:
    ```
    {
        "Deposited to user with ID": integer,
        "Deposited amount": float
    }
    ```

##### `POST /withdraw`
- Description: Withdraws funds from a user's balance.
- Request Body:
    ```json
    {
        "user_id": integer,
        "amount": float
    }
    ```
- Response:
    ```
    {
        "Funds withdrawn user ID": integer
    }
    ```

##### `POST /transfer`
- Description: Transfers funds from one user to another.
- Request Body:
    ```json
    {
        "from_user_id": integer,
        "to_user_id": integer,
        "amount": float
    }
    ```
- Response:
    ```
    {
        "message": "Funds transferred successfully"
    }
    ```

##### `GET /balance/{user_id}`
- Description: Retrieves the current balance of a specific user.
- Path Parameter:
    - `user_id`: integer
- Response:
    ```
    {
        "balance": float
    }
    ```

#### Error Handling
- Any errors encountered during API operations are logged, and appropriate error messages are returned in the response.

#### Running the Server
To run the server, execute the Python script. The API will be served locally on `localhost` at port `8000`.

```bash
python filename.py
```

ℹ️ Make sure to have the required environment variables set for `HOST`, `DATABASE`, `USER`, and `PASSWORD` for successful database connection.

🚀 Thank you for checking out the API documentation! If you have any further questions or need assistance, feel free to ask!
