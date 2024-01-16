import mysql.connector
from decimal import Decimal, InvalidOperation
from datetime import datetime

# Function to establish a database connection
def connect_to_database():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root",
            database="banking_system"
        )
        return connection
    except mysql.connector.Error as\
            err:
        print(f"Error: {err}")
        return None

# Function to create the database and tables if not present
def create_database():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root",
        )
        cursor = connection.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS banking_system")
        cursor.execute("USE banking_system")
        cursor.execute("CREATE TABLE IF NOT EXISTS accounts (id INT AUTO_INCREMENT PRIMARY KEY, account_holder VARCHAR(255), account_number INT, password VARCHAR(255), balance DECIMAL(10, 2))")
        cursor.execute("CREATE TABLE IF NOT EXISTS transactions (id INT AUTO_INCREMENT PRIMARY KEY, account_holder VARCHAR(255), account_number INT, transaction_type VARCHAR(50), amount DECIMAL(10, 2), timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
        connection.commit()
        cursor.close()
        connection.close()
    except mysql.connector.Error as err:
        print(f"Error: {err}")

# Function to create a new bank account
def create_account(connection, account_holder, account_number, password, initial_balance):
    cursor = connection.cursor()
    try:
        cursor.execute("INSERT INTO accounts (account_holder, account_number, password, balance) VALUES (%s, %s, %s, %s)",
                       (account_holder, account_number, password, Decimal(initial_balance)))
        connection.commit()
        print("Account created successfully!")
    except mysql.connector.Error as err:
        connection.rollback()
        print(f"Error: {err}")
    finally:
        cursor.close()

# Function to authenticate a user
def authenticate_user(connection, account_number, password):
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT account_holder FROM accounts WHERE account_number = %s AND password = %s", (account_number, password))
        result = cursor.fetchone()
        if result:
            return result[0]  # Return account holder name if authentication successful
        else:
            return None
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None
    finally:
        cursor.close()

# Function to fetch bank balance
def fetch_balance(connection, account_holder):
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT balance FROM accounts WHERE account_holder = %s", (account_holder,))
        result = cursor.fetchone()
        if result:
            print(f"Balance for {account_holder}: ${result[0]}")
        else:
            print(f"Account not found for {account_holder}")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()

# Function to withdraw amount
def withdraw_amount(connection, account_holder, amount):
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT balance FROM accounts WHERE account_holder = %s", (account_holder,))
        result = cursor.fetchone()
        if result:
            current_balance = Decimal(result[0])
            amount = Decimal(amount)
            if current_balance >= amount:
                new_balance = current_balance - amount
                cursor.execute("UPDATE accounts SET balance = %s WHERE account_holder = %s", (new_balance, account_holder))
                cursor.execute("INSERT INTO transactions (account_holder, account_number, transaction_type, amount) VALUES (%s, %s, %s, %s)",
                               (account_holder, result[0], 'Withdrawal', amount))
                connection.commit()
                print(f"Withdrawal successful! New balance for {account_holder}: ${new_balance}")
            else:
                print("Insufficient funds.")
        else:
            print(f"Account not found for {account_holder}")
    except mysql.connector.Error as err:
        connection.rollback()
        print(f"Error: {err}")
    except InvalidOperation as e:
        connection.rollback()
        print(f"Error: {e}")
    finally:
        cursor.close()

# Function to deposit amount
def deposit_amount(connection, account_holder, amount):
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT balance FROM accounts WHERE account_holder = %s", (account_holder,))
        result = cursor.fetchone()
        if result:
            current_balance = Decimal(result[0])
            amount = Decimal(amount)
            new_balance = current_balance + amount
            cursor.execute("UPDATE accounts SET balance = %s WHERE account_holder = %s", (new_balance, account_holder))
            cursor.execute("INSERT INTO transactions (account_holder, account_number, transaction_type, amount) VALUES (%s, %s, %s, %s)",
                           (account_holder, result[0], 'Deposit', amount))
            connection.commit()
            print(f"Deposit successful! New balance for {account_holder}: ${new_balance}")
        else:
            print(f"Account not found for {account_holder}")
    except mysql.connector.Error as err:
        connection.rollback()
        print(f"Error: {err}")
    except InvalidOperation as e:
        connection.rollback()
        print(f"Error: {e}")
    finally:
        cursor.close()

# Function to view account statement
def view_account_statement(connection, account_holder):
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT * FROM transactions WHERE account_holder = %s", (account_holder,))
        result = cursor.fetchall()
        if result:
            print(f"Account Statement for {account_holder}:")
            for row in result:
                print(f"ID: {row[0]}, Transaction Type: {row[3]}, Amount: ${row[4]}, Timestamp: {row[5]}")
        else:
            print(f"No transactions found for {account_holder}")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()

# Main function
def main():
    create_database()
    connection = connect_to_database()

    if connection:
        print("1. Create Account")
        print("2. Login")
        choice = input("Select an option (1 or 2): ")

        if choice == "1":
            account_holder = input("Enter account holder's name: ")
            account_number = int(input("Enter account number: "))
            password = input("Set a password: ")
            initial_balance = int(input("Enter initial balance: "))
            create_account(connection, account_holder, account_number, password, initial_balance)
        elif choice == "2":
            account_number = int(input("Enter account number: "))
            password = input("Enter password: ")
            account_holder = authenticate_user(connection, account_number, password)
            if account_holder:
                print(f"Login successful! Welcome, {account_holder}!")
                while True:
                    print("\n1. View Balance")
                    print("2. Withdraw")
                    print("3. Deposit")
                    print("4. View Account Statement")
                    print("5. Logout")
                    option = input("Select an option (1-5): ")

                    if option == "1":
                        fetch_balance(connection, account_holder)
                    elif option == "2":
                        amount = int(input("Enter withdrawal amount: "))
                        withdraw_amount(connection, account_holder, amount)
                    elif option == "3":
                        amount = int(input("Enter deposit amount: "))
                        deposit_amount(connection, account_holder, amount)
                    elif option == "4":
                        view_account_statement(connection, account_holder)
                    elif option == "5":
                        print("Logout successful.")
                        break
                    else:
                        print("Invalid option. Please try again.")
            else:
                print("Login failed. Invalid account number or password.")

        # Close the database connection
        connection.close()

if __name__ == "__main__":
    main()
