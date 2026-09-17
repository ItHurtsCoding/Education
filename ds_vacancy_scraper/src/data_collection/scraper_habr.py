import requests
import csv
import time

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*"
}

def parse_habr_api(query, qualifications):
    print(f"Парсинг Habr Career API по запросу: '{query}'...")
    url = "https://career.habr.com/api/frontend/vacancies"
    
    results = []
    page = 1
    max_pages = 10 # to ensure we get enough vacancies if available
    
    while page <= max_pages:
        params = {
            "q": query,
            "type": "all",
            "page": page
        }
        # 1=Intern, 2=Junior, 3=Middle, 4=Senior, 5=Lead, 6=Director
        for qual in qualifications:
            params.setdefault("qualifications[]", []).append(qual)
            
        try:
            response = requests.get(url, params=params, headers=HEADERS, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            vacancies = data.get("list", [])
            if not vacancies:
                break # no more pages
                
            for v in vacancies:
                title = v.get("title", "")
                company = v.get("company", {}).get("title", "Не указана")
                link = "https://career.habr.com" + v.get("href", "")
                
                salary_info = "Не указана"
                salary = v.get("salary")
                if salary:
                    salary_info = salary.get("formatted", "Не указана")
                
                locations = v.get("locations") or []
                city_list = [loc.get("title") for loc in locations if loc.get("type") == "city"]
                city = ", ".join(city_list) if city_list else "Не указан"
                
                is_remote = v.get("isRemote")
                work_format = "Удаленная работа" if is_remote else "Офис / Гибрид"
                
                skills = v.get("skills") or []
                requirements = ", ".join([s.get("title", "") for s in skills]) if skills else "Не указаны"
                
                results.append({
                    "source": "Habr Career",
                    "title": title,
                    "company": company,
                    "city": city,
                    "work_format": work_format,
                    "requirements": requirements,
                    "salary": salary_info,
                    "link": link
                })
                
            # If total items < per page * page, we reached the end
            # We don't know pagination exactly from JSON unless there's a meta field, so we just check if it's empty in next loop
            
        except Exception as e:
            print(f"Ошибка при парсинге Habr Career на странице {page}: {e}")
            break
            
        page += 1
        time.sleep(1) # delay between pages
        
    return results

def main():
    # Мы ищем Data Science, но теперь для грейдов: Intern (1), Junior (2), Middle (3), Senior (4)
    query = "Data Science"
    qualifications = [1, 2, 3, 4] # Intern, Junior, Middle, Middle+ (Senior)
    
    all_vacancies = []
    
    all_vacancies.extend(parse_habr_api(query, qualifications))
    
    unique_vacancies = {v['link']: v for v in all_vacancies if v.get('link')}.values()
    
    if unique_vacancies:
        import os
        keys = ["source", "title", "company", "city", "work_format", "requirements", "salary", "link"]
        filename = os.path.join("data", "ds_vacancies_updated.csv")
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(unique_vacancies)
        print(f"Успешно сохранено {len(unique_vacancies)} вакансий в {filename}")
    else:
        print("Вакансии не найдены.")

if __name__ == "__main__":
    main()
