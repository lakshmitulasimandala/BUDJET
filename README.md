BUDJET - Add Speed and Smoothness in Managing Money!

Project Overview:
BUDJET is a simple Flask web application designed to help users manage their finances with speed and ease. It allows users to add transactions, view active transactions, and track the history of finalized transactions.

The app uses SQLite for storing both active transactions and the transaction history. Users can add new transactions, view ongoing ones, and finalize them by moving them to the transaction history.

Features:
Add Transaction: Users can add a new transaction with an amount and category, which is stored in the active transactions table.
View Active Transactions: Displays a list of all active transactions with relevant details like amount, category, and timestamp.
View Transaction History: Shows all finalized transactions that have been moved to the transaction history.
Move to History: Users can move active transactions to the history once they are finalized.


Technologies Used:
Flask: A lightweight Python web framework used to create the web application and manage routes.
SQLite: A self-contained database used to store active transactions and the transaction history.
HTML/CSS: Used for the structure and styling of the user interface.
Bootstrap: For responsive design and basic styling.
