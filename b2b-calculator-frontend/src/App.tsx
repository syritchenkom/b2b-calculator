import { Routes, Route } from "react-router-dom";

// Імпортуємо компоненти макету
import Header from "./components/Header";
// import Footer from './components/Footer'; // Якщо є футер

// Імпортуємо компоненти сторінок з окремих файлів
import CalculatorPage from "./components/pages/CalculatorPage";
import InformacjePage from "./components/pages/InformacjePage";
import KontaktPage from "./components/pages/KontaktPage";
import NotFoundPage from "./components/pages/NotFoundPage"; // Якщо є сторінка 404

function App() {
  return (
    <div className="flex flex-col min-h-screen bg-gray-100">
      {/* Header start*/}
      <Header />
      {/* Header end*/}
      {/* Main content start*/}
      <main className="flex-grow">
        <Routes>
          <Route path="/" element={<CalculatorPage />} />
          <Route path="/informacje" element={<InformacjePage />} />
          <Route path="/kontakt" element={<KontaktPage />} />
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </main>
      {/* Main content end*/}
      {/* Footer start */}
      <footer className="bg-gray-800 text-gray-400 text-center p-4 text-sm mt-8">
        © {new Date().getFullYear()} B2B Калькулятор. Орієнтовні розрахунки.
      </footer>
      {/* Footer end */}
    </div>
  );
}

export default App;
