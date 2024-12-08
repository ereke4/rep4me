import socket
import ssl
import os
import speech_recognition as sr
import pyttsx3

def speak_text(text):
    """Озвучивает текст."""
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def save_to_history(message):
    """Сохраняет сообщение в историю."""
    with open("history.txt", "a", encoding="utf-8") as history_file:
        history_file.write(message + "\n")

def recognize_speech():
    """Преобразует речь в текст."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Говорите...")
        try:
            audio = recognizer.listen(source, timeout=5)
            text = recognizer.recognize_google(audio, language="ru-RU")
            return text  # Возвращаем распознанный текст
        except sr.UnknownValueError:
            print("Речь не распознана.")
        except sr.RequestError:
            print("Ошибка соединения с сервисом распознавания.")
    return None  # Если не удалось распознать, возвращаем None

def start_client():
    host = 'localhost'
    port = 9637
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    context.load_verify_locations('server_cert.pem')
    secure_socket = context.wrap_socket(client_socket, server_hostname=host)

    try:
        secure_socket.connect((host, port))
        print("Подключение к серверу установлено.")

        while True:
            print("\nВыберите действие:")
            print("1. Отправить сообщение (текстовый ввод)")
            print("2. Отправить сообщение (голосовой ввод)")
            print("3. Показать историю сообщений")
            print("4. Выйти")
            choice = input("Введите 1, 2, 3 или 4: ")

            if choice == "1":
                print("\nВыберите команду:")
                print("1. Получить список пользователей (GET_USERS)")
                print("2. Добавить нового пользователя (ADD_USER)")
                print("3. Удалить пользователя (DELETE_USER)")
                cmd_choice = input("Введите 1, 2 или 3: ")

                if cmd_choice == "1":
                    message = "GET_USERS"
                elif cmd_choice == "2":
                    name = input("Введите имя пользователя: ")
                    age = input("Введите возраст пользователя: ")
                    message = f"ADD_USER {name} {age}"
                elif cmd_choice == "3":
                    user_id = input("Введите ID пользователя для удаления: ")
                    message = f"DELETE_USER {user_id}"
                else:
                    print("Неверный выбор.")
                    continue

                secure_socket.sendall(message.encode())
                response = secure_socket.recv(1024)
                print(f"Ответ от сервера: {response.decode()}")
                save_to_history(f"Сообщение серверу: {message}")

            elif choice == "2":
                print("\nВыберите команду:")
                print("1. Получить список пользователей (GET_USERS)")
                print("2. Добавить нового пользователя (ADD_USER)")
                print("3. Удалить пользователя (DELETE_USER)")
                message = recognize_speech()
                if message:
                    if "получить список пользователей" in message.lower():
                        message = "GET_USERS"
                    elif "добавить" in message.lower():
                        print("Укажите имя")
                        name = recognize_speech()
                        if name:  # Проверяем, что имя было распознано
                            print("Укажите возраст")
                            age = recognize_speech()  # Получаем возраст
                            if age:  # Если возраст тоже распознан
                                message = f"ADD_USER {name} {age}"
                            else:
                                print("Возраст не распознан.")
                                continue
                        else:
                            print("Имя не распознано.")
                            continue
                    elif "удалить" in message.lower():
                        print("Укажите ID пользователя для удаления")
                        user_id = recognize_speech()  # Получаем ID для удаления
                        if user_id:  # Если ID распознан
                            user_id = int(user_id)
                            if user_id.isdigit():
                                message = f"DELETE_USER {user_id}"
                            else:
                                print("ID пользователя должен быть числом.")
                                continue
                        else:
                            print("ID пользователя не распознан.")
                            continue
                    else:
                        print("Команда не распознана.")
                        continue

                    secure_socket.sendall(message.encode())
                    response = secure_socket.recv(1024)
                    response_text = response.decode()

                    # Сначала выводим ответ на экран
                    print(f"Ответ от сервера: {response_text}")
                    
                    # Если нужно озвучивать, добавьте это условие
                    # Пример: озвучиваем только для голосового ввода
                    speak_text(response_text)  # Озвучиваем ответ
                    save_to_history(f"Сообщение серверу (голос): {message}")


            elif choice == "3":
                print("\nИстория сообщений:")
                if os.path.exists("history.txt"):
                    with open("history.txt", "r", encoding="utf-8") as history_file:
                        print(history_file.read())
                else:
                    print("История пуста.")

            elif choice == "4":
                print("Завершаем соединение с сервером.")
                break
            else:
                print("Неверный выбор. Попробуйте снова.")

    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        secure_socket.close()

if __name__ == "__main__":
  start_client()
