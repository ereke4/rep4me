import socket
import ssl
import sqlite3
import pyttsx3

# Конфигурация
DB_PATH = 'example.db'
CERT_FILE = "server_cert.pem"
KEY_FILE = "private_key.pem"
HOST, PORT = 'localhost', 9637

def speak_text(text):
    """Озвучивает текст с помощью pyttsx3."""
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def execute_query(query, params=(), fetch=False):
    """Выполняет запрос к SQLite и возвращает результаты при необходимости."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            if fetch:
                return cursor.fetchall()
            conn.commit()
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        return None

def create_table_if_not_exists():
    """Создаёт таблицу users, если она не существует."""
    query = """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age INTEGER NOT NULL
    );
    """
    execute_query(query)

def handle_client_request(request):
    """Обрабатывает запрос клиента."""
    if request == "GET_USERS":
        users = execute_query("SELECT * FROM users", fetch=True)
        if users:
            response = "\n".join([f"ID: {user[0]}, Имя: {user[1]}, Возраст: {user[2]}" for user in users])
        else:
            response = "No users found."
    elif request.startswith("ADD_USER"):
        try:
            _, name, age = request.split(" ", 2)
            execute_query("INSERT INTO users (name, age) VALUES (?, ?)", (name, int(age)))
            response = f"User {name} added successfully."
        except ValueError:
            response = "Invalid ADD_USER format. Use: ADD_USER <name> <age>"
    elif request.startswith("DELETE_USER"):
        try:
            _, user_id = request.split(" ", 1)
            execute_query("DELETE FROM users WHERE id = ?", (int(user_id),))
            response = f"User with ID {user_id} deleted."
        except ValueError:
            response = "Invalid DELETE_USER format. Use: DELETE_USER <id>"
    else:
        response = "Invalid command. Supported: GET_USERS, ADD_USER <name> <age>, DELETE_USER <id>"
    return response

def start_server():
    """Запуск SSL-сервера."""
    create_table_if_not_exists()

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            context.load_cert_chain(certfile=CERT_FILE, keyfile=KEY_FILE)
            server_socket = context.wrap_socket(server_socket, server_side=True)
            server_socket.bind((HOST, PORT))
            server_socket.listen(5)
            print(f"Server started on {HOST}:{PORT}")

            while True:
                conn, addr = server_socket.accept()
                print(f"Connected to client: {addr}")
                with conn:
                    while (data := conn.recv(1024)):
                        request = data.decode().strip()
                        print(f"Request from client: {request}")
                        response = handle_client_request(request)
                        conn.sendall(response.encode())
    except Exception as e:
        print(f"Error in server: {e}")

if __name__ == "__main__":
    start_server()
