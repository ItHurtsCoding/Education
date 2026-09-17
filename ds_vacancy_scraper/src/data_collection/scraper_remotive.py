import requests
import csv
import time
import os

def parse_remotive_api(category="data"):
    """
    Парсер открытого API Remotive (международные удаленные вакансии).
    Отличный источник реальных зарплат (в USD) без строгих блокировок.
    """
    print(f"Сбор данных с Remotive API (категория: {category})...")
    url = f"https://remotive.com/api/remote-jobs?category={category}"
    
    results = []
    
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        vacancies = data.get("jobs", [])
        print(f"Найдено {len(vacancies)} вакансий.")
        
        for v in vacancies:
            company = v.get("company_name", "Не указана")
            
            # В Remotive все вакансии удаленные
            work_format = "Удаленная работа"
            
            # Извлекаем навыки/теги
            tags = v.get("tags", [])
            requirements = ", ".join(tags) if tags else "Не указаны"
            
            # Парсим зарплату (Она приходит в формате строки, например "$70k - $100k" или "£50k")
            salary_str = v.get("salary", "")
            salary_num = None
            if salary_str:
                # Пытаемся извлечь числа (очень грубая оценка для учебного проекта)
                import re
                nums = re.findall(r'\d+', salary_str)
                if nums:
                    nums = [int(n) * 1000 for n in nums] # Переводим "70k" в 70000
                    
                    if len(nums) == 2:
                        salary_num = sum(nums) / 2
                    else:
                        salary_num = nums[0]
                        
                    # Так как это в основном USD, переводим в рубли (курс условно 95)
                    # В реальном проекте мы бы использовали API курсов валют
                    if "$" in salary_str or "USD" in salary_str:
                        salary_num *= 95
                    elif "£" in salary_str:
                        salary_num *= 115
                    elif "€" in salary_str:
                        salary_num *= 105
                    else:
                        # Если валюта не понятна, предположим USD по умолчанию
                        salary_num *= 95 
            
            # Оставляем только те вакансии, где удалось спарсить зарплату
            if salary_num:
                results.append({
                    "company": company,
                    "work_format": work_format,
                    "requirements": requirements,
                    "salary_num": int(salary_num)
                })
                
    except Exception as e:
        print(f"Ошибка при запросе к Remotive API: {e}")
        
    return results

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    data_dir = os.path.join(base_dir, 'data', 'raw')
    os.makedirs(data_dir, exist_ok=True)
    
    real_vacancies = parse_remotive_api("data")
    
    if real_vacancies:
        keys = ["company", "work_format", "requirements", "salary_num"]
        filename = os.path.join(data_dir, "remotive_real_vacancies.csv")
        
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(real_vacancies)
            
        print(f"\nУСПЕХ! Сохранено {len(real_vacancies)} вакансий с РЕАЛЬНЫМИ зарплатами в {filename}")
    else:
        print("Вакансии с зарплатами не найдены.")

if __name__ == "__main__":
    main()
