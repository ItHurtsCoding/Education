import requests
from bs4 import BeautifulSoup
import csv
import time

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*"
}

def parse_habr_api(query):
    print(f"Парсинг Habr Career API по запросу: {query}...")
    url = "https://career.habr.com/api/frontend/vacancies"
    params = {
        "q": query,
        "type": "all"
    }
    
    results = []
    try:
        response = requests.get(url, params=params, headers=HEADERS, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        vacancies = data.get("list", [])
        for v in vacancies:
            title = v.get("title", "")
            company = v.get("company", {}).get("title", "Не указана")
            link = "https://career.habr.com" + v.get("href", "")
            
            salary_info = "Не указана"
            salary = v.get("salary")
            if salary:
                salary_info = salary.get("formatted", "Не указана")
            
            locations = v.get("locations", [])
            city_list = [loc.get("title") for loc in locations if loc.get("type") == "city"]
            city = ", ".join(city_list) if city_list else "Не указан"
            
            is_remote = v.get("isRemote")
            work_format = "Удаленная работа" if is_remote else "Офис / Гибрид"
            
            skills = v.get("skills", [])
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
    except Exception as e:
        print(f"Ошибка при парсинге Habr Career: {e}")
        
    return results

def parse_remotive(query):
    print(f"Парсинг Remotive API по запросу: {query}...")
    url = "https://remotive.com/api/remote-jobs"
    params = {
        "search": query,
        "category": "data"
    }
    
    results = []
    try:
        response = requests.get(url, params=params, headers=HEADERS, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        jobs = data.get("jobs", [])
        for job in jobs:
            results.append({
                "source": "Remotive.com",
                "title": job.get("title", ""),
                "company": job.get("company_name", "Не указана"),
                "city": job.get("candidate_required_location", "Anywhere"),
                "work_format": "Удаленная работа",
                "requirements": ", ".join(job.get("tags", [])),
                "salary": job.get("salary") or "Не указана",
                "link": job.get("url", "")
            })
    except Exception as e:
        print(f"Ошибка при парсинге Remotive: {e}")
        
    return results

def parse_geekjob(query):
    print(f"Парсинг GeekJob.ru по запросу: {query}...")
    url = "https://geekjob.ru/vacancies"
    params = {
        "qs": query
    }
    
    results = []
    try:
        response = requests.get(url, params=params, headers=HEADERS, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        
        cards = soup.find_all("div", class_="vacancy-item")
        for card in cards:
            title_elem = card.find("a", class_="title")
            if not title_elem:
                continue
            title = title_elem.text.strip()
            link = "https://geekjob.ru" + title_elem["href"]
            
            company_elem = card.find("div", class_="company-name")
            company = company_elem.text.strip() if company_elem else "Не указана"
            
            location_elem = card.find("span", class_="location")
            city = location_elem.text.strip() if location_elem else "Не указан"
            
            tags_elem = card.find("div", class_="tags")
            tags = tags_elem.text.strip().split("\n") if tags_elem else []
            tags = [t.strip() for t in tags if t.strip()]
            
            work_format = "Не указан"
            if "Удаленная работа" in tags or "удаленка" in [t.lower() for t in tags]:
                work_format = "Удаленная работа"
            elif "Офис" in tags:
                work_format = "Офис"
                
            requirements = ", ".join(tags) if tags else "Не указаны"
            
            salary_elem = card.find("span", class_="salary")
            salary = salary_elem.text.strip() if salary_elem else "Не указана"
            
            results.append({
                "source": "GeekJob.ru",
                "title": title,
                "company": company,
                "city": city,
                "work_format": work_format,
                "requirements": requirements,
                "salary": salary,
                "link": link
            })
    except Exception as e:
        print(f"Ошибка при парсинге GeekJob: {e}")
        
    return results

def main():
    queries = [
        "Data Science Intern",
        "Data Science Junior"
    ]
    
    all_vacancies = []
    
    for q in queries:
        all_vacancies.extend(parse_habr_api(q))
        all_vacancies.extend(parse_remotive(q))
        all_vacancies.extend(parse_geekjob(q))
        time.sleep(2)
        
    unique_vacancies = {v['link']: v for v in all_vacancies if v.get('link')}.values()
    
    if unique_vacancies:
        keys = ["source", "title", "company", "city", "work_format", "requirements", "salary", "link"]
        filename = "ds_junior_advanced.csv"
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(unique_vacancies)
        print(f"Успешно сохранено {len(unique_vacancies)} вакансий в {filename}")
    else:
        print("Вакансии не найдены.")

if __name__ == "__main__":
    main()
