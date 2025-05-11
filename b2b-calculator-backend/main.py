# FastAPI framework for building APIs / FastAPI framework do tworzenia API
# Import List for type hinting / Import List do typowania
from typing import Optional, List
# Import necessary FastAPI components / Import potrzebnych komponentów FastAPI
from fastapi import FastAPI, HTTPException, Depends
# BaseModel is used to define request schemas / BaseModel jest używany do definiowania schematów żądań
from pydantic import BaseModel
# Import CORSMiddleware for handling Cross-Origin Resource Sharing / Import CORSMiddleware do obsługi Cross-Origin Resource Sharing
from fastapi.middleware.cors import CORSMiddleware

# === Component Import / Import komponentów ===
# Import functions and models from the ZUS data fetching module / Import funkcji i modeli z modułu pobierania danych ZUS
from zus_data_fetcher import fetch_and_cache_zus_data, ZUSData
# === End of Import / Koniec importu ===

# Create FastAPI app / Stworzenie aplikacji FastAPI
# Set API title / Ustawienie tytułu API
app = FastAPI(title="Kalkulator składek B2B (Polska)")

# === CORS Configuration / Konfiguracja CORS ===
# List of origins allowed to make requests / Lista źródeł (origins), którym zezwolono na wysyłanie żądań
# For development, allow the Vite default port or use "*" to allow all (less secure for production)
# W celach deweloperskich można zezwolić na domyślny port Vite lub użyć "*" aby zezwolić wszystkim (mniej bezpieczne dla produkcji)
origins = [
    "http://localhost:5173",  # Standard Vite port / Standardowy port Vite
    "http://127.0.0.1:5173",
    # Add your frontend address here if it's on a different port/domain
    # Dodaj tutaj adres swojego frontendu, jeśli jest na innym porcie/domenie
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allowed origins / Dozwolone źródła
    # Allow cookies (if needed) / Zezwól na ciasteczka (jeśli potrzebne)
    allow_credentials=True,
    # Allow all methods (GET, POST, etc.) / Zezwól na wszystkie metody (GET, POST, itp.)
    allow_methods=["*"],
    allow_headers=["*"],    # Allow all headers / Zezwól na wszystkie nagłówki
)
# === End of CORS Configuration / Koniec konfiguracji CORS ===

# === API Data Models / Modele danych dla API ===


class QuotaInput(BaseModel):
    """Request schema for the calculation endpoint / Schemat żądania dla punktu końcowego obliczeń."""
    income: float  # Monthly income in PLN / Miesięczny przychód w PLN
    # Monthly costs (KUP) / Miesięczne koszty uzyskania przychodu (KUP)
    costs: float = 0.0
    # Tax form: "ryczalt_15", "ryczalt_12", "liniowy_19", "skala" / Forma opodatkowania
    forma_opodatkowania: str
    stawka_vat: float = 0.0  # VAT rate / Stawka VAT
    # Whether user has PIT discount / Czy użytkownik ma ulgę podatkową PIT
    has_tax_discount: bool = False
    # Whether user pays voluntary sickness contribution / Czy użytkownik opłaca dobrowolną składkę chorobową
    # Assume pays by default / Domyślnie zakładamy, że opłaca
    platnik_chorobowe: bool = True


class SkladkaDetail(BaseModel):
    """Details of a single ZUS contribution component / Szczegóły pojedynczej składowej składki ZUS."""
    nazwa: str      # Contribution name / Nazwa składki
    procent: float  # Percentage rate / Stawka procentowa
    podstawa: float  # Calculation base / Podstawa wymiaru
    kwota: float    # Calculated amount / Obliczona kwota


class QuotaOutput(BaseModel):
    """Response structure for the calculator / Struktura odpowiedzi kalkulatora."""
    rok_danych_zus: int  # Year of the ZUS data used / Rok danych ZUS użytych do obliczeń
    # ZUS contribution base (can be None on error) / Podstawa wymiaru składek ZUS (może być None w przypadku błędu)
    podstawa_wymiaru_skladek_zus: Optional[float]
    # Detailed list of social ZUS contributions / Szczegółowa lista składek ZUS społecznych
    zus_spoleczne_details: List[SkladkaDetail]
    # Total social ZUS contributions / Suma składek ZUS społecznych
    zus_spoleczne_total: float
    # Health insurance contribution (currently simplified) / Składka na ubezpieczenie zdrowotne (obecnie uproszczona)
    skladka_zdrowotna: float
    podatek_pit: float  # Income tax (PIT) / Podatek dochodowy (PIT)
    vat: float  # VAT amount / Kwota VAT
    # Total burden (zus_total + health + pit) / Całkowite obciążenie (ZUS społeczny + zdrowotna + PIT)
    calkowite_obciazenie: float
    # Net income (income - costs - total burden) / Dochód netto (przychód - koszty - całkowite obciążenie)
    dochod_netto: float
    # List of warnings (e.g., about simplifications) / Lista ostrzeżeń (np. o uproszczeniach)
    ostrzezenia: List[str] = []
    # Error message if fetching ZUS data failed / Komunikat błędu, jeśli pobieranie danych ZUS nie powiodło się
    blad_danych_zus: Optional[str] = None

# === FastAPI Dependency for ZUS Data / Zależność FastAPI dla danych ZUS ===


async def get_zus_dependency() -> ZUSData:
    """
    Dependency to get ZUS data, ensuring it's fetched if needed.
    Zależność do pobierania danych ZUS, zapewniająca ich pobranie w razie potrzeby.
    """
    zus_info = fetch_and_cache_zus_data()
    # Don't raise an error here, pass the data as is
    # The endpoint can handle the situation (e.g., show an error to the user)
    # Nie zgłaszamy tutaj błędu, przekazujemy dane jakie są
    # Punkt końcowy może obsłużyć sytuację (np. pokazać błąd użytkownikowi)
    return zus_info

# === API Endpoints / Punkty końcowe API ===


# Define POST endpoint and response model / Definiuj punkt końcowy POST i model odpowiedzi
@app.post("/oblicz", response_model=QuotaOutput)
# Function to calculate Polish taxes / Funkcja do obliczania polskich podatków
# Calculates ZUS, PIT, and health contribution based on user input / Oblicza ZUS, PIT i składkę zdrowotną na podstawie danych wejściowych użytkownika
# Inject ZUS data dependency / Wstrzyknij zależność danych ZUS
async def calculate_polish_taxes(data: QuotaInput, zus_info: ZUSData = Depends(get_zus_dependency)):
    # Input validation / Walidacja danych wejściowych
    if data.income < 0:
        # Error if income is negative / Błąd, jeśli przychód jest ujemny
        raise HTTPException(
            status_code=400, detail="Dochód (przychód) nie może być ujemny")  # Income cannot be negative
    if data.costs < 0:
        # Error if costs are negative / Błąd, jeśli koszty są ujemne
        raise HTTPException(
            status_code=400, detail="Koszty nie mogą być ujemne")  # Costs cannot be negative
    # Consider warning if costs exceed income / Rozważ ostrzeżenie, jeśli koszty przekraczają przychód
    if data.income < data.costs:
        # For now, just calculate, but this might be unrealistic
        # Na razie po prostu obliczamy, ale może to być nierealistyczne
        pass

    # === Social ZUS Calculation / Obliczenie ZUS Społecznego ===
    zus_details = []  # List to store details of each contribution / Lista do przechowywania szczegółów każdej składki
    zus_total = 0.0  # Total social ZUS / Suma ZUS społecznego
    warnings = []  # List for calculation warnings / Lista na ostrzeżenia dotyczące obliczeń
    # Get ZUS base from dependency / Pobierz podstawę ZUS z zależności
    zus_base = zus_info.zus_base

    # Handle case where ZUS base couldn't be fetched / Obsługa przypadku, gdy nie udało się pobrać podstawy ZUS
    if zus_base is None:
        warnings.append(
            "Nie udało się pobrać aktualnej podstawy ZUS. Użyto wartości domyślnych/zerowych.")  # Failed to fetch current ZUS base. Using default/zero values.
        # Set a default base or keep 0, depending on desired logic / Ustaw domyślną podstawę lub zostaw 0, w zależności od pożądanej logiki
        zus_base = 0.0  # Or another default value / Lub inna wartość domyślna

    # Calculate contributions if base is valid / Oblicz składki, jeśli podstawa jest prawidłowa
    if zus_base > 0:
        # ZUS rates (may change, especially 'Wypadkowe') / Stawki ZUS (mogą ulec zmianie, zwłaszcza 'Wypadkowe')
        rates = {
            "Emerytalne": 0.1952,  # Pension / Emerytalne
            "Rentowe": 0.0800,  # Disability / Rentowe
            # Accident (standard rate, may vary) / Wypadkowe (standardowa stawka, może się różnić)
            "Wypadkowe": 0.0167,
            # Labor Fund/Solidarity Fund / Fundusz Pracy/Solidarnościowy
            "Fundusz Pracy/Solidarnościowy": 0.0245,
        }
        # Add voluntary sickness contribution if applicable / Dodaj dobrowolną składkę chorobową, jeśli dotyczy
        if data.platnik_chorobowe:
            # Sickness (voluntary) / Chorobowe (dobrowolne)
            rates["Chorobowe (dobrowolne)"] = 0.0245

        # Calculate each component / Oblicz każdą składową
        for name, rate in rates.items():
            # Calculate amount / Oblicz kwotę
            amount = round(zus_base * rate, 2)
            zus_details.append(SkladkaDetail(
                nazwa=name, procent=rate * 100, podstawa=zus_base, kwota=amount))  # Add details to list / Dodaj szczegóły do listy
            zus_total += amount  # Add to total / Dodaj do sumy

        zus_total = round(zus_total, 2)  # Round the total / Zaokrąglij sumę

    # === Health Contribution Calculation (SIMPLIFIED!) / Obliczenie Składki Zdrowotnej (UPROSZCZONE!) ===
    # !!! WARNING: This is a highly simplified and likely INCORRECT calculation for most forms!
    # !!! OSTRZEŻENIE: To jest bardzo uproszczone i prawdopodobnie NIEPOPRAWNE obliczenie dla większości form!
    health_contribution = 0.0
    przychody = data.income  # Revenue / Przychód
    koszty = data.costs  # Costs / Koszty
    # Preliminary base for health contribution (not always correct) / Wstępna podstawa składki zdrowotnej (nie zawsze poprawna)
    # Income for health insurance base / Dochód do podstawy zdrowotnej
    dochod_do_zdrowotnej = max(0, przychody - koszty - zus_total)

    # Calculate based on tax form / Oblicz na podstawie formy opodatkowania
    if data.forma_opodatkowania == "skala":  # Tax scale / Skala podatkowa
        health_rate_simplified = 0.09  # Simplified rate / Uproszczona stawka
        health_contribution = round(
            dochod_do_zdrowotnej * health_rate_simplified, 2)
        # TODO: Add check for minimum health contribution base / TODO: Dodaj sprawdzenie minimalnej podstawy składki zdrowotnej
        warnings.append(
            "Składka zdrowotna (skala) obliczona wg uproszczonej stawki 9% od dochodu (przychód - koszty - ZUS społ.).")  # Health contribution (scale) calculated using simplified 9% rate of income (revenue - costs - social ZUS).
    elif data.forma_opodatkowania == "liniowy_19":  # Flat tax / Podatek liniowy
        health_rate_simplified = 0.049  # Simplified rate / Uproszczona stawka
        health_contribution = round(
            dochod_do_zdrowotnej * health_rate_simplified, 2)
        # TODO: Add check for minimum health contribution base / TODO: Dodaj sprawdzenie minimalnej podstawy składki zdrowotnej
        warnings.append(
            "Składka zdrowotna (liniowy) obliczona wg uproszczonej stawki 4.9% od dochodu (przychód - koszty - ZUS społ.).")  # Health contribution (flat) calculated using simplified 4.9% rate of income (revenue - costs - social ZUS).
    # Lump sum tax / Ryczałt ewidencjonowany
    elif data.forma_opodatkowania.startswith("ryczalt"):
        # TODO: Implement lump sum logic with income thresholds and fixed rates / TODO: Zaimplementuj logikę ryczałtu z progami dochodowymi i stałymi stawkami
        health_contribution = 300.0  # Temporary placeholder / Tymczasowa wartość zastępcza
        warnings.append(
            "Składka zdrowotna (ryczałt) jest wartością tymczasową. Wymaga implementacji progów dochodowych.")  # Health contribution (lump sum) is a temporary value. Requires implementation of income thresholds.
    else:  # Unknown tax form / Nieznana forma opodatkowania
        # Unknown tax form for health contribution.
        warnings.append("Nieznana forma opodatkowania dla składki zdrowotnej.")

    # Cannot be negative / Nie może być ujemna
    health_contribution = max(0, health_contribution)

    # === PIT Calculation (SIMPLIFIED!) / Obliczenie PIT (UPROSZCZONE!) ===
    # !!! WARNING: PIT calculation is also simplified. / !!! OSTRZEŻENIE: Obliczenie PIT jest również uproszczone.
    pit_tax = 0.0  # Income tax amount / Kwota podatku dochodowego
    pit_base = 0.0  # Tax base / Podstawa opodatkowania

    # Determine tax rate and base based on tax form / Określ stawkę podatku i podstawę w zależności od formy opodatkowania
    if data.forma_opodatkowania == "ryczalt_15":
        pit_rate = 0.15
        # For lump sum, base = revenue (minus social ZUS, minus part of health - not implemented) / Dla ryczałtu podstawa = przychód (minus ZUS społ., minus część zdrowotnej - niezaimplementowane)
        pit_base = max(0, przychody - zus_total)  # Simplified / Uproszczone
        pit_tax = pit_base * pit_rate
        warnings.append(
            "PIT (ryczałt) obliczony od przychodu pomniejszonego tylko o ZUS społeczny (uproszczenie).")  # PIT (lump sum) calculated from revenue minus only social ZUS (simplification).
    elif data.forma_opodatkowania == "ryczalt_12":
        pit_rate = 0.12
        pit_base = max(0, przychody - zus_total)  # Simplified / Uproszczone
        pit_tax = pit_base * pit_rate
        warnings.append(
            "PIT (ryczałt) obliczony od przychodu pomniejszonego tylko o ZUS społeczny (uproszczenie).")  # PIT (lump sum) calculated from revenue minus only social ZUS (simplification).
    elif data.forma_opodatkowania == "liniowy_19":
        pit_rate = 0.19
        # Base = income (revenue - costs - social contributions) / Podstawa = dochód (przychód - koszty - składki społeczne)
        # TODO: Account for possible health contribution deduction / TODO: Uwzględnij możliwość odliczenia składki zdrowotnej
        pit_base = max(0, przychody - koszty - zus_total)
        pit_tax = pit_base * pit_rate
        warnings.append(
            "PIT (liniowy) obliczony od dochodu (przychód - koszty - ZUS społ.) bez odliczenia składki zdrowotnej (uproszczenie).")  # PIT (flat) calculated from income (revenue - costs - social ZUS) without health contribution deduction (simplification).
    elif data.forma_opodatkowania == "skala":
        # Base = income (revenue - costs - social contributions) / Podstawa = dochód (przychód - koszty - składki społeczne)
        pit_base = max(0, przychody - koszty - zus_total)
        # Calculation for tax scale (simplified, without monthly tax-reducing amount) / Obliczenie dla skali podatkowej (uproszczone, bez miesięcznej kwoty zmniejszającej podatek)
        # TODO: Implement correct calculation with tax-free amount/tax-reducing amount and annual thresholds / TODO: Zaimplementuj poprawne obliczenie z kwotą wolną/zmniejszającą podatek i progami rocznymi
        # Estimated annual income / Szacowany roczny dochód
        roczny_dochod_szacowany = pit_base * 12
        # 3600 / 12 (Tax reducing amount per month) / (Kwota zmniejszająca podatek miesięcznie)
        kwota_zmniejszajaca_miesiecznie = 300.0
        if roczny_dochod_szacowany <= 120000:  # First tax threshold / Pierwszy próg podatkowy
            pit_rate = 0.12
            pit_tax = max(0, (pit_base * pit_rate) -
                          kwota_zmniejszajaca_miesiecznie)  # Apply tax reducing amount / Zastosuj kwotę zmniejszającą podatek
        else:  # Second tax threshold / Drugi próg podatkowy
            pit_rate = 0.32
            # Very simplified calculation for the second threshold / Bardzo uproszczone obliczenie dla drugiego progu
            # Correct calculation requires considering the tax paid in the first bracket / Poprawne obliczenie wymaga uwzględnienia podatku zapłaconego w pierwszym progu
            pit_tax = pit_base * pit_rate  # Needs refinement / Wymaga dopracowania
        warnings.append(
            "PIT (skala) obliczony w sposób uproszczony (bez pełnego uwzględnienia kwoty wolnej/zmniejszającej i progów rocznych).")  # PIT (scale) calculated simplistically (without full consideration of tax-free/reducing amount and annual thresholds).
    else:  # Unknown tax form / Nieznana forma opodatkowania
        raise HTTPException(
            status_code=400, detail="Nieprawidłowa forma opodatkowania")  # Invalid tax form

    # Tax cannot be negative / Podatek nie może być ujemny
    pit_tax = round(max(0, pit_tax), 2)

    # Apply tax discount if applicable / Zastosuj ulgę podatkową, jeśli dotyczy
    if data.has_tax_discount:
        # TODO: Clarify which specific discount is meant. / TODO: Wyjaśnij, o którą konkretnie ulgę chodzi.
        # If 50% KUP for creators, it affects pit_base, not pit_tax directly. / Jeśli 50% KUP dla twórców, wpływa to na pit_base, a nie bezpośrednio na pit_tax.
        pit_tax *= 0.5  # Current logic reduces the tax amount / Obecna logika zmniejsza kwotę podatku
        warnings.append(
            "Zastosowano uproszczoną zniżkę PIT 50% na kwotę podatku.")  # Applied simplified 50% PIT discount on the tax amount.

    # Calculate VAT (does not affect other calculations) / Oblicz VAT (nie wpływa na inne obliczenia)
    vat_amount = round(data.income * (data.stawka_vat / 100), 2)

    # Total monthly burden (excluding VAT) / Całkowite miesięczne obciążenie (bez VAT)
    total_contributions = round(zus_total + health_contribution + pit_tax, 2)

    # Net income ('take-home' pay) / Dochód netto ('na rękę')
    net_income = round(data.income - data.costs - total_contributions, 2)

    # Format the response / Sformatuj odpowiedź
    return QuotaOutput(
        rok_danych_zus=zus_info.year,  # Year of ZUS data / Rok danych ZUS
        # ZUS base used / Użyta podstawa ZUS
        podstawa_wymiaru_skladek_zus=zus_info.zus_base,
        # Detailed ZUS contributions / Szczegółowe składki ZUS
        zus_spoleczne_details=zus_details,
        zus_spoleczne_total=zus_total,  # Total social ZUS / Suma ZUS społecznego
        # Health contribution / Składka zdrowotna
        skladka_zdrowotna=health_contribution,
        podatek_pit=pit_tax,  # PIT amount / Kwota PIT
        vat=vat_amount,  # VAT amount / Kwota VAT
        calkowite_obciazenie=total_contributions,  # Total burden / Całkowite obciążenie
        dochod_netto=net_income,  # Net income / Dochód netto
        ostrzezenia=warnings,  # List of warnings / Lista ostrzeżeń
        # ZUS data fetch error message (if any) / Komunikat błędu pobierania danych ZUS (jeśli wystąpił)
        blad_danych_zus=zus_info.error_message
    )

# Endpoint to check current ZUS data (uses the new module) / Punkt końcowy do sprawdzania aktualnych danych ZUS (używa nowego modułu)


@app.get("/aktualne_dane_zus", response_model=ZUSData)
async def get_current_zus_data(force_refresh: bool = False):
    """
    Returns current data about projected average salary and ZUS base. Uses cache.
    Add ?force_refresh=true to update data from the ZUS website.

    Zwraca aktualne dane o prognozowanym przeciętnym wynagrodzeniu i podstawie ZUS. Używa pamięci podręcznej.
    Dodaj ?force_refresh=true, aby zaktualizować dane ze strony ZUS.
    """
    result = fetch_and_cache_zus_data(force_refresh=force_refresh)
    # No need to raise an error here, just return the result (which might contain an error message)
    # Nie ma potrzeby zgłaszania tutaj błędu, po prostu zwróć wynik (który może zawierać komunikat o błędzie)
    return result
