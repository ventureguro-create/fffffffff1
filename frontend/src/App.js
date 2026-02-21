import "./App.css";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { Suspense, lazy } from "react";
import AppLayout from "./layout/AppLayout";

// Loading component for Suspense fallback
const PageLoader = () => (
  <div className="min-h-screen bg-gray-50 flex items-center justify-center">
    <div className="flex flex-col items-center gap-4">
      <div className="w-10 h-10 border-4 border-gray-200 border-t-gray-900 rounded-full animate-spin" />
      <p className="text-sm text-gray-500 font-medium">Loading...</p>
    </div>
  </div>
);

// Main dashboard placeholder
const DashboardPage = () => (
  <div className="p-6">
    <h1 className="text-page-title mb-4">Dashboard</h1>
    <p className="text-description">Welcome to FOMO Intelligence Platform</p>
  </div>
);

// Telegram Intelligence Module
const TelegramEntitiesPage = lazy(() => import("./pages/TelegramEntitiesPage"));
const TelegramChannelOverviewPage = lazy(() => import("./pages/TelegramChannelOverviewPage"));

function App() {
  return (
    <BrowserRouter>
      <Suspense fallback={<PageLoader />}>
        <Routes>
          {/* Main routes with AppLayout (sidebar + topbar) */}
          <Route element={<AppLayout />}>
            {/* Dashboard */}
            <Route path="/" element={<DashboardPage />} />
            
            {/* Telegram Intelligence Module */}
            <Route path="/telegram" element={<TelegramEntitiesPage />} />
            <Route path="/telegram/entities" element={<TelegramEntitiesPage />} />
            <Route path="/telegram/channel/:username" element={<TelegramChannelOverviewPage />} />
            <Route path="/telegram/:username" element={<TelegramChannelOverviewPage />} />
            
            {/* Placeholder routes for sidebar navigation */}
            <Route path="/market" element={<DashboardPage />} />
            <Route path="/tokens" element={<DashboardPage />} />
            <Route path="/wallets" element={<DashboardPage />} />
            <Route path="/entities" element={<DashboardPage />} />
            <Route path="/actors" element={<DashboardPage />} />
            <Route path="/signals" element={<DashboardPage />} />
            
            {/* Fallback */}
            <Route path="/*" element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
      </Suspense>
    </BrowserRouter>
  );
}

export default App;
