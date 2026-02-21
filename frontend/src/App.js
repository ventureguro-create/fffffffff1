/**
 * Telegram Intelligence App
 * Main application router
 */
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import TelegramEntitiesPage from './pages/TelegramEntitiesPage';
import TelegramChannelOverviewPage from './pages/TelegramChannelOverviewPage';
import './App.css';

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          {/* Main route - Telegram Entities Overview */}
          <Route path="/" element={<Navigate to="/telegram" replace />} />
          <Route path="/telegram" element={<TelegramEntitiesPage />} />
          <Route path="/telegram/:username" element={<TelegramChannelOverviewPage />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;
