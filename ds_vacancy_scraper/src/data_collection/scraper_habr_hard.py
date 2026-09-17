import requests
import csv
import time
import re
import os

def parse_habr_hard():
    """
    Жёсткий парсинг Хабр Карьеры по конкретным DS/ML направлениям.
    Соберет МАКСИМУМ доступных вакансий и вытащит реальные зарплаты.
    """
    queries = [
        "Data Scientist", 
        "Machine Learning", 
        "ML Engineer", 
        "Data Analyst", 
        "Computer Vision", 
        "NLP"
    ]
    
    url = "https://career.habr.com/api/frontend/vacancies"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json, text/plain, */*"
    }
    
    results = []
    seen_ids = set() # Чтобы избежать дубликатов, если вакансия попадёт в 2 запроса
    
    for query in queries:
        print(f"\nПоиск по направлению: {query}...")
        page = 1
        
        while True:
            params = {
                "q": query,
                "type": "all",
                "page": page
            }
            
            try:
                response = requests.get(url, params=params, headers=headers, timeout=10)
                response.raise_for_status()
                data = response.json()
                
                vacancies = data.get("list", [])
                if not vacancies:
                    break # Конец страниц для этого запроса
                    
                for v in vacancies:
                    vac_id = v.get("id")
                    if vac_id in seen_ids:
                        continue
                    seen_ids.add(vac_id)
                    
                    # 1. Компания
                    company = v.get("company", {}).get("title", "Не указана")
                    
                    # 2. Формат работы
                    is_remote = v.get("isRemote")
                    work_format = "Удаленная работа" if is_remote else "Офис / Гибрид"
                    
                    # 3. Требования (Навыки)
                    skills = v.get("skills") or []
                    requirements = ", ".join([s.get("title", "") for s in skills]) if skills else "Не указаны"
                    
                    # 4. Зарплата (РЕАЛЬНАЯ, парсим из JSON Хабра)
                    salary_num = None
                    salary_data = v.get("salary")
                    if salary_data:
                        sal_from = salary_data.get("from")
                        sal_to = salary_data.get("to")
                        currency = salary_data.get("currency", "RUR")
                        
                        if sal_from and sal_to:
                            salary_num = (sal_from + sal_to) / 2
                        elif sal_from:
                            salary_num = sal_from
                        elif sal_to:
                            salary_num = sal_to
                            
                        # Перевод в рубли, если указано в валюте (грубая оценка)
                        if salary_num:
                            if currency == "USD":
                                salary_num *= 95
                            elif currency == "EUR":
                                salary_num *= 105
                    
                    # Захар просил только 4 колонки (без Названия, города, сорса)
                    results.append({
                        "company": company,
                        "work_format": work_format,
                        "requirements": requirements,
                        "salary_num": int(salary_num) if salary_num else "" # Пустые оставим как "", чтобы не терять стек навыков
                    })
                    
                print(f"Собрана страница {page} ({len(vacancies)} вакансий)...")
                page += 1
                time.sleep(1) # Уважение к серверу
                
            except Exception as e:
                print(f"Ошибка при парсинге страницы {page}: {e}")
                break
                
    return results

def main():
    print("Запуск жёсткого парсера Хабр Карьеры...")
    vacancies = parse_habr_hard()
    
    if vacancies:
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        data_dir = os.path.join(base_dir, 'data', 'raw')
        filename = os.path.join(data_dir, "habr_real_ds.csv")
        
        keys = ["company", "work_format", "requirements", "salary_num"]
        
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(vacancies)
            
        print(f"\nУСПЕХ! Собрано {len(vacancies)} уникальных вакансий.")
        print(f"Файл сохранен: {filename}")
        
        # Посмотрим, сколько из них имеют реальную зарплату
        with_salary = [v for v in vacancies if v["salary_num"]]
        print(f"Из них с указанной зарплатой: {len(with_salary)} вакансий.")
    else:
        print("Не удалось найти вакансии.")

if __name__ == "__main__":
    main()
