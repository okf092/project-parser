import requests
import csv
import time
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from collections import Counter
import plotly.express as px

# URL для поиска вакансий
URL_VACANCIES = 'https://api.hh.ru/vacancies'

# Список специальностей
specialties = [
    "Архитектор", 
    "Реставратор", 
    "Дизайнер", 
    "Строитель"
]

# Список для хранения всех вакансий
vacancies_data = []

# Основной цикл по специальностям
for specialty in specialties:
    print(f"Собираем информацию по специальности: {specialty}")
    
    page = 0
    while True:
        params = {
            'text': specialty,
            'page': page,
            'per_page': 100  # Количество вакансий на странице (дефолт 10, максимум 100)
        }
        
        # Отправляем запрос с использованием сессии
        with requests.Session() as session:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
            }

            response = session.get(URL_VACANCIES, params=params, headers=headers)
            data = response.json()
            
            # Проверяем, есть ли данные вакансий для обработки
            if 'items' not in data or not data['items']:
                break
            
            for item in data['items']:
                vacancy_id = item['id']  # Получаем ID вакансии
                vacancy_name = item['name']
                employer_name = item['employer']['name'] if 'employer' in item and 'name' in item['employer'] else 'Неизвестно'
                url = item['alternate_url']
                
                # Подробный запрос на вакансию
                vacancy_detail_response = session.get(f"{URL_VACANCIES}/{vacancy_id}", headers=headers)
                vacancy_detail_data = vacancy_detail_response.json()
                
                # Извлечение ключевых навыков
                key_skills = vacancy_detail_data.get('key_skills', [])
                if not key_skills:  # Пропускать вакансии без ключевых навыков
                    continue

                skills = ', '.join([skill['name'] for skill in key_skills])
                
                # Сохранение данных о вакансии
                vacancy_info = {
                    'specialty': specialty,
                    'vacancy_name': vacancy_name,
                    'employer_name': employer_name,
                    'url': url,
                    'key_skills': skills
                }
                
                vacancies_data.append(vacancy_info)  # Добавляем в общий список

            print(f"Обработана страница {page + 1} для специальности: {specialty}")
            page += 1

# Сохранение в CSV файл
csv_file_fields = ['specialty', 'vacancy_name', 'employer_name', 'url', 'key_skills']

with open('vacancies.csv', 'w', encoding='utf-8', newline='') as csv_file:
    writer = csv.DictWriter(csv_file, fieldnames=csv_file_fields)
    writer.writeheader()  # Записываем заголовки
    writer.writerows(vacancies_data)  # Записываем данные

print("Данные успешно сохранены в файл vacancies.csv.")
