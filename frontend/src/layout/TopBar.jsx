import { Link, useLocation } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { Eye, Wallet, Search, X, Bell, Filter } from 'lucide-react';

export default function TopBar() {
  const location = useLocation();
  const [searchOpen, setSearchOpen] = useState(false);
  const [isMobile, setIsMobile] = useState(false);
  
  // Check if mobile on mount and resize
  useEffect(() => {
    const checkMobile = () => setIsMobile(window.innerWidth < 768);
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);
  
  const isActive = (path) => {
    if (path === '/') return location.pathname === '/';
    return location.pathname.startsWith(path);
  };

  return (
    <div className="bg-white border-b px-4 md:px-6 py-3 flex items-center justify-between" data-testid="topbar">
      {/* Search Bar */}
      <div className="flex-1 max-w-2xl">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search for a project, fund or person..."
            className="w-full pl-10 pr-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-gray-300 focus:border-transparent text-sm"
          />
        </div>
      </div>

      {/* Stats */}
      <div className="hidden md:flex items-center gap-6 mx-6">
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-500 uppercase tracking-wide">Funds</span>
          <span className="text-sm font-semibold text-gray-900">200</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-500 uppercase tracking-wide">Projects</span>
          <span className="text-sm font-semibold text-gray-900">200</span>
        </div>
      </div>

      {/* Right Section - Icons + Connect */}
      <div className="flex items-center gap-2 md:gap-3">
        {/* Social Icons */}
        <div className="hidden lg:flex items-center gap-1">
          {['twitter', 'discord', 'telegram', 'instagram', 'linkedin', 'youtube', 'tiktok'].map((social) => (
            <button 
              key={social}
              className="p-2 rounded-lg text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition-colors"
            >
              <img 
                src={`https://cdn.simpleicons.org/${social}/888888`} 
                alt={social}
                className="w-4 h-4"
                onError={(e) => e.target.style.display = 'none'}
              />
            </button>
          ))}
        </div>

        {/* Ad Mode Button */}
        <button className="hidden md:flex items-center gap-1.5 px-3 py-2 text-xs font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors">
          <Eye className="w-4 h-4" />
          <span>Ad Mode</span>
        </button>

        {/* Filter Button */}
        <button className="flex items-center gap-1.5 px-3 py-2 text-xs font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors">
          <Filter className="w-4 h-4" />
          <span className="hidden sm:inline">Filter</span>
        </button>

        {/* Notifications */}
        <button className="relative p-2.5 rounded-full text-gray-500 hover:text-gray-900 hover:bg-gray-100 transition-colors">
          <Bell className="w-5 h-5" />
          <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
        </button>

        {/* Connect Wallet Button */}
        <button className="flex items-center gap-2 px-3 md:px-5 py-2 md:py-2.5 bg-gray-900 hover:bg-gray-800 text-white rounded-full text-xs md:text-sm font-bold transition-all shadow-lg shadow-gray-900/20 hover:shadow-xl hover:shadow-gray-900/30 hover:scale-105 active:scale-95">
          <Wallet className="w-4 h-4" />
          <span className="hidden sm:inline">Connect</span>
        </button>
      </div>
    </div>
  );
}
