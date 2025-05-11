import React, { useState, FormEvent, ChangeEvent, useCallback } from "react";
import axios from "axios";

// --- Інтерфейси (можна винести в src/types.ts) ---
interface QuotaInput {
  income: number;
  costs: number;
  forma_opodatkowania:
    | "ryczalt_15"
    | "ryczalt_12"
    | "liniowy_19"
    | "skala"
    | "";
  stawka_vat: number;
  has_tax_discount: boolean;
  platnik_chorobowe: boolean;
}

interface SkladkaDetail {
  nazwa: string;
  procent: number;
  podstawa: number;
  kwota: number;
}

interface QuotaOutput {
  rok_danych_zus: number;
  podstawa_wymiaru_skladek_zus: number | null;
  zus_spoleczne_details: SkladkaDetail[];
  zus_spoleczne_total: number;
  skladka_zdrowotna: number;
  podatek_pit: number;
  vat: number;
  calkowite_obciazenie: number;
  dochod_netto: number;
  ostrzezenia: string[];
  blad_danych_zus: string | null;
}

const CalculatorPage: React.FC = () => {
  // --- Стан для вхідних даних та результатів ---
  const [inputData, setInputData] = useState<QuotaInput>({
    income: 10000,
    costs: 0,
    forma_opodatkowania: "ryczalt_15", // Початкова форма
    stawka_vat: 8, // Початкова ставка VAT
    has_tax_discount: false,
    platnik_chorobowe: false, // За замовчуванням сплачує
  });
  const [results, setResults] = useState<QuotaOutput | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    setResults(null);
    setIsLoading(true);

    // Перевірка чи вибрана форма оподаткування
    if (!inputData.forma_opodatkowania) {
      setError("Будь ласка, оберіть форму оподаткування.");
      setIsLoading(false);
      return;
    }

    // Перевірка чи дохід є числом і не від'ємний
    if (isNaN(inputData.income) || inputData.income < 0) {
      setError("Будь ласка, введіть дійсний позитивний дохід.");
      setIsLoading(false);
      return;
    }
    // Перевірка чи витрати є числом і не від'ємні
    if (isNaN(inputData.costs) || inputData.costs < 0) {
      setError("Будь ласка, введіть дійсні невід'ємні витрати.");
      setIsLoading(false);
      return;
    }

    // Дані для відправки на бекенд
    const requestData = {
      ...inputData,
      // Переконуємося, що числові значення передаються як числа
      income: Number(inputData.income),
      costs: Number(inputData.costs),
      stawka_vat: Number(inputData.stawka_vat),
    };

    try {
      const response = await axios.post<QuotaOutput>(
        "http://127.0.0.1:8000/oblicz",
        requestData
      );

      console.log("Результат обчислення:", response.data);
      setResults(response.data);
    } catch (err) {
      if (axios.isAxiosError(err)) {
        console.error("Помилка запиту axios:", err.response?.data);
        // Спробуємо показати помилку з бекенду, якщо вона є
        const backendError =
          err.response?.data?.detail || "Сталася помилка під час розрахунку.";
        setError(
          typeof backendError === "string"
            ? backendError
            : "Сталася невідома помилка валідації."
        );
      } else {
        setError("Сталася невідома помилка.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  // Розрахунок доходу "на руки"
  const incomeNet = results
    ? results.dochod_netto // Використовуємо значення з бекенду
    : null;

  // Універсальний обробник змін для полів форми
  const handleChange = useCallback(
    (e: ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
      const { name, value, type } = e.target;

      // Для чекбоксів використовуємо 'checked', для інших - 'value'
      const newValue =
        type === "checkbox" ? (e.target as HTMLInputElement).checked : value;

      setInputData((prevData) => ({
        ...prevData,
        [name]: newValue,
      }));
    },
    []
  );
  return (
    // Контейнер для основного контенту сторінки Калькулятора
    <div className="container mx-auto p-4 max-w-lg mt-8">
      <div className="bg-white shadow-lg rounded-lg p-6 md:p-8">
        <form
          onSubmit={handleSubmit}
          className="bg-white shadow-xl rounded-lg px-8 pt-6 pb-8 mb-6" // Покращені тіні та відступи
        >
          {/* Відступ зверху */}
          <h1 className="text-3xl font-bold text-center mb-6 text-gray-800">
            Калькулятор B2B (Польща)
          </h1>
          {/* Поле для введення доходу */}
          <div className="mb-5">
            <label
              htmlFor="income"
              className="block text-gray-700 text-sm font-bold mb-2"
            >
              Місячний дохід (PLN, нетто на фактурі):
            </label>
            <input
              type="number"
              id="income"
              name="income" // Name attribute for form handling
              value={inputData.income}
              onChange={handleChange} // Використовуємо універсальний обробник
              placeholder="Наприклад, 10000"
              step="0.01"
              min="0"
              required
              className="shadow-sm appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition duration-150 ease-in-out" // Покращений фокус
            />
          </div>

          {/* Додано поле для витрат */}
          <div className="mb-5">
            <label
              htmlFor="costs"
              className="block text-gray-700 text-sm font-bold mb-2"
            >
              Місячні витрати (KUP, PLN):
            </label>
            <input
              type="number"
              id="costs"
              name="costs" // Додано name
              value={inputData.costs}
              onChange={handleChange} // Використовуємо універсальний обробник
              step="0.01"
              className="shadow-sm appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition duration-150 ease-in-out"
            />
          </div>

          <div className="mb-5">
            <label
              htmlFor="vatRate"
              className="block text-gray-700 text-sm font-bold mb-2"
            >
              Ставка VAT (%):
            </label>
            <select
              id="vatRate"
              name="stawka_vat" // Змінено name відповідно до QuotaInput
              value={inputData.stawka_vat}
              onChange={handleChange} // Використовуємо універсальний обробник
              className="shadow-sm border rounded w-full py-2 px-3 text-gray-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition duration-150 ease-in-out"
            >
              <option value={0}>0%</option>
              <option value={5}>5%</option>
              <option value={8}>8%</option>
              <option value={23}>23%</option>
            </select>
          </div>

          {/* Вибір форми оподаткування */}
          <div className="mb-5">
            <label
              htmlFor="taxForm"
              className="block text-gray-700 text-sm font-bold mb-2"
            >
              Форма оподаткування:
            </label>
            <select
              id="taxForm"
              name="forma_opodatkowania" // Додано name
              value={inputData.forma_opodatkowania}
              onChange={handleChange} // Використовуємо універсальний обробник
              required // Додано required, якщо вибір обов'язковий
              className="shadow-sm border rounded w-full py-2 px-3 text-gray-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition duration-150 ease-in-out"
            >
              {/* <option value="" disabled>-- Виберіть форму --</option> */}
              <option value="skala">Skala podatkowa (12%/32%)</option>
              <option value="liniowy_19">Podatek liniowy 19%</option>
              <option value="ryczalt_15">Ryczałt 15%</option>
              <option value="ryczalt_12">Ryczałt 12%</option>
            </select>
          </div>

          {/* Додано чекбокс для składki chorobowej */}
          <div className="mb-5">
            <label className="flex items-center text-gray-700 text-sm font-bold cursor-pointer">
              <input
                type="checkbox"
                id="platnik_chorobowe"
                name="platnik_chorobowe" // Додано name
                checked={inputData.platnik_chorobowe}
                onChange={handleChange} // Використовуємо універсальний обробник
                className="mr-2 leading-tight h-4 w-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500"
              />
              <span>Сплачую добровільний внесок на випадок хвороби</span>
            </label>
          </div>

          {/* Чекбокс для податкової знижки */}
          <div className="mb-6">
            <label className="flex items-center text-gray-700 text-sm font-bold cursor-pointer">
              <input
                type="checkbox"
                name="has_tax_discount" // Додано name
                checked={inputData.has_tax_discount}
                onChange={handleChange} // Використовуємо універсальний обробник
                className="mr-2 leading-tight h-4 w-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500" // Стилізація чекбоксу
              />
              <span>Маю податкову знижку (Ulga IP Box / R&D)</span>
              {/* Уточнено назву */}
            </label>
            <p className="text-xs text-gray-500 mt-1">
              Застосовує 50% знижку до бази оподаткування PIT.
            </p>{" "}
            {/* Примітка: Бекенд застосовує знижку до суми податку, а не бази. Можливо, варто уточнити текст. */}
          </div>

          {/* Кнопка відправки та індикатор завантаження */}
          <div className="flex items-center justify-center">
            {/* Кнопка по центру */}
            <button
              type="submit"
              disabled={isLoading}
              className={`w-full sm:w-auto bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-2 px-6 rounded focus:outline-none focus:shadow-outline transition duration-150 ease-in-out ${
                // Стилізація кнопки
                isLoading ? "opacity-50 cursor-not-allowed" : ""
              }`}
            >
              {isLoading ? "Розрахунок..." : "Розрахувати"}
            </button>
          </div>
        </form>
        {/* Відображення помилок */}
        {error && (
          <div
            className="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 mb-6 rounded-md shadow" // Покращений вигляд помилки
            role="alert"
          >
            <p className="font-bold">Помилка!</p>
            <p>{error}</p>
          </div>
        )}
        {/* --- Відображення результатів --- */}
        {/* Умовне відображення блоку результатів */}
        {(isLoading || results) && (
          <div
            className={`p-6 rounded-md shadow h-full ${
              isLoading
                ? "bg-gray-100 border-l-4 border-gray-300 text-gray-600 animate-pulse"
                : results
                ? "bg-green-100 border-l-4 border-green-500 text-green-800"
                : "bg-gray-100 border-l-4 border-gray-300 text-gray-700" // Початковий стан
            }`}
          >
            <h2 className="text-xl font-semibold mb-4 text-center">
              {isLoading
                ? "Триває розрахунок..."
                : `Результати (дані ZUS на ${results?.rok_danych_zus} рік):`}
            </h2>

            {/* Попередження від бекенду */}
            {results?.blad_danych_zus && (
              <div
                className="mb-4 bg-yellow-100 border border-yellow-400 text-yellow-700 px-4 py-3 rounded"
                role="alert"
              >
                <strong className="font-bold">Увага (дані ZUS): </strong>{" "}
                {results.blad_danych_zus}
              </div>
            )}
            {results?.ostrzezenia && results.ostrzezenia.length > 0 && (
              <div
                className="mb-4 bg-blue-100 border border-blue-400 text-blue-700 px-4 py-3 rounded"
                role="alert"
              >
                <strong className="font-bold">
                  Попередження щодо розрахунків:
                </strong>
                <ul className="list-disc list-inside mt-1">
                  {results.ostrzezenia.map((warn, index) => (
                    <li key={index}>{warn}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Основні результати */}
            {isLoading ? (
              <div className="text-center text-lg font-semibold animate-pulse">
                ...
              </div>
            ) : results ? (
              <>
                <ul className="space-y-2 text-gray-700">
                  <li className="flex justify-between items-center py-1">
                    <span>База для внесків ZUS:</span>
                    <strong className="font-mono text-lg">
                      {results.podstawa_wymiaru_skladek_zus !== null
                        ? results.podstawa_wymiaru_skladek_zus.toFixed(2)
                        : "N/A"}{" "}
                      PLN
                    </strong>
                  </li>
                  <li className="flex justify-between items-center py-1">
                    <span>Сума соціальних внесків ZUS:</span>
                    <strong className="font-mono text-lg">
                      {results.zus_spoleczne_total.toFixed(2)} PLN
                    </strong>
                  </li>
                  <li className="flex justify-between items-center py-1">
                    <span>Внесок на здоров'я (NFZ):</span>
                    <strong className="font-mono text-lg">
                      {results.skladka_zdrowotna.toFixed(2)} PLN
                    </strong>
                  </li>
                  <li className="flex justify-between items-center py-1">
                    <span>Податок PIT (прибутковий):</span>
                    <strong className="font-mono text-lg">
                      {results.podatek_pit.toFixed(2)} PLN
                    </strong>
                  </li>
                  <li className="flex justify-between items-center py-1 border-t pt-2 mt-2">
                    <span>ПДВ (VAT) до сплати:</span>
                    <strong className="font-mono text-lg">
                      {results.vat.toFixed(2)} PLN
                    </strong>
                  </li>
                  <li
                    className={`mt-3 pt-3 border-t ${
                      results ? "border-green-300" : "border-gray-300"
                    } flex justify-between items-center text-lg font-semibold`}
                  >
                    <span>Загальне навантаження (ZUS + Здоров'я + PIT):</span>
                    <strong className="font-mono text-xl">
                      {results.calkowite_obciazenie.toFixed(2)} PLN
                    </strong>
                  </li>
                  <li
                    className={`mt-3 pt-3 border-t-2 border-indigo-500 ${
                      // Змінено стиль розділювача
                      results ? "border-indigo-500" : "border-gray-300"
                    } flex justify-between items-center text-xl font-bold ${
                      results ? "text-indigo-700" : "text-gray-500 opacity-75"
                    }`}
                  >
                    <span>Дохід нетто ("на руки"):</span>
                    <strong className="font-mono text-2xl">
                      {results.dochod_netto.toFixed(2)} PLN
                    </strong>
                  </li>
                </ul>

                {/* Деталізація ZUS (опціонально) */}
                {results.zus_spoleczne_details &&
                  results.zus_spoleczne_details.length > 0 && (
                    <details className="mt-6">
                      <summary className="cursor-pointer font-semibold text-indigo-600 hover:text-indigo-800">
                        Показати деталі соціальних внесків ZUS
                      </summary>
                      <table className="w-full border-collapse mt-2 text-sm">
                        <thead>
                          <tr className="border-b text-left text-gray-600">
                            <th className="p-2 font-medium">Назва</th>
                            <th className="p-2 font-medium">Ставка (%)</th>
                            <th className="p-2 font-medium">База (PLN)</th>
                            <th className="p-2 font-medium">Сума (PLN)</th>
                          </tr>
                        </thead>
                        <tbody>
                          {results.zus_spoleczne_details.map((detail) => (
                            <tr
                              key={detail.nazwa}
                              className="border-b border-gray-200 hover:bg-gray-50"
                            >
                              <td className="p-2">{detail.nazwa}</td>
                              <td className="p-2 font-mono">
                                {detail.procent.toFixed(2)}%
                              </td>
                              <td className="p-2 font-mono">
                                {detail.podstawa.toFixed(2)}
                              </td>
                              <td className="p-2 font-mono">
                                {detail.kwota.toFixed(2)}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </details>
                  )}
              </>
            ) : (
              // Початковий стан або стан після помилки (коли немає результатів)
              <ul className="space-y-2 text-gray-500 opacity-75">
                <li className="flex justify-between items-center py-1">
                  <span>База для внесків ZUS:</span>{" "}
                  <strong className="font-mono text-lg">- PLN</strong>
                </li>
                <li className="flex justify-between items-center py-1">
                  <span>Сума соціальних внесків ZUS:</span>{" "}
                  <strong className="font-mono text-lg">- PLN</strong>
                </li>
                <li className="flex justify-between items-center py-1">
                  <span>Внесок на здоров'я (NFZ):</span>{" "}
                  <strong className="font-mono text-lg">- PLN</strong>
                </li>
                <li className="flex justify-between items-center py-1">
                  <span>Податок PIT (прибутковий):</span>{" "}
                  <strong className="font-mono text-lg">- PLN</strong>
                </li>
                <li className="flex justify-between items-center py-1 border-t pt-2 mt-2">
                  <span>ПДВ (VAT) до сплати:</span>{" "}
                  <strong className="font-mono text-lg">- PLN</strong>
                </li>
                <li className="mt-3 pt-3 border-t border-gray-300 flex justify-between items-center text-lg font-semibold">
                  <span>Загальне навантаження:</span>
                  <strong className="font-mono text-xl">- PLN</strong>
                </li>
                <li className="mt-3 pt-3 border-t-2 border-gray-300 flex justify-between items-center text-xl font-bold">
                  <span>Дохід "на руки":</span>
                  <strong className="font-mono">
                    {incomeNet !== null ? incomeNet.toFixed(2) : "-"} PLN
                  </strong>
                </li>
              </ul> // Кінець початкового стану
            )}
          </div>
        )}{" "}
        {/* Кінець умовного відображення блоку результатів */}
      </div>
    </div>
  );
};

export default CalculatorPage;
