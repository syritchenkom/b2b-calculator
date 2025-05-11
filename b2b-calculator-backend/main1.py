# FastAPI framework for building APIs / FastAPI фреймворк для створення API
from typing import Optional
import re
from bs4 import BeautifulSoup
# from fastapi import FastAPI, HTTPException, requests
from fastapi import FastAPI, HTTPException
import requests
# BaseModel is used to define request schemas / BaseModel використовується для опису схем запитів
from pydantic import BaseModel
# Import CORSMiddleware
from fastapi.middleware.cors import CORSMiddleware

# Create FastAPI app / Створення застосунку FastAPI
app = FastAPI(title="Kalkulator składek B2B (Polska)")

# === Налаштування CORS ===
# Список джерел (origins), яким дозволено робити запити.
# Для розробки можна дозволити джерело Vite (зазвичай http://localhost:5173)
# Або використати "*" для дозволу всіх джерел (менш безпечно для продакшену)
origins = [
    "http://localhost:5173",  # Стандартний порт Vite
    "http://127.0.0.1:5173",
    # Додайте сюди адресу вашого frontend'у, якщо він буде на іншому порту/домені
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Дозволені джерела
    allow_credentials=True,  # Дозволити кукі (якщо потрібно)
    allow_methods=["*"],    # Дозволити всі методи (GET, POST, etc.)
    allow_headers=["*"],    # Дозволити всі заголовки
)
# === Кінець налаштування CORS ===

# Request schema: monthly income and optional tax discount
# Схема запиту: щомісячний дохід та опціональна податкова знижка


class QuotaInput(BaseModel):
    income: float  # Monthly income in PLN / Місячний дохід у злотих
    forma_opodatkowania: str  # "ryczalt_15", "ryczalt_12", "liniowy_19", "skala"
    stawka_vat: float = 0.0
    # Whether user has PIT discount / Чи має користувач податкову пільгу
    has_tax_discount: bool = False


@app.post("/oblicz")  # Translated endpoint name / Назва маршруту польською
# Function to calculate Polish taxes / Функція для обчислення польських податків
# Обчислює ZUS, PIT та składkę zdrowotną на основі доходу користувача
def calculate_polish_taxes(data: QuotaInput):
    if data.income < 0:
        # Error if income is negative / Помилка, якщо дохід від'ємний
        raise HTTPException(
            status_code=400, detail="Dochód nie może być ujemny")

    # 👉 Fixed contributions for Polish B2B (example values from 2024)
    # Фіксовані ставки для самозайнятих у Польщі (дані орієнтовні, 2024 р.)
    # Base social insurance (ZUS) in PLN / Основний соціальний внесок ZUS
    zus = 1600.0
    pit_rate = 0.12  # PIT (standard 12%) / Податок PIT (стандартна ставка 12%)
    health_rate = 0.09  # Health contribution / Внесок на медичне страхування

    # Визначення ставки податку в залежності від форми оподаткування
    if data.forma_opodatkowania == "ryczalt_15":
        pit_rate = 0.15
    elif data.forma_opodatkowania == "ryczalt_12":
        pit_rate = 0.12
    elif data.forma_opodatkowania == "liniowy_19":
        pit_rate = 0.19
    elif data.forma_opodatkowania == "skala":
        if data.income <= 120000:
            pit_rate = 0.12111
        else:
            pit_rate = 0.32
    else:
        raise HTTPException(
            status_code=400, detail="Nieprawidłowa forma opodatkowania")

    # 👉 Calculate PIT / Розрахунок PIT
    pit = data.income * pit_rate
    if data.has_tax_discount:
        pit *= 0.5  # Apply 50% tax relief / Застосування пільги 50%

    # 👉 Calculate health insurance / Розрахунок медичного внеску
    health = data.income * health_rate

    # Вирахування VAT
    vat_amount = data.income * (data.stawka_vat / 100)

    # 👉 Total monthly burden / Підсумкове податкове навантаження на місяць
    total_tax = zus + pit + health + vat_amount

    return {
        "ZUS": zus,
        "Podatek PIT": round(pit, 2),
        "Składka zdrowotna": round(health, 2),
        "VAT": round(vat_amount, 2),
        "Całkowite składki": round(total_tax, 2)
    }


class SalaryResponse(BaseModel):
    year: int
    avg_salary: Optional[int] = None
    zus_base: Optional[float] = None


def fetch_avg_salary():
    salaryYear = 2025
    patternTextMinimal = rf"Kwota\s+prognozowanego\s+przeciętnego\s+wynagrodzenia\s+w\s+{salaryYear}\s+roku\s+wynosi\s+([\d\s.]+)\s*zł\.?"
    url = f"https://www.zus.pl/-/nowe-wysoko%C5%9Bci-sk%C5%82adek-na-ubezpieczenia-spo%C5%82eczne-w-{salaryYear}-r.?p_l_back_url=%2Fwyniki-wyszukiwania%3Fquery%3Dkwota%2Bprognozowanego%2Bprzeci%25C4%2599tnego%2Bwynagrodzenia%26dateFrom%3D%26dateTo%3D"
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print("Error fetching data: ", e)
        return SalaryResponse(year=salaryYear)

    soup = BeautifulSoup(response.text, 'html.parser')

    patternMinimal = re.compile(
        patternTextMinimal, re.IGNORECASE
    )
    # pattern = r'prognozowan[aej]* .*? wynagrodzen[aiy]* .*?(\d[\d\s]*)'
    # print("pattern: ", pattern)
    for tag in soup.find_all(['p', 'strong']):
        text = tag.get_text(strip=True).replace('\xa0', ' ')
        match = patternMinimal.search(text)
        if match:
            try:
                # Видаляємо пробіли та крапки для перетворення в int
                salary_str = match.group(1).replace(" ", "").replace(".", "")
                salary = int(salary_str)
                # Оскільки ми знайшли мінімальну зарплату, а не середню,
                # ви можете або повернути її, або змінити назву поля в SalaryResponse
                return SalaryResponse(year=salaryYear, avg_salary=salary)
            except ValueError:
                continue
    print("No match found for minimal salary.")
    # або return None, залежно від бажаної поведінки
    return SalaryResponse(year=salaryYear)


@app.get("/srednia_zus", response_model=SalaryResponse)
def get_avg_salary():
    result = fetch_avg_salary()
    if result.avg_salary is not None:
        # База ZUS рахується від середньої, тому це може бути некоректно для мінімальної
        result.zus_base = round(result.avg_salary * 0.6, 2)
    return result
