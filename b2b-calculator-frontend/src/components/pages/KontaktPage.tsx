import React from "react";

const KontaktPage: React.FC = () => {
  return (
    <div className="container mx-auto p-4 mt-8 max-w-xl">
      {" "}
      {/* Обмеження ширини */}
      <h1 className="text-3xl font-bold mb-6 text-gray-800 text-center">
        Контакти
      </h1>
      <div className="bg-white shadow-lg rounded-lg p-6 md:p-8 text-gray-700 space-y-4">
        {" "}
        {/* Більші відступи */}
        <p className="text-lg">
          Якщо у вас виникли запитання щодо роботи калькулятора, є пропозиції
          щодо його покращення, або ви помітили помилку в розрахунках, будь
          ласка, зв'яжіться зі мною.
        </p>
        <p>Я завжди відкритий до конструктивного фідбеку та співпраці.</p>
        <div className="pt-4 space-y-3">
          <h2 className="text-xl font-semibold">Способи зв'язку:</h2>
          <ul className="list-none space-y-2">
            <li className="flex items-center">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-5 w-5 mr-2 text-indigo-600"
                viewBox="0 0 20 20"
                fill="currentColor"
              >
                <path d="M2.003 5.884L10 9.882l7.997-3.998A2 2 0 0016 4H4a2 2 0 00-1.997 1.884z" />
                <path d="M18 8.118l-8 4-8-4V14a2 2 0 002 2h12a2 2 0 002-2V8.118z" />
              </svg>
              <strong>Email:</strong>
              <a
                href="mailto:your.email@example.com"
                className="ml-2 text-indigo-600 hover:underline break-all"
              >
                your.email@example.com {/* <-- ЗАМІНІТЬ НА ВАШ EMAIL */}
              </a>
            </li>
            <li className="flex items-center">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-5 w-5 mr-2 text-gray-800"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                strokeWidth="2"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4"
                />
              </svg>
              <strong>GitHub:</strong>
              <a
                href="https://github.com/yourusername"
                target="_blank"
                rel="noopener noreferrer"
                className="ml-2 text-indigo-600 hover:underline break-all"
              >
                github.com/yourusername {/* <-- ЗАМІНІТЬ НА ВАШ GITHUB */}
              </a>
            </li>
            {/* Додайте інші контакти за потреби (LinkedIn, Telegram тощо) */}
            {/* <li className="flex items-center">
              <svg ... > </svg>
              <strong>LinkedIn:</strong>
              <a href="..." target="_blank" rel="noopener noreferrer" className="ml-2 text-indigo-600 hover:underline">...</a>
            </li> */}
          </ul>
        </div>
        <p className="text-sm text-gray-500 pt-4 border-t mt-6">
          Будь ласка, зверніть увагу, що я не надаю професійних бухгалтерських
          чи податкових консультацій.
        </p>
      </div>
    </div>
  );
};

export default KontaktPage;
