import React from 'react';
import { NavLink, Link } from 'react-router-dom'; // Використовуємо NavLink для стилізації активних посилань

// Якщо у вас є емблема (наприклад, SVG або PNG)
// import logo from '../assets/logo.svg'; // Приклад імпорту

const Header: React.FC = () => {
  // Функція для визначення класів посилань (активне/неактивне/hover)
  const getNavLinkClass = ({ isActive }: { isActive: boolean }): string => {
    const baseClasses = 'transition-colors duration-150 font-medium px-3 py-1 rounded'; // Базові класи + трохи падінгу для кращого кліку
    if (isActive) {
      return `${baseClasses} text-white`; // Активний стан: білий
    }
    // Неактивний стан + hover
    return `${baseClasses} text-white/50 hover:text-white/75`; // Неактивний: білий з 50% прозорості, Hover: білий з 75% прозорості
  };

  return (
    <header className="w-full bg-black text-white text-base py-3 px-6 flex items-center justify-between shadow-md">
      {/* Ліва сторона: Логотип або Назва */}
      <Link to="/" className="text-xl font-bold hover:opacity-80 transition-opacity">
        {/* Варіант 1: Текстова назва */}
        B2B Калькулятор
        {/* Варіант 2: Емблема (розкоментуйте, якщо є) */}
        {/* <img src={logo} alt="Логотип" className="h-8 w-auto" /> */}
      </Link>

      {/* Права сторона: Меню навігації */}
      <nav>
        <ul className="flex space-x-4">
          <li>
            <NavLink to="/" className={getNavLinkClass} end> {/* `end` важливий для головної сторінки */}
              KALKULATOR
            </NavLink>
          </li>
          <li>
            <NavLink to="/informacje" className={getNavLinkClass}>
              INFORMACJE
            </NavLink>
          </li>
          <li>
            <NavLink to="/kontakt" className={getNavLinkClass}>
              KONTAKT
            </NavLink>
          </li>
        </ul>
      </nav>
    </header>
  );
};

export default Header;