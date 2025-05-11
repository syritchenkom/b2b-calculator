import React from "react";
import { Link } from "react-router-dom"; // Для посилання на головну

const NotFoundPage: React.FC = () => {
  return (
    <div className="container mx-auto p-4 mt-16 flex flex-col items-center justify-center text-center">
      {" "}
      {/* Відступ зверху та центрування */}
      <svg
        xmlns="http://www.w3.org/2000/svg"
        className="h-24 w-24 text-red-500 mb-4"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
        strokeWidth="1"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
        />
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          d="M12 8v4m0 4h.01"
        />{" "}
        {/* Знак оклику всередині */}
      </svg>
      <h1 className="text-6xl font-bold text-gray-800 mb-2">404</h1>
      <h2 className="text-2xl font-semibold text-gray-600 mb-6">
        Сторінку не знайдено
      </h2>
      <p className="text-gray-500 mb-8 max-w-md">
        На жаль, сторінка, яку ви шукаєте, не існує. Можливо, ви ввели
        неправильну адресу або сторінка була переміщена.
      </p>
      <Link
        to="/"
        className="bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-2 px-6 rounded focus:outline-none focus:shadow-outline transition duration-150 ease-in-out"
      >
        Повернутися на головну
      </Link>
    </div>
  );
};

export default NotFoundPage;
