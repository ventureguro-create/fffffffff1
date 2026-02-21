/**
 * Telegram Channel Overview Page (UI-FREEZE-1)
 * Channel detail view with all sections from design reference
 */
import { useState, useEffect, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import { 
  ArrowLeft, 
  RefreshCw, 
  Users, 
  Eye, 
  MessageCircle, 
  Activity,
  ExternalLink,
  TrendingUp,
  TrendingDown,
  Shield,
  AlertTriangle,
  Star,
  Clock,
  BarChart3,
  Loader2
} from 'lucide-react';

const API_BASE = process.env.REACT_APP_BACKEND_URL || '';

export default function TelegramChannelOverviewPage() {
  const { username } = useParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [refreshing, setRefreshing] = useState(false);

  const fetchData = useCallback(async () => {
    if (!username) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const res = await fetch(`${API_BASE}/api/telegram-intel/channel/${username}/overview`);
      if (!res.ok) throw new Error(`Error: ${res.status}`);
      const json = await res.json();
      setData(json);
    } catch (err) {
      console.error('[Channel] Fetch error:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [username]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleRefresh = async () => {
    setRefreshing(true);
    try {
      await fetch(`${API_BASE}/api/telegram-intel/channel/${username}/refresh`, {
        method: 'POST'
      });
      await fetchData();
    } catch (err) {
      console.error('[Channel] Refresh error:', err);
    } finally {
      setRefreshing(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Loader2 className="w-8 h-8 text-teal-500 animate-spin" />
      </div>
    );
  }

  if (error || !data?.ok) {
    return (
      <div className="min-h-screen bg-gray-50 px-6 py-6">
        <Link to="/telegram" className="flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-6">
          <ArrowLeft className="w-4 h-4" /> Back to Entities
        </Link>
        <div className="bg-red-50 border border-red-200 text-red-700 px-6 py-4 rounded-xl">
          {error || 'Channel not found'}
        </div>
      </div>
    );
  }

  const { profile, topCards, aiSummary, activityOverview, audienceSnapshot, productOverview, channelSnapshot, healthSafety, relatedChannels, timeline, recentPosts, metrics } = data;

  return (
    <div className="min-h-screen bg-gray-50" data-testid="channel-overview-page">
      <div className="max-w-[1400px] mx-auto px-6 py-6">
        {/* Back Link */}
        <Link to="/telegram" className="flex items-center gap-2 text-gray-600 hover:text-teal-600 mb-6 transition-colors">
          <ArrowLeft className="w-4 h-4" /> Back to Entities
        </Link>

        {/* Main Grid: 8 + 4 columns */}
        <div className="grid grid-cols-12 gap-6">
          {/* Left Column (8 cols) */}
          <div className="col-span-12 lg:col-span-8 space-y-6">
            {/* Channel Header */}
            <ChannelHeader 
              profile={profile} 
              onRefresh={handleRefresh} 
              refreshing={refreshing}
              metrics={metrics}
            />

            {/* Top Cards Row */}
            <div className="grid grid-cols-4 gap-4">
              <TopCard 
                label="Subscribers" 
                value={formatNumber(topCards?.subscribers)} 
                icon={<Users className="w-5 h-5 text-teal-500" />}
              />
              <TopCard 
                label="Views/Post" 
                value={formatNumber(topCards?.viewsPerPost)} 
                icon={<Eye className="w-5 h-5 text-blue-500" />}
              />
              <TopCard 
                label="Messages/Day" 
                value={topCards?.messagesPerDay?.toFixed(1)} 
                icon={<MessageCircle className="w-5 h-5 text-violet-500" />}
              />
              <TopCard 
                label="Activity Level" 
                value={topCards?.activityLevel} 
                icon={<Activity className="w-5 h-5 text-amber-500" />}
                badge
              />
            </div>

            {/* 3-column section */}
            <div className="grid grid-cols-3 gap-4">
              {/* Activity Overview */}
              <div className="bg-white rounded-xl border border-gray-200 p-5">
                <h3 className="text-sm font-semibold text-gray-900 mb-4">Activity Overview</h3>
                <div className="space-y-3">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-500">Posts/Day</span>
                    <span className="font-medium text-gray-900">{activityOverview?.postsPerDay?.toFixed(1)}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-500">Active Days</span>
                    <span className="font-medium text-gray-900">{activityOverview?.activeDays}/7</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-500">Peak Hour</span>
                    <span className="font-medium text-gray-900">{activityOverview?.peakHour}:00</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-500">Consistency</span>
                    <span className="font-medium text-gray-900">{(activityOverview?.consistency * 100)?.toFixed(0)}%</span>
                  </div>
                </div>
              </div>

              {/* Audience Snapshot */}
              <div className="bg-white rounded-xl border border-gray-200 p-5">
                <h3 className="text-sm font-semibold text-gray-900 mb-4">Audience Snapshot</h3>
                <div className="space-y-3">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-500">Total</span>
                    <span className="font-medium text-gray-900">{formatNumber(audienceSnapshot?.total)}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-500">Growth 7D</span>
                    <span className={`font-medium ${audienceSnapshot?.growth7d >= 0 ? 'text-emerald-600' : 'text-red-500'}`}>
                      {audienceSnapshot?.growth7d >= 0 ? '+' : ''}{audienceSnapshot?.growth7d?.toFixed(1)}%
                    </span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-500">Growth 30D</span>
                    <span className={`font-medium ${audienceSnapshot?.growth30d >= 0 ? 'text-emerald-600' : 'text-red-500'}`}>
                      {audienceSnapshot?.growth30d >= 0 ? '+' : ''}{audienceSnapshot?.growth30d?.toFixed(1)}%
                    </span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-500">Engagement</span>
                    <span className="font-medium text-gray-900">{(audienceSnapshot?.engagementRate * 100)?.toFixed(1)}%</span>
                  </div>
                </div>
              </div>

              {/* Product Overview */}
              <div className="bg-white rounded-xl border border-gray-200 p-5">
                <h3 className="text-sm font-semibold text-gray-900 mb-4">Product Overview</h3>
                <div className="space-y-3">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-500">Category</span>
                    <span className="font-medium text-gray-900">{productOverview?.category}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-500">Language</span>
                    <span className="font-medium text-gray-900">{productOverview?.language}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-500">Monetization</span>
                    <span className="font-medium text-gray-900">{productOverview?.monetization}</span>
                  </div>
                  <div className="text-sm">
                    <span className="text-gray-500">Topics: </span>
                    <span className="font-medium text-gray-900">{productOverview?.topics?.slice(0, 3).join(', ')}</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Engagement Timeline */}
            <div className="bg-white rounded-xl border border-gray-200 p-6">
              <div className="flex items-center justify-between mb-6">
                <h3 className="font-semibold text-gray-900">Engagement Timeline</h3>
                <div className="flex gap-2">
                  {['24H', '7D', '30D', '90D'].map((period) => (
                    <button 
                      key={period}
                      className="px-3 py-1 text-xs font-medium rounded-lg bg-gray-100 text-gray-600 hover:bg-teal-100 hover:text-teal-700 transition-colors"
                    >
                      {period}
                    </button>
                  ))}
                </div>
              </div>
              <div className="h-48 flex items-end justify-between gap-1">
                {timeline?.slice(0, 30).map((point, i) => (
                  <div 
                    key={i}
                    className="flex-1 bg-teal-400 hover:bg-teal-500 rounded-t transition-colors"
                    style={{ 
                      height: `${Math.min(100, (point.views / (topCards?.viewsPerPost || 10000)) * 100)}%`,
                      minHeight: '4px'
                    }}
                    title={`${point.date}: ${formatNumber(point.views)} views`}
                  />
                ))}
              </div>
            </div>

            {/* Recent Posts */}
            <div className="bg-white rounded-xl border border-gray-200 p-6">
              <h3 className="font-semibold text-gray-900 mb-4">Recent Posts</h3>
              <div className="space-y-4">
                {recentPosts?.slice(0, 5).map((post, i) => (
                  <div key={post.id || i} className="border-b border-gray-100 pb-4 last:border-0 last:pb-0">
                    <p className="text-sm text-gray-700 mb-2 line-clamp-2">{post.text}</p>
                    <div className="flex items-center gap-4 text-xs text-gray-500">
                      <span className="flex items-center gap-1">
                        <Eye className="w-3 h-3" /> {formatNumber(post.views)}
                      </span>
                      <span className="flex items-center gap-1">
                        <TrendingUp className="w-3 h-3" /> {post.forwards}
                      </span>
                      <span className="flex items-center gap-1">
                        <MessageCircle className="w-3 h-3" /> {post.replies}
                      </span>
                      <span className="flex items-center gap-1">
                        <Clock className="w-3 h-3" /> {formatDate(post.date)}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Right Column (4 cols) */}
          <div className="col-span-12 lg:col-span-4 space-y-6">
            {/* AI Summary */}
            <div className="bg-gradient-to-br from-teal-50 to-blue-50 rounded-xl border border-teal-100 p-5">
              <div className="flex items-center gap-2 mb-3">
                <Star className="w-4 h-4 text-teal-600" />
                <h3 className="text-sm font-semibold text-teal-800">AI Summary</h3>
              </div>
              <p className="text-sm text-teal-700 leading-relaxed">{aiSummary}</p>
            </div>

            {/* Channel Snapshot (Live) */}
            <div className="bg-white rounded-xl border border-gray-200 p-5">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-semibold text-gray-900">Channel Snapshot</h3>
                {channelSnapshot?.live && (
                  <span className="flex items-center gap-1 text-xs text-emerald-600">
                    <span className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse" />
                    Live
                  </span>
                )}
              </div>
              <div className="space-y-3">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Last Post</span>
                  <span className="font-medium text-gray-900">{formatDate(channelSnapshot?.lastPost)}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Total Posts</span>
                  <span className="font-medium text-gray-900">{formatNumber(channelSnapshot?.totalPosts)}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Avg Views</span>
                  <span className="font-medium text-gray-900">{formatNumber(channelSnapshot?.avgViews)}</span>
                </div>
              </div>
            </div>

            {/* Health & Safety */}
            <div className="bg-white rounded-xl border border-gray-200 p-5">
              <h3 className="text-sm font-semibold text-gray-900 mb-4">Health & Safety</h3>
              <div className="space-y-4">
                <ProgressBar 
                  label="Trust Score" 
                  value={healthSafety?.trustScore} 
                  color="teal"
                />
                <ProgressBar 
                  label="Stability" 
                  value={healthSafety?.stability * 100} 
                  color="blue"
                />
                <ProgressBar 
                  label="Fraud Risk" 
                  value={healthSafety?.fraudRisk * 100} 
                  color="rose"
                  inverted
                />
                <div className="flex items-center justify-between text-sm pt-2 border-t border-gray-100">
                  <span className="text-gray-500 flex items-center gap-1">
                    <AlertTriangle className="w-4 h-4 text-rose-400" />
                    Red Flags
                  </span>
                  <span className="font-semibold text-rose-600">{healthSafety?.redFlags}</span>
                </div>
              </div>
            </div>

            {/* Related Channels */}
            <div className="bg-white rounded-xl border border-gray-200 p-5">
              <h3 className="text-sm font-semibold text-gray-900 mb-4">Related Channels</h3>
              <div className="space-y-3">
                {relatedChannels?.slice(0, 4).map((ch, i) => (
                  <Link 
                    key={ch.username || i}
                    to={`/telegram/${ch.username}`}
                    className="flex items-center gap-3 p-2 rounded-lg hover:bg-gray-50 transition-colors"
                  >
                    <div 
                      className="w-8 h-8 rounded-full flex items-center justify-center text-white text-xs font-semibold"
                      style={{ backgroundColor: ch.avatarColor }}
                    >
                      {ch.title?.substring(0, 2).toUpperCase()}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="text-sm font-medium text-gray-900 truncate">{ch.title}</div>
                      <div className="text-xs text-gray-500">{formatNumber(ch.members)} members</div>
                    </div>
                    <div className="text-xs font-medium text-teal-600">{ch.utilityScore}</div>
                  </Link>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// Sub-components

function ChannelHeader({ profile, onRefresh, refreshing, metrics }) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-6">
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-4">
          <div 
            className="w-16 h-16 rounded-full flex items-center justify-center text-white text-xl font-bold"
            style={{ backgroundColor: profile?.avatarColor || '#1976D2' }}
          >
            {profile?.title?.substring(0, 2).toUpperCase() || '??'}
          </div>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{profile?.title}</h1>
            <div className="flex items-center gap-2 mt-1">
              <span className="text-gray-500">@{profile?.username}</span>
              <span className="px-2 py-0.5 bg-gray-100 text-gray-600 text-xs rounded-full">{profile?.type}</span>
            </div>
            {profile?.about && (
              <p className="text-sm text-gray-600 mt-2 max-w-xl">{profile.about}</p>
            )}
          </div>
        </div>
        <div className="flex items-center gap-4">
          <div className="text-right">
            <div className="text-3xl font-bold text-teal-600">{metrics?.utilityScore || '—'}</div>
            <div className="text-xs text-gray-500">FOMO Score</div>
          </div>
          <button
            onClick={onRefresh}
            disabled={refreshing}
            className="p-2 rounded-lg hover:bg-gray-100 transition-colors disabled:opacity-50"
            title="Refresh channel data"
            data-testid="refresh-button"
          >
            <RefreshCw className={`w-5 h-5 text-gray-500 ${refreshing ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>
    </div>
  );
}

function TopCard({ label, value, icon, badge }) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-4">
      <div className="flex items-center gap-2 mb-2">
        {icon}
        <span className="text-xs text-gray-500">{label}</span>
      </div>
      {badge ? (
        <span className={`inline-flex px-3 py-1 text-sm font-medium rounded-full ${
          value === 'High' ? 'bg-teal-100 text-teal-700' :
          value === 'Medium' ? 'bg-amber-100 text-amber-700' :
          'bg-rose-100 text-rose-600'
        }`}>
          {value || '—'}
        </span>
      ) : (
        <div className="text-xl font-bold text-gray-900">{value || '—'}</div>
      )}
    </div>
  );
}

function ProgressBar({ label, value, color, inverted }) {
  const colorMap = {
    teal: 'bg-teal-500',
    blue: 'bg-blue-500',
    rose: 'bg-rose-500',
  };
  
  return (
    <div>
      <div className="flex justify-between text-sm mb-1">
        <span className="text-gray-500">{label}</span>
        <span className="font-medium text-gray-900">{value?.toFixed(0)}%</span>
      </div>
      <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
        <div 
          className={`h-full rounded-full transition-all ${colorMap[color]}`}
          style={{ width: `${Math.min(100, value || 0)}%` }}
        />
      </div>
    </div>
  );
}

// Utility functions

function formatNumber(num) {
  if (num === null || num === undefined) return '—';
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
  if (num >= 1000) return (num / 1000).toFixed(num >= 10000 ? 0 : 1) + 'k';
  return num.toString();
}

function formatDate(dateStr) {
  if (!dateStr) return '—';
  try {
    const date = new Date(dateStr);
    const now = new Date();
    const diffHours = Math.floor((now - date) / (1000 * 60 * 60));
    
    if (diffHours < 1) return 'Just now';
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffHours < 48) return 'Yesterday';
    if (diffHours < 168) return `${Math.floor(diffHours / 24)}d ago`;
    
    return date.toLocaleDateString();
  } catch {
    return '—';
  }
}
