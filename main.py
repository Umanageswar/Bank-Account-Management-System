import mysql.connector

try:
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="YOUR PASSWORD",
        database="bank_management"
    )
    if connection.is_connected():
        print("Connected to MySQL successfully!")
except mysql.connector.Error as e:
    print("Database connection failed:", e)
    connection = None

def create_account():
    if connection is None:
        print("Database connection is not available.")
        return
    try:
        name = input("Enter your name: ").strip()
        if not name:
            print("Name cannot be empty.")
            return
        phone = input("Enter your phone number: ").strip()
        if not phone.isdigit() or len(phone) != 10:
            print("Phone number must contain exactly 10 digits.")
            return
        pin = input("Create a 4-digit PIN: ").strip()
        if len(pin) != 4 or not pin.isdigit():
            print("PIN must contain exactly 4 digits.")
            return
        initial_deposit = float(input("Enter initial deposit: "))
        if initial_deposit < 0:
            print("Initial deposit cannot be negative.")
            return
        cursor = connection.cursor()
        query = """
            INSERT INTO accounts (name, phone, pin, balance)
            VALUES (%s, %s, %s, %s)
        """
        values = (name, phone, pin, initial_deposit)
        cursor.execute(query, values)
        connection.commit()
        print("Account created successfully!")
        print("Your Account Number is:", cursor.lastrowid)
        cursor.close()
    except ValueError:
        print("Please enter a valid amount.")
    except mysql.connector.Error as e:
        connection.rollback()
        print("Database error:", e)
def login():
    if connection is None:
        print("Database connection is not available.")
        return
    try:
        account_no = int(input("Enter your account number: "))
        pin = input("Enter your PIN: ").strip()
        cursor = connection.cursor()
        query = """
            SELECT account_no, name, balance
            FROM accounts
            WHERE account_no = %s AND pin = %s
        """
        cursor.execute(query, (account_no, pin))
        account = cursor.fetchone()
        if account:
            print("\nLogin successful!")
            print("Welcome,", account[1])
            account_menu(account[0])
        else:
            print("\nInvalid account number or PIN.")
        cursor.close()
    except ValueError:
        print("Please enter a valid account number.")
    except mysql.connector.Error as e:
        print("Database error:", e)
def account_menu(account_no):
    while True:
        print("\n===== BANK ACCOUNT MENU =====")
        print("1. Check Balance")
        print("2. Deposit")
        print("3. Withdraw")
        print("4. Transfer Money")
        print("5. Transaction History")
        print("6. Change PIN")
        print("7. Logout")
        choice = input("Enter your choice: ").strip()
        if choice == "1":
            check_balance(account_no)
        elif choice == "2":
            deposit(account_no)
        elif choice == "3":
            withdraw(account_no)
        elif choice == "4":
            transfer_money(account_no)
        elif choice == "5":
            transaction_history(account_no)
        elif choice == "6":
            change_pin(account_no)
        elif choice == "7":
            print("Logged out successfully.")
            break
        else:
            print("Invalid choice. Please select 1-7.")

def check_balance(account_no):
    if connection is None:
        return
    cursor = None
    try:
        cursor = connection.cursor()
        query = """
            SELECT balance
            FROM accounts
            WHERE account_no = %s
        """
        cursor.execute(query, (account_no,))
        result = cursor.fetchone()
        if result:
            print("Current Balance: ₹", result[0])
        else:
            print("Account not found.")
    except mysql.connector.Error as e:
        print("Database error:", e)
    finally:
        if cursor:
            cursor.close()

def deposit(account_no):
    if connection is None:
        return
    cursor = None
    try:
        amount = float(input("Enter deposit amount: "))
        if amount <= 0:
            print("Amount must be greater than 0.")
            return
        cursor = connection.cursor()
        query = """
            UPDATE accounts
            SET balance = balance + %s
            WHERE account_no = %s
        """
        cursor.execute(query, (amount, account_no))
        if cursor.rowcount == 0:
            print("Account not found.")
            return
        transaction_query = """
            INSERT INTO transactions
            (account_no, transaction_type, amount)
            VALUES (%s, %s, %s)
        """
        cursor.execute(
            transaction_query,
            (account_no, "DEPOSIT", amount)
        )
        connection.commit()
        print("Amount deposited successfully.")
        print("Deposited Amount: ₹", amount)
    except ValueError:
        print("Please enter a valid amount.")
    except mysql.connector.Error as e:
        connection.rollback()
        print("Database error:", e)
    finally:
        if cursor:
            cursor.close()
def withdraw(account_no):
    if connection is None:
        return
    cursor = None
    try:
        amount = float(input("Enter withdrawal amount: "))
        if amount <= 0:
            print("Amount must be greater than 0.")
            return
        cursor = connection.cursor()
        query = """
            SELECT balance
            FROM accounts
            WHERE account_no = %s
        """
        cursor.execute(query, (account_no,))
        result = cursor.fetchone()
        if result is None:
            print("Account not found.")
            return
        balance = result[0]
        if amount > balance:
            print("Insufficient balance.")
            print("Available Balance: ₹", balance)
            return
        update_query = """
            UPDATE accounts
            SET balance = balance - %s
            WHERE account_no = %s
        """
        cursor.execute(update_query, (amount, account_no))
        transaction_query = """
            INSERT INTO transactions
            (account_no, transaction_type, amount)
            VALUES (%s, %s, %s)
        """
        cursor.execute(
            transaction_query,
            (account_no, "WITHDRAW", amount)
        )
        connection.commit()
        print("Amount withdrawn successfully.")
        print("Withdrawn Amount: ₹", amount)
    except ValueError:
        print("Please enter a valid amount.")
    except mysql.connector.Error as e:
        connection.rollback()
        print("Database error:", e)
    finally:
        if cursor:
            cursor.close()

def transfer_money(sender_account_no):
    if connection is None:
        return
    cursor = None
    try:
        receiver_account_no = int(
            input("Enter receiver account number: ")
        )
        amount = float(input("Enter transfer amount: "))
        if amount <= 0:
            print("Amount must be greater than 0.")
            return
        if sender_account_no == receiver_account_no:
            print("You cannot transfer money to the same account.")
            return
        cursor = connection.cursor()
        query = """
            SELECT account_no
            FROM accounts
            WHERE account_no = %s
        """
        cursor.execute(query, (receiver_account_no,))
        receiver = cursor.fetchone()
        if receiver is None:
            print("Receiver account not found.")
            return
        query = """
            SELECT balance
            FROM accounts
            WHERE account_no = %s
        """
        cursor.execute(query, (sender_account_no,))
        sender = cursor.fetchone()
        if sender is None:
            print("Sender account not found.")
            return
        sender_balance = sender[0]
        if amount > sender_balance:
            print("Insufficient balance.")
            print("Available Balance: ₹", sender_balance)
            return
        update_sender = """
            UPDATE accounts
            SET balance = balance - %s
            WHERE account_no = %s
        """
        cursor.execute(
            update_sender,
            (amount, sender_account_no)
        )
        update_receiver = """
            UPDATE accounts
            SET balance = balance + %s
            WHERE account_no = %s
        """
        cursor.execute(
            update_receiver,
            (amount, receiver_account_no)
        )
        sender_transaction = """
            INSERT INTO transactions
            (account_no, transaction_type, amount)
            VALUES (%s, %s, %s)
        """
        cursor.execute(
            sender_transaction,
            (sender_account_no, "TRANSFER_OUT", amount)
        )
        receiver_transaction = """
            INSERT INTO transactions
            (account_no, transaction_type, amount)
            VALUES (%s, %s, %s)
        """
        cursor.execute(
            receiver_transaction,
            (receiver_account_no, "TRANSFER_IN", amount)
        )
        connection.commit()
        print("Money transferred successfully.")
        print("Transferred Amount: ₹", amount)
    except ValueError:
        print("Please enter valid account number and amount.")
    except mysql.connector.Error as e:
        connection.rollback()
        print("Transfer failed. No changes were saved.")
        print("Database error:", e)
    finally:
        if cursor:
            cursor.close()

def transaction_history(account_no):
    if connection is None:
        return
    cursor = None
    try:
        cursor = connection.cursor()
        query = """
            SELECT transaction_id, transaction_type, amount, transaction_date
            FROM transactions
            WHERE account_no = %s
            ORDER BY transaction_date DESC
        """
        cursor.execute(query, (account_no,))
        transactions = cursor.fetchall()
        if not transactions:
            print("No transactions found.")
            return
        print("\n========== TRANSACTION HISTORY ==========")
        print("ID\tType\t\tAmount\t\tDate")
        print("------------------------------------------")
        for transaction in transactions:
            print(
                transaction[0],
                "\t",
                transaction[1],
                "\t₹",
                transaction[2],
                "\t",
                transaction[3]
            )
    except mysql.connector.Error as e:
        print("Database error:", e)
    finally:
        if cursor:
            cursor.close()

def change_pin(account_no):
    if connection is None:
        return
    cursor = None
    try:
        current_pin = input("Enter current PIN: ").strip()
        cursor = connection.cursor()
        query = """
            SELECT pin
            FROM accounts
            WHERE account_no = %s
        """
        cursor.execute(query, (account_no,))
        result = cursor.fetchone()
        if result is None:
            print("Account not found.")
            return
        if current_pin != result[0]:
            print("Incorrect current PIN.")
            return
        new_pin = input("Enter new PIN: ").strip()
        confirm_pin = input("Confirm new PIN: ").strip()
        if len(new_pin) != 4 or not new_pin.isdigit():
            print("PIN must contain exactly 4 digits.")
            return
        if new_pin != confirm_pin:
            print("PINs do not match.")
            return
        if new_pin == current_pin:
            print("New PIN must be different from the current PIN.")
            return
        update_query = """
            UPDATE accounts
            SET pin = %s
            WHERE account_no = %s
        """
        cursor.execute(update_query, (new_pin, account_no))
        connection.commit()
        print("PIN changed successfully.")
    except mysql.connector.Error as e:
        connection.rollback()
        print("Database error:", e)

    finally:
        if cursor:
            cursor.close()

def main():
    while True:
        print("\n===== BANK ACCOUNT MANAGEMENT SYSTEM =====")
        print("1. Create Account")
        print("2. Login")
        print("3. Exit")
        choice = input("Enter your choice: ")
        if choice == "1":
            create_account()
        elif choice == "2":
            login()
        elif choice == "3":
            print("Thank you for using the Bank Account Management System.")
            break
        else:
            print("Invalid choice. Please select 1-3.")

if connection:
    try:
        main()
    except KeyboardInterrupt:
        print("\nProgram stopped by user.")
    finally:
        if connection.is_connected():
            connection.close()
            print("Database connection closed.")
