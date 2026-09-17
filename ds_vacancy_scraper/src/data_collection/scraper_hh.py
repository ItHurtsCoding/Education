import requests
import csv
import time
import os

def parse_hh_api(query="Data Science"):
    """
    Скрипт для парсинга реальных вакансий с открытого API HeadHunter (hh.ru).
    Здесь мы получим РЕАЛЬНЫЕ зарплаты, что исправит проблему нашей ML модели.
    """
    print(f"Начинаем сбор реальных данных с HH.ru по запросу: '{query}'...")
    url = "https://api.hh.ru/vacancies"
    
    results = []
    page = 0
    max_pages = 10 # 10 страниц по 100 вакансий = 1000 вакансий (максимум для API без токена)
    
    while page < max_pages:
        params = {
            "text": query,
            "page": page,
            "per_page": 100,
            "search_field": "name", # Ищем именно в названии вакансии
            "area": 113 # 113 - Россия
        }
        
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "application/json"
            }
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            vacancies = data.get("items", [])
            if not vacancies:
                break # Вакансии закончились
                
            for v in vacancies:
                # 1. Компания
                company = v.get("employer", {}).get("name", "Не указана")
                
                # 2. Формат работы (Удаленка, офис и т.д.)
                work_format = v.get("schedule", {}).get("name", "Не указан")
                
                # 3. Требования (очищаем от HTML-тегов встроенными методами или оставляем как есть, snippet обычно чистый)
                snippet = v.get("snippet", {})
                req = str(snippet.get("requirement", ""))
                resp = str(snippet.get("responsibility", ""))
                # Убираем теги <highlighttext>
                requirements = (req + " " + resp).replace("<highlighttext>", "").replace("</highlighttext>", "")
                if requirements.strip() == "None None" or not requirements.strip():
                    requirements = "Не указаны"
                
                # 4. Зарплата (РЕАЛЬНАЯ!)
                salary_info = v.get("salary")
                salary_num = None
                if salary_info:
                    sal_from = salary_info.get("from")
                    sal_to = salary_info.get("to")
                    # Если есть и от и до - берем среднее. Иначе берем то, что есть.
                    if sal_from and sal_to:
                        salary_num = (sal_from + sal_to) / 2
                    elif sal_from:
                        salary_num = sal_from
                    elif sal_to:
                        salary_num = sal_to
                        
                    # Конвертация валюты (очень базово, для пета сойдет)
                    currency = salary_info.get("currency", "RUR")
                    if currency == "USD" and salary_num:
                        salary_num *= 95
                    elif currency == "EUR" and salary_num:
                        salary_num *= 105
                
                # По ТЗ от Захара: нам больше НЕ нужны Названия (title), город (city) и источник (source).
                # Сохраняем только самое важное.
                if salary_num: # Берем только вакансии с указанной зарплатой для ML!
                    results.append({
                        "company": company,
                        "work_format": work_format,
                        "requirements": requirements,
                        "salary_num": int(salary_num)
                    })
                    
        except Exception as e:
            print(f"Ошибка на странице {page}: {e}")
            break
            
        print(f"Собрано {len(results)} вакансий с реальной зарплатой (страница {page})...")
        page += 1
        time.sleep(0.5) # Пауза, чтобы HH не заблокировал
        
    return results

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    data_dir = os.path.join(base_dir, 'data', 'raw')
    os.makedirs(data_dir, exist_ok=True)
    
    real_vacancies = parse_hh_api("Data Science OR Machine Learning OR Data Analyst")
    
    if real_vacancies:
        keys = ["company", "work_format", "requirements", "salary_num"]
        filename = os.path.join(data_dir, "hh_real_vacancies.csv")
        
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(real_vacancies)
            
        print(f"\nУСПЕХ! Сохранено {len(real_vacancies)} вакансий с РЕАЛЬНЫМИ зарплатами в {filename}")
        print("Теперь наша модель будет учиться на настоящих данных!")
    else:
        print("Вакансии с зарплатами не найдены.")

if __name__ == "__main__":
    main()
