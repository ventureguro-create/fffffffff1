/**
 * Telegram Entities Overview Page (Production)
 * Connected to real backend with URL-driven filters
 */
import { useState, useEffect, useCallback } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { 
  Search, 
  Filter, 
  Star, 
  ThumbsUp,
  ChevronLeft, 
  ChevronRight,
  RefreshCw,
  Loader2
} from 'lucide-react';
import TelegramFilterDrawer from '../components/telegram/TelegramFilterDrawer';
import { Sparkline } from '../modules/telegram/components/Sparkline';

const API_BASE = process.env.REACT_APP_BACKEND_URL || '';

export default function TelegramEntitiesPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filterOpen, setFilterOpen] = useState(false);
  const [searchInput, setSearchInput] = useState(searchParams.get('q') || '');

  // Build API URL from search params
  const buildApiUrl = useCallback(() => {
    const params = new URLSearchParams();
    
    // Transfer all search params to API
    searchParams.forEach((value, key) => {
      params.set(key, value);
    });
    
    // Ensure defaults
    if (!params.has('limit')) params.set('limit', '20');
    if (!params.has('page')) params.set('page', '1');
    
    return `${API_BASE}/api/telegram-intel/utility/list?${params.toString()}`;
  }, [searchParams]);

  // Fetch data
  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      const url = buildApiUrl();
      const res = await fetch(url);
      
      if (!res.ok) {
        throw new Error(`API error: ${res.status}`);
      }
      
      const json = await res.json();
      setData(json);
    } catch (err) {
      console.error('[Entities] Fetch error:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [buildApiUrl]);

  // Fetch on mount and when params change
  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // Handle search submit
  const handleSearch = (e) => {
    e.preventDefault();
    const newParams = new URLSearchParams(searchParams);
    if (searchInput.trim()) {
      newParams.set('q', searchInput.trim());
    } else {
      newParams.delete('q');
    }
    newParams.set('page', '1');
    setSearchParams(newParams);
  };

  // Handle pagination
  const goToPage = (page) => {
    const newParams = new URLSearchParams(searchParams);
    newParams.set('page', String(page));
    setSearchParams(newParams);
  };

  const currentPage = Number(searchParams.get('page')) || 1;
  const limit = Number(searchParams.get('limit')) || 20;
  const total = data?.total || 0;
  const totalPages = Math.ceil(total / limit);
  const items = data?.items || [];
  const stats = data?.stats || { tracked: 0, avgUtility: 0, highGrowth: 0, highRisk: 0 };

  // Count active filters
  const activeFilters = Array.from(searchParams.entries()).filter(
    ([key]) => !['page', 'limit', 'q'].includes(key)
  ).length;

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-[1400px] mx-auto px-6 py-6">
        {/* Top Row: Search + Stats */}
        <div className="flex items-center justify-between mb-6">
          {/* Search Form */}
          <form onSubmit={handleSearch} className="relative w-96">
            <input
              type="text"
              placeholder="Search for a project, fund or person..."
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
              className="w-full px-4 py-2.5 border border-gray-200 rounded-lg text-sm bg-white focus:outline-none focus:ring-2 focus:ring-teal-100 focus:border-teal-400"
              data-testid="entity-search"
            />
          </form>

          {/* Stats Cards */}
          <div className="flex items-center gap-6">
            <StatCard label="Tracked" value={stats.tracked} color="teal" />
            <StatCard label="Avg Score" value={stats.avgUtility} color="teal" />
            <StatCard label="High Growth" value={stats.highGrowth} color="emerald" />
            <StatCard label="High Risk" value={stats.highRisk} color="rose" />
          </div>
        </div>

        {/* Title Row with Filter Button */}
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-xl font-semibold text-gray-900">Entities Overview</h1>

          <div className="flex items-center gap-3">
            {/* Social Platform Icons */}
            <div className="flex items-center gap-1">
              {/* X/Twitter */}
              <button className="w-9 h-9 rounded-lg border border-gray-200 flex items-center justify-center text-gray-600 hover:bg-gray-50 hover:border-gray-300 transition-colors">
                <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
                </svg>
              </button>
              {/* Discord */}
              <button className="w-9 h-9 rounded-lg border border-gray-200 flex items-center justify-center text-gray-600 hover:bg-gray-50 hover:border-gray-300 transition-colors">
                <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M20.317 4.37a19.791 19.791 0 0 0-4.885-1.515.074.074 0 0 0-.079.037c-.21.375-.444.864-.608 1.25a18.27 18.27 0 0 0-5.487 0 12.64 12.64 0 0 0-.617-1.25.077.077 0 0 0-.079-.037A19.736 19.736 0 0 0 3.677 4.37a.07.07 0 0 0-.032.027C.533 9.046-.32 13.58.099 18.057a.082.082 0 0 0 .031.057 19.9 19.9 0 0 0 5.993 3.03.078.078 0 0 0 .084-.028 14.09 14.09 0 0 0 1.226-1.994.076.076 0 0 0-.041-.106 13.107 13.107 0 0 1-1.872-.892.077.077 0 0 1-.008-.128 10.2 10.2 0 0 0 .372-.292.074.074 0 0 1 .077-.01c3.928 1.793 8.18 1.793 12.062 0a.074.074 0 0 1 .078.01c.12.098.246.198.373.292a.077.077 0 0 1-.006.127 12.299 12.299 0 0 1-1.873.892.077.077 0 0 0-.041.107c.36.698.772 1.362 1.225 1.993a.076.076 0 0 0 .084.028 19.839 19.839 0 0 0 6.002-3.03.077.077 0 0 0 .032-.054c.5-5.177-.838-9.674-3.549-13.66a.061.061 0 0 0-.031-.03zM8.02 15.33c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.956-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.956 2.418-2.157 2.418zm7.975 0c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.955-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.946 2.418-2.157 2.418z"/>
                </svg>
              </button>
              {/* Telegram */}
              <button className="w-9 h-9 rounded-lg border border-teal-200 bg-teal-50 flex items-center justify-center text-teal-600 hover:bg-teal-100 transition-colors">
                <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a12 12 0 0 0-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z"/>
                </svg>
              </button>
              {/* Instagram */}
              <button className="w-9 h-9 rounded-lg border border-gray-200 flex items-center justify-center text-gray-600 hover:bg-gray-50 hover:border-gray-300 transition-colors">
                <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24c3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0zm0 5.838a6.162 6.162 0 1 0 0 12.324 6.162 6.162 0 0 0 0-12.324zM12 16a4 4 0 1 1 0-8 4 4 0 0 1 0 8zm6.406-11.845a1.44 1.44 0 1 0 0 2.881 1.44 1.44 0 0 0 0-2.881z"/>
                </svg>
              </button>
              {/* LinkedIn */}
              <button className="w-9 h-9 rounded-lg border border-gray-200 flex items-center justify-center text-gray-600 hover:bg-gray-50 hover:border-gray-300 transition-colors">
                <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
                </svg>
              </button>
              {/* TikTok */}
              <button className="w-9 h-9 rounded-lg border border-gray-200 flex items-center justify-center text-gray-600 hover:bg-gray-50 hover:border-gray-300 transition-colors">
                <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12.525.02c1.31-.02 2.61-.01 3.91-.02.08 1.53.63 3.09 1.75 4.17 1.12 1.11 2.7 1.62 4.24 1.79v4.03c-1.44-.05-2.89-.35-4.2-.97-.57-.26-1.1-.59-1.62-.93-.01 2.92.01 5.84-.02 8.75-.08 1.4-.54 2.79-1.35 3.94-1.31 1.92-3.58 3.17-5.91 3.21-1.43.08-2.86-.31-4.08-1.03-2.02-1.19-3.44-3.37-3.65-5.71-.02-.5-.03-1-.01-1.49.18-1.9 1.12-3.72 2.58-4.96 1.66-1.44 3.98-2.13 6.15-1.72.02 1.48-.04 2.96-.04 4.44-.99-.32-2.15-.23-3.02.37-.63.41-1.11 1.04-1.36 1.75-.21.51-.15 1.07-.14 1.61.24 1.64 1.82 3.02 3.5 2.87 1.12-.01 2.19-.66 2.77-1.61.19-.33.4-.67.41-1.06.1-1.79.06-3.57.07-5.36.01-4.03-.01-8.05.02-12.07z"/>
                </svg>
              </button>
              {/* Spotify */}
              <button className="w-9 h-9 rounded-lg border border-gray-200 flex items-center justify-center text-gray-600 hover:bg-gray-50 hover:border-gray-300 transition-colors">
                <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 0C5.4 0 0 5.4 0 12s5.4 12 12 12 12-5.4 12-12S18.66 0 12 0zm5.521 17.34c-.24.359-.66.48-1.021.24-2.82-1.74-6.36-2.101-10.561-1.141-.418.122-.779-.179-.899-.539-.12-.421.18-.78.54-.9 4.56-1.021 8.52-.6 11.64 1.32.42.18.479.659.301 1.02zm1.44-3.3c-.301.42-.841.6-1.262.3-3.239-1.98-8.159-2.58-11.939-1.38-.479.12-1.02-.12-1.14-.6-.12-.48.12-1.021.6-1.141C9.6 9.9 15 10.561 18.72 12.84c.361.181.54.78.241 1.2zm.12-3.36C15.24 8.4 8.82 8.16 5.16 9.301c-.6.179-1.2-.181-1.38-.721-.18-.601.18-1.2.72-1.381 4.26-1.26 11.28-1.02 15.721 1.621.539.3.719 1.02.419 1.56-.299.421-1.02.599-1.559.3z"/>
                </svg>
              </button>
            </div>

            {/* Ad Mode */}
            <button className="flex items-center gap-2 px-4 py-2 border border-gray-200 rounded-lg text-sm bg-white hover:bg-gray-50">
              <svg className="w-4 h-4 text-gray-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <rect x="3" y="3" width="18" height="18" rx="2"/>
                <path d="M3 9h18M9 21V9"/>
              </svg>
              <span>Ad Mode</span>
            </button>

            {/* Filter Button */}
            <button 
              onClick={() => setFilterOpen(true)}
              className="flex items-center gap-2 px-4 py-2 border border-gray-200 rounded-lg text-sm bg-white hover:bg-gray-50 relative"
              data-testid="filter-button"
            >
              <Filter className="w-4 h-4 text-gray-500" />
              <span>Filter</span>
              {activeFilters > 0 && (
                <span className="absolute -top-1 -right-1 w-5 h-5 bg-teal-500 text-white text-xs rounded-full flex items-center justify-center">
                  {activeFilters}
                </span>
              )}
            </button>
          </div>
        </div>

        {/* Loading State */}
        {loading && (
          <div className="bg-white rounded-xl border border-gray-200 p-12 flex items-center justify-center">
            <Loader2 className="w-8 h-8 text-teal-500 animate-spin" />
          </div>
        )}

        {/* Error State */}
        {error && !loading && (
          <div className="bg-white rounded-xl border border-red-200 p-8 text-center">
            <p className="text-red-600 mb-4">{error}</p>
            <button 
              onClick={fetchData}
              className="px-4 py-2 bg-red-100 text-red-700 rounded-lg text-sm hover:bg-red-200"
            >
              Retry
            </button>
          </div>
        )}

        {/* Table */}
        {!loading && !error && (
          <div className="bg-white rounded-xl border border-gray-200 overflow-hidden" data-testid="entities-table">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-100">
                  <th className="text-left px-6 py-4 text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Channel/Group
                  </th>
                  <th className="text-left px-4 py-4 text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Type
                  </th>
                  <th className="text-right px-4 py-4 text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Members
                  </th>
                  <th className="text-right px-4 py-4 text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Avg Reach
                  </th>
                  <th className="text-center px-4 py-4 text-xs font-medium text-gray-500 uppercase tracking-wider w-24">
                    Trend
                  </th>
                  <th className="text-right px-4 py-4 text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Growth (7D)
                  </th>
                  <th className="text-center px-4 py-4 text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Activity
                  </th>
                  <th className="text-center px-4 py-4 text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Red Flags
                  </th>
                  <th className="text-right px-6 py-4 text-xs font-medium text-gray-500 uppercase tracking-wider">
                    FOMO Score
                  </th>
                </tr>
              </thead>
              <tbody>
                {items.length === 0 ? (
                  <tr>
                    <td colSpan={9} className="px-6 py-12 text-center text-gray-500">
                      No entities found matching your filters.
                    </td>
                  </tr>
                ) : (
                  items.map((entity) => (
                    <EntityRow key={entity.username} entity={entity} />
                  ))
                )}
              </tbody>
            </table>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex items-center justify-between px-6 py-4 border-t border-gray-100">
                <button 
                  onClick={() => goToPage(currentPage - 1)}
                  disabled={currentPage === 1}
                  className="p-2 rounded-lg hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <ChevronLeft className="w-5 h-5 text-gray-500" />
                </button>

                <div className="flex items-center gap-2">
                  {generatePageNumbers(currentPage, totalPages).map((p, i) => (
                    p === '...' ? (
                      <span key={`ellipsis-${i}`} className="text-gray-400">...</span>
                    ) : (
                      <button
                        key={p}
                        onClick={() => goToPage(p)}
                        className={`w-8 h-8 rounded-full text-sm font-medium transition-colors ${
                          currentPage === p 
                            ? 'bg-teal-500 text-white' 
                            : 'text-gray-600 hover:bg-gray-100'
                        }`}
                      >
                        {p}
                      </button>
                    )
                  ))}
                </div>

                <div className="flex items-center gap-4">
                  <span className="text-sm text-gray-500">
                    Showing {(currentPage - 1) * limit + 1} – {Math.min(currentPage * limit, total)} of {total}
                  </span>
                  <button 
                    onClick={() => goToPage(currentPage + 1)}
                    disabled={currentPage >= totalPages}
                    className="p-2 rounded-lg hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <ChevronRight className="w-5 h-5 text-gray-500" />
                  </button>
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Filter Drawer */}
      <TelegramFilterDrawer 
        open={filterOpen} 
        onClose={() => setFilterOpen(false)} 
      />
    </div>
  );
}

function StatCard({ label, value, color }) {
  const colorMap = {
    teal: 'text-teal-600',
    emerald: 'text-emerald-600',
    rose: 'text-rose-600',
  };
  
  return (
    <div className="text-right">
      <div className="text-xs text-gray-500">{label}:</div>
      <div className={`text-lg font-semibold ${colorMap[color] || colorMap.teal}`}>
        {value}
      </div>
    </div>
  );
}

function EntityRow({ entity }) {
  return (
    <tr 
      className="border-b border-gray-50 hover:bg-gray-50/50 transition-colors"
      data-testid={`entity-row-${entity.username}`}
    >
      {/* Channel/Group */}
      <td className="px-6 py-4">
        <Link to={`/telegram/${entity.username}`} className="flex items-center gap-3">
          <div 
            className="w-8 h-8 rounded-full flex items-center justify-center text-white text-xs font-semibold"
            style={{ backgroundColor: entity.avatarColor }}
          >
            {entity.title?.substring(0, 2).toUpperCase() || entity.username.substring(0, 2).toUpperCase()}
          </div>
          <span className="font-medium text-gray-900 hover:text-teal-600 transition-colors">
            {entity.title || entity.username}
          </span>
        </Link>
      </td>

      {/* Type */}
      <td className="px-4 py-4 text-sm text-gray-600">
        {entity.type}
      </td>

      {/* Members */}
      <td className="px-4 py-4 text-sm text-gray-900 text-right font-medium">
        {formatNumber(entity.members)}
      </td>

      {/* Avg Reach */}
      <td className="px-4 py-4 text-sm text-gray-900 text-right font-medium">
        {formatNumber(entity.avgReach)}
      </td>

      {/* Trend Sparkline */}
      <td className="px-4 py-4">
        <div className="w-20 h-6">
          <Sparkline 
            data={entity.sparkline || []} 
            height={24} 
            color={entity.growth7 >= 0 ? '#10b981' : '#ef4444'} 
          />
        </div>
      </td>

      {/* Growth (7D) */}
      <td className={`px-4 py-4 text-sm text-right font-medium ${
        entity.growth7 >= 0 ? 'text-emerald-600' : 'text-red-500'
      }`}>
        {entity.growth7 >= 0 ? '+' : ''}{entity.growth7?.toFixed(1) || '0.0'}%
      </td>

      {/* Activity Badge */}
      <td className="px-4 py-4 text-center">
        <ActivityBadge level={entity.activity || entity.activityLabel} />
      </td>

      {/* Red Flags */}
      <td className="px-4 py-4 text-center">
        <div className="flex items-center justify-center gap-1">
          <span className="text-sm text-gray-700">{entity.redFlags || 0}</span>
          <svg className="w-4 h-4 text-red-400" viewBox="0 0 24 24" fill="currentColor">
            <path d="M4 2v20h2v-8h12l-2-4 2-4H6V2H4z"/>
          </svg>
        </div>
      </td>

      {/* FOMO Score */}
      <td className="px-6 py-4 text-right">
        <div className="flex items-center justify-end gap-2">
          <span className="text-sm font-semibold text-gray-900">{entity.fomoScore || entity.utilityScore}</span>
          <Star className="w-4 h-4 text-amber-400 fill-amber-400" />
          {entity.engagement !== null && entity.engagement !== undefined && (
            <>
              <span className="text-sm text-gray-500">{formatNumber(entity.engagement)}</span>
              <ThumbsUp className="w-4 h-4 text-teal-500" />
            </>
          )}
        </div>
      </td>
    </tr>
  );
}

function ActivityBadge({ level }) {
  const styles = {
    High: 'bg-teal-100 text-teal-700 border-teal-200',
    Medium: 'bg-amber-100 text-amber-700 border-amber-200',
    Low: 'bg-rose-100 text-rose-600 border-rose-200',
  };

  return (
    <span className={`inline-flex px-3 py-1 text-xs font-medium rounded-full border ${styles[level] || styles.Medium}`}>
      {level || 'Medium'}
    </span>
  );
}

function formatNumber(num) {
  if (num === null || num === undefined) return '—';
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
  if (num >= 1000) return (num / 1000).toFixed(num >= 10000 ? 0 : 1) + 'k';
  return num.toString();
}

function generatePageNumbers(current, total) {
  const pages = [];
  const delta = 2;

  for (let i = 1; i <= total; i++) {
    if (i === 1 || i === total || (i >= current - delta && i <= current + delta)) {
      pages.push(i);
    } else if (pages[pages.length - 1] !== '...') {
      pages.push('...');
    }
  }

  return pages;
}
