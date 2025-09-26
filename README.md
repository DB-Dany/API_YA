# API_YA

**Тесты для Яндекс.Диск REST API**  
Набор автотестов для проверки работы REST API Яндекс.Диска, specifically для операций с папками.

📋 **Описание**  
Проект содержит unit-тесты и интеграционные тесты, проверяющие:

- Создание папок на Яндекс.Диске

- Обработку различных сценариев (успешные и ошибочные)

- Полный жизненный цикл работы с папками

**Описание тестов:**  
Положительные тесты:  

- test_01_create_folder_success - успешное создание папки

- test_06_create_folder_nested_success - создание вложенной папки

- test_07_get_folder_info_success - получение информации о папке

- test_full_folder_lifecycle - полный цикл работы с папкой

Отрицательные тесты:

- test_02_create_folder_already_exists - попытка создать существующую папку

- test_03_create_folder_unauthorized - запрос без авторизации

- test_04_create_folder_invalid_name - некорректное имя папки

- test_05_create_folder_invalid_token - неверный токен

- test_08_create_folder_empty_name - пустое имя папки
