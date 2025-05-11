# Library for making HTTP requests / Biblioteka do wykonywania żądań HTTP
import requests
# Library for regular expressions / Biblioteka do wyrażeń regularnych
import re
# Library for time-related functions (used for caching) / Biblioteka do funkcji związanych z czasem (używana do buforowania)
import time
# Library for parsing HTML / Biblioteka do parsowania HTML
from bs4 import BeautifulSoup
# Library for data validation and settings management using Python type annotations / Biblioteka do walidacji danych i zarządzania ustawieniami przy użyciu adnotacji typów Python
from pydantic import BaseModel
# For type hinting optional values / Do typowania opcjonalnych wartości
from typing import Optional

# === Data Models / Modele danych ===


class ZUSData(BaseModel):
    """Model for storing ZUS data / Model do przechowywania danych ZUS."""
    # Year the data pertains to / Rok, którego dotyczą dane
    year: int
    # Projected average salary / Prognozowane przeciętne wynagrodzenie
    avg_salary: Optional[float] = None
    # Base for social contributions (60% of avg_salary) / Podstawa wymiaru składek społecznych (60% przeciętnego wynagrodzenia)
    zus_base: Optional[float] = None
    # To store an error message if fetching fails / Do przechowywania komunikatu o błędzie, jeśli pobieranie się nie powiedzie
    error_message: Optional[str] = None


# === Cache / Pamięć podręczna (Kesz) ===
_zus_data_cache = {
    "data": None,  # Cached data object / Zbuforowany obiekt danych
    "timestamp": 0,  # Timestamp of the last update / Znacznik czasu ostatniej aktualizacji
    # Cache Time To Live in seconds (1 hour) / Czas życia pamięci podręcznej w sekundach (1 godzina)
    "ttl": 3600
}

# === Configuration / Konfiguracja ===
# Year for which we are fetching data / Rok, dla którego pobieramy dane
ZUS_INFO_YEAR = 2025
# URL template for the ZUS page containing the data / Szablon URL strony ZUS zawierającej dane
# WARNING: This URL and pattern might become outdated if ZUS changes its website structure.
# OSTRZEŻENIE: Ten URL i wzorzec mogą stać się nieaktualne, jeśli ZUS zmieni strukturę swojej strony internetowej.
ZUS_INFO_URL_TEMPLATE = "https://www.zus.pl/-/nowe-wysoko%C5%9Bci-sk%C5%82adek-na-ubezpieczenia-spo%C5%82eczne-w-{year}-r.?p_l_back_url=%2Fwyniki-wyszukiwania%3Fquery%3Dkwota%2Bprognozowanego%2Bprzeci%25C4%2599tnego%2Bwynagrodzenia%26dateFrom%3D%26dateTo%3D"
# Regular expression pattern template to find the salary text / Szablon wzorca wyrażenia regularnego do znalezienia tekstu z wynagrodzeniem
ZUS_SALARY_PATTERN_TEMPLATE = r"Kwota\s+prognozowanego\s+przeciętnego\s+wynagrodzenia\s+w\s+{year}\s+roku\s+wynosi\s+([\d\s.,]+)\s*zł\.?"
# Request timeout in seconds / Limit czasu żądania w sekundach
REQUEST_TIMEOUT = 10

# === Main Data Fetching Function / Główna funkcja pobierania danych ===


def fetch_and_cache_zus_data(force_refresh: bool = False) -> ZUSData:
    """
    Fetches and caches data about the projected average salary and ZUS base.
    Pobiera i buforuje dane o prognozowanym przeciętnym wynagrodzeniu i podstawie ZUS.

    Args:
        force_refresh: If True, ignores the cache and makes a new request. / Jeśli True, ignoruje pamięć podręczną i wykonuje nowe żądanie.

    Returns:
        ZUSData object with the fetched data or an error message. / Obiekt ZUSData z pobranymi danymi lub komunikatem o błędzie.
    """
    current_time = time.time()
    year = ZUS_INFO_YEAR

    # Check cache / Sprawdzenie pamięci podręcznej
    cached_data = _zus_data_cache.get("data")
    # Check if cache is valid / Sprawdź, czy pamięć podręczna jest ważna
    if not force_refresh and cached_data and \
       (current_time - _zus_data_cache.get("timestamp", 0) < _zus_data_cache.get("ttl", 0)):
        print(f"ZUS Fetcher: Returning cached data for {year}")
        # Return cached data if valid / Zwróć dane z pamięci podręcznej, jeśli są ważne
        return cached_data

    # If cache is invalid or force_refresh is True, fetch new data / Jeśli pamięć podręczna jest nieważna lub force_refresh jest True, pobierz nowe dane
    print(f"ZUS Fetcher: Fetching new data for {year} from zus.pl")
    # Format URL with the target year / Sformatuj URL z docelowym rokiem
    url = ZUS_INFO_URL_TEMPLATE.format(year=year)
    # Format regex pattern with the target year / Sformatuj wzorzec regex z docelowym rokiem
    pattern_text = ZUS_SALARY_PATTERN_TEMPLATE.format(year=year)
    # Compile regex for efficiency / Skompiluj regex dla wydajności
    pattern_compiled = re.compile(pattern_text, re.IGNORECASE | re.DOTALL)

    try:
        # Make the HTTP GET request / Wykonaj żądanie HTTP GET
        response = requests.get(url, timeout=REQUEST_TIMEOUT)
        # Check for HTTP errors (4xx, 5xx) / Sprawdź błędy HTTP (4xx, 5xx)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        # Handle request errors (network issues, timeouts, etc.) / Obsłuż błędy żądania (problemy sieciowe, przekroczenia limitu czasu itp.)
        error_msg = f"ZUS Fetcher: Error fetching data from URL: {e}"
        print(error_msg)
        # Return ZUSData object with error message / Zwróć obiekt ZUSData z komunikatem o błędzie
        return ZUSData(year=year, error_message=error_msg)

    # Parse the HTML content / Sparsuj zawartość HTML
    soup = BeautifulSoup(response.text, 'html.parser')
    avg_salary_found = None

    # Search for the salary text within common HTML tags / Wyszukaj tekst z wynagrodzeniem w popularnych tagach HTML
    for tag in soup.find_all(['p', 'strong', 'div', 'span']):
        # Get tag text and replace non-breaking space / Pobierz tekst tagu i zamień twardą spację
        text = tag.get_text(strip=True).replace(
            '\xa0', ' ')
        # Try to match the regex pattern / Spróbuj dopasować wzorzec regex
        match = pattern_compiled.search(text)
        if match:
            try:
                # Extract, clean (remove spaces, replace comma with dot), and convert the salary string to float
                # Wyodrębnij, wyczyść (usuń spacje, zamień przecinek na kropkę) i przekonwertuj ciąg znaków wynagrodzenia na float
                salary_str = match.group(1).replace(" ", "").replace(".", "")
                avg_salary_found = float(salary_str)
                print(
                    f"ZUS Fetcher: Found avg_salary for {year}: {avg_salary_found}")
                # Salary found, exit the loop / Znaleziono wynagrodzenie, wyjdź z pętli
                break
            except (ValueError, IndexError) as e:
                # Handle potential errors during parsing or conversion / Obsłuż potencjalne błędy podczas parsowania lub konwersji
                print(
                    f"ZUS Fetcher: Error parsing salary string '{match.group(1)}': {e}")
                # Try finding in the next tag / Spróbuj znaleźć w następnym tagu
                continue

    # If salary was successfully found and parsed / Jeśli wynagrodzenie zostało pomyślnie znalezione i sparsowane
    if avg_salary_found is not None:
        # Calculate ZUS base (60% of average salary) / Oblicz podstawę ZUS (60% przeciętnego wynagrodzenia)
        zus_base_calculated = round(avg_salary_found * 0.6, 2)
        # Create result object / Utwórz obiekt wynikowy
        result = ZUSData(year=year, avg_salary=avg_salary_found,
                         zus_base=zus_base_calculated)
        # Update cache / Zaktualizuj pamięć podręczną
        _zus_data_cache["data"] = result
        _zus_data_cache["timestamp"] = current_time
        print(f"ZUS Fetcher: Successfully fetched and cached data: {result}")
        # Return the result / Zwróć wynik
        return result
    else:
        # If salary text was not found on the page / Jeśli tekst wynagrodzenia nie został znaleziony na stronie
        error_msg = f"ZUS Fetcher: Could not find average salary data for {year} on the page."
        print(error_msg)
        # Return ZUSData object with error message / Zwróć obiekt ZUSData z komunikatem o błędzie
        return ZUSData(year=year, error_message=error_msg)
