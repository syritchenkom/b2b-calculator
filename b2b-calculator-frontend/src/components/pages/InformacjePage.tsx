import React from "react";

const InformacjePage: React.FC = () => {
  return (
    <div className="container mx-auto p-4 mt-8 max-w-3xl">
      {" "}
      {/* Обмеження ширини */}
      <h1 className="text-3xl font-bold mb-6 text-gray-800 text-center">
        Інформація
      </h1>
      <div className="bg-white shadow-lg rounded-lg p-6 md:p-8 text-gray-700 space-y-4">
        {" "}
        {/* Більші відступи на середніх екранах */}
        <p className="text-lg">
          Цей розділ призначений для надання детальної інформації про
          розрахунки, податкові ставки, внески ZUS та інші важливі аспекти
          ведення підприємницької діяльності (B2B) в Польщі.
        </p>
        <h2 className="text-xl font-semibold pt-4">Форми оподаткування</h2>
        <p>
          В Польщі існують різні форми оподаткування для підприємців, кожна зі
          своїми особливостями:
        </p>
        <ul className="list-disc list-inside ml-4 space-y-1">
          <li>
            <strong>Ryczałt od przychodów ewidencjonowanych:</strong> Спрощена
            форма, де податок сплачується з доходу за фіксованою ставкою, що
            залежить від виду діяльності. Немає можливості враховувати витрати.
          </li>
          <li>
            <strong>Skala podatkowa (zasady ogólne):</strong> Прогресивна шкала
            (12% та 32%). Дозволяє враховувати витрати та користуватися різними
            податковими пільгами.
          </li>
          <li>
            <strong>Podatek liniowy:</strong> Фіксована ставка податку (19%)
            незалежно від доходу. Дозволяє враховувати витрати, але обмежує
            доступ до деяких пільг.
          </li>
        </ul>
        <h2 className="text-xl font-semibold pt-4">Внески ZUS</h2>
        <p>
          Соціальні внески (ZUS) є обов'язковими і їх розмір залежить від стажу
          підприємницької діяльності та доходу (для składki zdrowotnej):
        </p>
        <ul className="list-disc list-inside ml-4 space-y-1">
          <li>
            <strong>Ulga na start:</strong> Звільнення від соціальних внесків
            (крім składki zdrowotnej) протягом перших 6 місяців.
          </li>
          <li>
            <strong>ZUS preferencyjny:</strong> Знижені соціальні внески
            протягом наступних 24 місяців.
          </li>
          <li>
            <strong>Mały ZUS Plus:</strong> Можливість сплачувати знижені внески
            залежно від доходу за попередній рік (за певних умов).
          </li>
          <li>
            <strong>Pełny ZUS:</strong> Стандартні внески для досвідчених
            підприємців.
          </li>
        </ul>
        <p>
          Розмір внеску на медичне страхування (składka zdrowotna) залежить від
          обраної форми оподаткування та доходу/прибутку.
        </p>
        <h2 className="text-xl font-semibold pt-4">Податкові знижки (Ulgi)</h2>
        <p>
          Існують різні податкові знижки, які можуть зменшити базу оподаткування
          або сам податок, наприклад:
        </p>
        <ul className="list-disc list-inside ml-4 space-y-1">
          <li>
            <strong>Ulga IP Box:</strong> Знижена ставка податку (5%) для
            доходів від кваліфікованих прав інтелектуальної власності.
          </li>
          <li>
            <strong>Ulga B+R (Badania i Rozwój):</strong> Додаткове відрахування
            витрат на дослідження та розробки.
          </li>
          <li>Інші пільги (наприклад, для молоді, на дітей тощо).</li>
        </ul>
        <p className="text-sm text-red-600 pt-6 border-t mt-6 font-semibold">
          <strong>Важливе застереження:</strong> Інформація та розрахунки,
          надані на цьому сайті, мають виключно ознайомчий характер і не є
          юридичною або податковою консультацією. Податкове законодавство Польщі
          може змінюватися. Для отримання точної та актуальної інформації, що
          стосується вашої індивідуальної ситуації, завжди звертайтеся до
          кваліфікованого бухгалтера або податкового консультанта.
        </p>
      </div>
    </div>
  );
};

export default InformacjePage;
