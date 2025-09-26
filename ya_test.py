import requests
import unittest
import os
from dotenv import load_dotenv

# pip install requests python-dotenv

# Загрузка переменных окружения из файла .env
load_dotenv()


class TestYandexDiskAPI(unittest.TestCase):

    def setUp(self):
        """Настройка тестовых данных"""
        self.base_url = "https://cloud-api.yandex.net/v1/disk/resources"
        self.headers = {
            "Authorization": f"OAuth {os.getenv('YANDEX_DISK_TOKEN')}",
            "Content-Type": "application/json"
        }
        self.test_folder = "test_folder"
        self.invalid_folder = "invalid/folder/name"  # Некорректное имя папки

    def tearDown(self):
        """Очистка после тестов"""
        try:
            # Удаляем тестовую папку если она существует
            requests.delete(f"{self.base_url}?path={self.test_folder}", headers=self.headers)
        except:
            pass

    def test_01_create_folder_success(self):
        """Тест успешного создания папки"""
        response = requests.put(f"{self.base_url}?path={self.test_folder}", headers=self.headers)

        # Проверка кода ответа
        self.assertEqual(response.status_code, 201,
                         f"Ожидался код 201, получен {response.status_code}. Ответ: {response.text}")

        # Проверка, что папка действительно создалась
        check_response = requests.get(f"{self.base_url}?path={self.test_folder}", headers=self.headers)
        self.assertEqual(check_response.status_code, 200, "Папка не найдена после создания")

    def test_02_create_folder_already_exists(self):
        """Тест создания папки, которая уже существует"""
        # Cоздаем папку
        requests.put(f"{self.base_url}?path={self.test_folder}", headers=self.headers)

        # Пытаемся создать снова
        response = requests.put(f"{self.base_url}?path={self.test_folder}", headers=self.headers)

        # Ошибка 409
        self.assertEqual(response.status_code, 409,
                         f"Ожидалась ошибка 409, получен {response.status_code}")

    def test_03_create_folder_unauthorized(self):
        """Тест создания папки без авторизации"""
        headers_without_auth = {"Content-Type": "application/json"}
        response = requests.put(f"{self.base_url}?path={self.test_folder}",
                                headers=headers_without_auth)

        self.assertEqual(response.status_code, 401,
                         f"Ожидалась ошибка 401, получен {response.status_code}")

    def test_04_create_folder_invalid_name(self):
        """Тест создания папки с некорректным именем"""
        response = requests.put(f"{self.base_url}?path={self.invalid_folder}",
                                headers=self.headers)

        # Может вернуться 400 или 409 в зависимости от типа ошибки
        self.assertIn(response.status_code, [400, 409],
                      f"Ожидалась ошибка 400 или 409, получен {response.status_code}")

    def test_05_create_folder_invalid_token(self):
        """Тест создания папки с неверным токеном"""
        invalid_headers = {
            "Authorization": "OAuth invalid_token_12345",
            "Content-Type": "application/json"
        }
        response = requests.put(f"{self.base_url}?path={self.test_folder}",
                                headers=invalid_headers)

        self.assertEqual(response.status_code, 401,
                         f"Ожидалась ошибка 401, получен {response.status_code}")

    def test_06_create_folder_nested_success(self):
        """Тест создания вложенной папки"""
        nested_folder = f"{self.test_folder}/nested_subfolder"
        response = requests.put(f"{self.base_url}?path={nested_folder}",
                                headers=self.headers)

        # Проверяем успешное создание
        self.assertIn(response.status_code, [201, 409],
                      f"Ожидался код 201 или 409 (если уже существует), получен {response.status_code}")

    def test_07_get_folder_info_success(self):
        """Тест получения информации о созданной папке"""
        # Создаем папку
        requests.put(f"{self.base_url}?path={self.test_folder}", headers=self.headers)

        # Получаем информацию о папке
        response = requests.get(f"{self.base_url}?path={self.test_folder}",
                                headers=self.headers)

        self.assertEqual(response.status_code, 200,
                         f"Ожидался код 200, получен {response.status_code}")

        # Проверяем, что это папка
        response_data = response.json()
        self.assertEqual(response_data["type"], "dir", "Созданный ресурс не является папкой")
        self.assertEqual(response_data["name"], self.test_folder, "Имя папки не совпадает")

    def test_08_create_folder_empty_name(self):
        """Тест создания папки с пустым именем"""
        response = requests.put(f"{self.base_url}?path=", headers=self.headers)

        self.assertEqual(response.status_code, 400,
                         f"Ожидалась ошибка 400, получен {response.status_code}")

    def test_09_create_folder_special_characters(self):
        """Тест создания папки со специальными символами"""
        special_folder = "test_folder_@#$%^&"
        response = requests.put(f"{self.base_url}?path={special_folder}",
                                headers=self.headers)

        # Проверяем, что создание прошло успешно или получили ожидаемую ошибку
        self.assertIn(response.status_code, [201, 400, 409],
                      f"Неожиданный код ответа: {response.status_code}")


class TestYandexDiskAPIIntegration(unittest.TestCase):
    """Интеграционные тесты с проверкой полного цикла"""

    def setUp(self):
        self.base_url = "https://cloud-api.yandex.net/v1/disk/resources"
        self.headers = {
            "Authorization": f"OAuth {os.getenv('YANDEX_DISK_TOKEN')}",
            "Content-Type": "application/json"
        }
        self.test_folder = "integration_test_folder"

    def tearDown(self):
        try:
            requests.delete(f"{self.base_url}?path={self.test_folder}", headers=self.headers)
        except:
            pass

    def test_full_folder_lifecycle(self):
        """Полный тест жизненного цикла папки: создание → проверка → удаление"""

        # 1. Создание папки
        create_response = requests.put(f"{self.base_url}?path={self.test_folder}",
                                       headers=self.headers)
        self.assertEqual(create_response.status_code, 201, "Ошибка при создании папки")

        # 2. Проверка существования
        check_response = requests.get(f"{self.base_url}?path={self.test_folder}",
                                      headers=self.headers)
        self.assertEqual(check_response.status_code, 200, "Папка не найдена после создания")

        # 3. Удаление папки
        delete_response = requests.delete(f"{self.base_url}?path={self.test_folder}",
                                          headers=self.headers)
        self.assertEqual(delete_response.status_code, 204, "Ошибка при удалении папки")

        # 4. Проверка, что папка удалена
        check_deleted_response = requests.get(f"{self.base_url}?path={self.test_folder}",
                                              headers=self.headers)
        self.assertEqual(check_deleted_response.status_code, 404, "Папка не была удалена")


if __name__ == "__main__":
    # Проверка наличия токена
    if not os.getenv('YANDEX_DISK_TOKEN'):
        print("Ошибка: Не найден YANDEX_DISK_TOKEN в переменных окружения")
        print("Создайте файл .env и добавьте: YANDEX_DISK_TOKEN=your_token_here")
        exit(1)

    # Запуск тестов
    unittest.main(verbosity=2)