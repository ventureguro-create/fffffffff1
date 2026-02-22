import { Link, useLocation } from 'react-router-dom';
import { Wallet, Menu, X } from 'lucide-react';
import { useState, useEffect } from 'react';

export function Sidebar({ globalState }) {
  const location = useLocation();
  const [isMobileOpen, setIsMobileOpen] = useState(false);

  // Close mobile sidebar on route change
  useEffect(() => {
    setIsMobileOpen(false);
  }, [location.pathname]);

  // Close sidebar on escape key
  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === 'Escape') setIsMobileOpen(false);
    };
    window.addEventListener('keydown', handleEscape);
    return () => window.removeEventListener('keydown', handleEscape);
  }, []);

  const isActive = (path) => location.pathname === path || location.pathname.startsWith(path + '/');

  // Navigation items - simple links only
  const navItems = [
    { path: '/', label: 'Dashboard', icon: '🏠' },
    { path: '/market', label: 'Market', icon: '📊' },
    { path: '/telegram', label: 'Telegram', icon: '📱' },
    { path: '/tokens', label: 'Tokens', icon: '🪙' },
    { path: '/wallets', label: 'Wallets', icon: '👛' },
    { path: '/entities', label: 'Entities', icon: '🏢' },
    { path: '/actors', label: 'Actors', icon: '👤' },
    { path: '/signals', label: 'Signals', icon: '📡' },
  ];

  return (
    <>
      {/* Mobile Menu Button - Fixed */}
      <button
        onClick={() => setIsMobileOpen(true)}
        className="lg:hidden fixed top-4 left-4 z-50 p-2 bg-gray-900 text-white rounded-lg shadow-lg"
        data-testid="mobile-menu-btn"
      >
        <Menu className="w-6 h-6" />
      </button>

      {/* Mobile Overlay */}
      {isMobileOpen && (
        <div 
          className="lg:hidden fixed inset-0 bg-black/50 z-40"
          onClick={() => setIsMobileOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside className={`
        fixed lg:relative inset-y-0 left-0 z-50
        w-64 lg:w-56 bg-gray-900 text-white min-h-screen flex flex-col overflow-y-auto
        transform transition-transform duration-300 ease-in-out
        ${isMobileOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
      `}>
        {/* Mobile Close Button */}
        <button
          onClick={() => setIsMobileOpen(false)}
          className="lg:hidden absolute top-4 right-4 p-2 text-gray-400 hover:text-white"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Logo */}
        <div className="p-6 border-b border-gray-800">
          <Link to="/" className="flex items-center gap-2">
            <div className="w-8 h-8 bg-white rounded-lg flex items-center justify-center">
              <span className="text-gray-900 font-bold text-sm">F</span>
            </div>
            <span className="text-white font-bold text-lg">FOMO</span>
          </Link>
        </div>

        {/* Main Navigation */}
        <nav className="flex-1 p-4 space-y-1">
          {navItems.map((item) => {
            // Group item with children
            if (item.children) {
              const isExpanded = expandedGroups.includes(item.id);
              const hasActiveChild = isGroupActive(item.children);
              
              return (
              <div key={item.id}>
                {/* Group header */}
                <button
                  onClick={() => toggleGroup(item.id)}
                  className={`w-full flex items-center justify-between px-3 py-2 rounded-lg text-sm transition-colors ${
                    hasActiveChild
                      ? 'bg-gray-800 text-white font-medium'
                      : 'text-gray-300 hover:bg-gray-800 hover:text-white'
                  }`}
                >
                  <div className="flex items-center gap-2">
                    <span>{item.icon}</span>
                    <span>{item.label}</span>
                  </div>
                  {isExpanded ? (
                    <ChevronDown className="w-4 h-4 text-gray-500" />
                  ) : (
                    <ChevronRight className="w-4 h-4 text-gray-500" />
                  )}
                </button>
                
                {/* Children */}
                {isExpanded && (
                  <div className="ml-4 mt-1 space-y-1 border-l border-gray-700 pl-2">
                    {item.children.map((child) => (
                      <Link
                        key={child.path}
                        to={child.path}
                        className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm ${
                          isActive(child.path)
                            ? 'bg-gray-800 text-white font-medium'
                            : 'text-gray-400 hover:bg-gray-800 hover:text-white'
                        }`}
                      >
                        <span className="text-xs">{child.icon}</span>
                        <span>{child.label}</span>
                      </Link>
                    ))}
                  </div>
                )}
              </div>
            );
          }
          
          // Regular item
          return (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm ${
                isActive(item.path) && item.path !== '/'
                  ? 'bg-gray-800 text-white font-medium'
                  : item.path === '/' && location.pathname === '/'
                  ? 'bg-gray-800 text-white font-medium'
                  : 'text-gray-300 hover:bg-gray-800 hover:text-white'
              }`}
            >
              <span>{item.icon}</span>
              <span>{item.label}</span>
            </Link>
          );
        })}
      </nav>

      {/* Connect Wallet Button */}
      <div className="p-4 border-t border-gray-800 mt-auto">
        <button className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-white hover:bg-gray-100 text-gray-900 rounded-full text-sm font-bold transition-all shadow-lg">
          <Wallet className="w-4 h-4" />
          <span>Connect</span>
        </button>
      </div>
    </aside>
    </>
  );
}
