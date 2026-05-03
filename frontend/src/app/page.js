'use client';
import { useState, useEffect, useCallback, useRef } from 'react';
import TaskCard from '../components/TaskCard';
import ConflictModal from '../components/ConflictModal';

const API = 'http://localhost:8000';

// ── Dummy data for Guest Mode ───────────────────────────────────
const GUEST_COURSES = [
  { id: 'g1', name: 'CS 301 – Data Structures & Algorithms', description: 'Advanced trees, graphs, and dynamic programming.', external_id: null },
  { id: 'g2', name: 'MATH 250 – Linear Algebra', description: 'Vector spaces, eigenvalues, and matrix decompositions.', external_id: null },
  { id: 'g3', name: 'PHY 201 – Classical Mechanics', description: 'Lagrangian and Hamiltonian formulations of mechanics.', external_id: null },
  { id: 'g4', name: 'ENG 102 – Technical Writing', description: 'Reports, documentation, and research papers.', external_id: null },
  { id: 'g5', name: 'CS 410 – Machine Learning', description: 'Supervised, unsupervised learning, and neural networks.', external_id: null },
];

const GUEST_TASKS = [
  { id: 't1', title: 'Binary Search Tree Implementation', course: 'CS 301 – DSA', priority_score: 88.5, effort_estimate_hrs: 4, due_date: new Date(Date.now() + 2 * 86400000).toISOString(), status: 'PENDING' },
  { id: 't2', title: 'Eigenvalue Problem Set #7', course: 'MATH 250 – Linear Algebra', priority_score: 76.2, effort_estimate_hrs: 3, due_date: new Date(Date.now() + 3 * 86400000).toISOString(), status: 'PENDING' },
  { id: 't3', title: 'Lagrangian Mechanics Lab Report', course: 'PHY 201 – Classical Mechanics', priority_score: 91.0, effort_estimate_hrs: 5, due_date: new Date(Date.now() + 1 * 86400000).toISOString(), status: 'PENDING' },
  { id: 't4', title: 'Research Paper Draft – AI Ethics', course: 'ENG 102 – Technical Writing', priority_score: 62.3, effort_estimate_hrs: 6, due_date: new Date(Date.now() + 5 * 86400000).toISOString(), status: 'PENDING' },
  { id: 't5', title: 'Neural Network from Scratch (NumPy)', course: 'CS 410 – Machine Learning', priority_score: 83.7, effort_estimate_hrs: 8, due_date: new Date(Date.now() + 4 * 86400000).toISOString(), status: 'PENDING' },
  { id: 't6', title: 'Graph Traversal Quiz Prep', course: 'CS 301 – DSA', priority_score: 45.0, effort_estimate_hrs: 1.5, due_date: new Date(Date.now() + 7 * 86400000).toISOString(), status: 'COMPLETED' },
];

function getToken() {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('axiom_token');
}

function authHeaders() {
  const token = getToken();
  if (!token) return {};
  return { 'Authorization': `Bearer ${token}` };
}

export default function Dashboard() {
  const [tasks, setTasks] = useState([]);
  const [courses, setCourses] = useState([]);
  const [activeConflict, setActiveConflict] = useState(null);
  const [syncing, setSyncing] = useState(false);
  const [syncMsg, setSyncMsg] = useState(null);
  const [loading, setLoading] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [isGuest, setIsGuest] = useState(false);
  const [userName, setUserName] = useState('');
  // `initializing` is true until the first client-side auth check completes.
  // While true, we render nothing to avoid the flash.
  const [initializing, setInitializing] = useState(true);
  const initRan = useRef(false);

  // On mount: check for token in URL (from OAuth callback redirect) or localStorage
  useEffect(() => {
    // Strict-mode guard: only run once
    if (initRan.current) return;
    initRan.current = true;

    const params = new URLSearchParams(window.location.search);
    const urlToken = params.get('token');
    const name = params.get('name');

    if (urlToken) {
      localStorage.setItem('axiom_token', urlToken);
      if (name) localStorage.setItem('axiom_user_name', name);
      window.history.replaceState({}, '', '/');
    }

    const token = localStorage.getItem('axiom_token');
    if (token) {
      setIsLoggedIn(true);
      setUserName(localStorage.getItem('axiom_user_name') || 'Student');
    }
    // Done checking – stop initializing
    setInitializing(false);
  }, []);

  const fetchData = useCallback(async () => {
    if (!getToken()) return;
    setLoading(true);
    try {
      const [coursesRes, tasksRes] = await Promise.all([
        fetch(`${API}/courses/`, { headers: authHeaders() }),
        fetch(`${API}/tasks/`, { headers: authHeaders() }),
      ]);

      if (coursesRes.status === 401 || tasksRes.status === 401) {
        handleLogout();
        return;
      }

      const coursesData = await coursesRes.json();
      const tasksData = await tasksRes.json();

      if (Array.isArray(coursesData)) setCourses(coursesData);
      if (Array.isArray(tasksData)) setTasks(tasksData);
    } catch (err) {
      console.error('Error fetching data:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (isLoggedIn && !isGuest) {
      fetchData();
    }
  }, [isLoggedIn, isGuest, fetchData]);

  const handleLogin = () => {
    window.location.href = `${API}/auth/login`;
  };

  const handleGuestMode = () => {
    setCourses(GUEST_COURSES);
    setTasks([...GUEST_TASKS].sort((a, b) => b.priority_score - a.priority_score));
    setIsGuest(true);
    setIsLoggedIn(true);
    setUserName('Guest');
  };

  const handleLogout = () => {
    localStorage.removeItem('axiom_token');
    localStorage.removeItem('axiom_user_name');
    setIsLoggedIn(false);
    setIsGuest(false);
    setCourses([]);
    setTasks([]);
    setUserName('');
  };

  const handleSyncClassroom = async () => {
    if (isGuest) {
      setSyncMsg('ℹ️ Sync is disabled in Guest Mode. Sign in with Google to sync your real courses.');
      setTimeout(() => setSyncMsg(null), 4000);
      return;
    }
    setSyncing(true);
    setSyncMsg(null);
    try {
      const res = await fetch(`${API}/courses/sync-classroom`, {
        method: 'POST',
        headers: authHeaders(),
      });
      const data = await res.json();
      if (res.ok) {
        setSyncMsg(`✅ Synced! Added ${data.added.length} new, updated ${data.updated.length} existing course(s).`);
        await fetchData();
      } else if (res.status === 401) {
        handleLogout();
      } else {
        setSyncMsg(`❌ Sync failed: ${data.detail || 'Unknown error'}`);
      }
    } catch (err) {
      setSyncMsg(`❌ Could not reach backend: ${err.message}`);
    } finally {
      setSyncing(false);
      setTimeout(() => setSyncMsg(null), 6000);
    }
  };

  const handleResolveConflict = (decision) => {
    console.log('User decision:', decision);
    setActiveConflict(null);
  };

  // ── While initializing, render nothing (prevents flash) ───────
  if (initializing) {
    return null;
  }

  // ── Login Screen ──────────────────────────────────────────────
  if (!isLoggedIn) {
    return (
      <main className="login-container">
        <div className="login-card glass-panel animate-slide-up">
          <div className="login-logo">
            <span className="login-logo-icon">⚡</span>
            <h1>Axiom</h1>
          </div>
          <p className="login-subtitle">Your prioritized study schedule, automatically generated.</p>

          <div className="login-features">
            <div className="login-feature-item">
              <span>📚</span>
              <span>Auto-sync Google Classroom courses</span>
            </div>
            <div className="login-feature-item">
              <span>🤖</span>
              <span>AI-powered task prioritization</span>
            </div>
            <div className="login-feature-item">
              <span>📅</span>
              <span>Smart calendar integration</span>
            </div>
            <div className="login-feature-item">
              <span>📧</span>
              <span>Gmail deadline detection</span>
            </div>
          </div>

          <button className="google-login-btn" onClick={handleLogin} id="google-login-btn">
            <svg width="18" height="18" viewBox="0 0 24 24">
              <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z"/>
              <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
              <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
              <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
            </svg>
            Sign in with Google
          </button>

          <div className="login-divider">
            <span>or</span>
          </div>

          <button className="guest-login-btn" onClick={handleGuestMode} id="guest-login-btn">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
              <circle cx="12" cy="7" r="4"/>
            </svg>
            Continue as Guest
          </button>

          <p className="login-note">Your data stays private. We only read your courses and assignments.</p>
        </div>
      </main>
    );
  }

  // ── Dashboard ─────────────────────────────────────────────────
  return (
    <main className="dashboard-container">
      <header className="header">
        <div>
          <h1>Axiom</h1>
          <p>Your prioritized study schedule, automatically generated.</p>
        </div>
        <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
          <button
            className={syncing ? 'btn-active' : 'btn-primary'}
            onClick={handleSyncClassroom}
            disabled={syncing}
            id="sync-classroom-btn"
            style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}
          >
            {syncing ? (
              <>
                <span className="spinner" />
                Syncing…
              </>
            ) : (
              <>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <polyline points="1 4 1 10 7 10"/>
                  <path d="M3.51 15a9 9 0 1 0 .49-4.5"/>
                </svg>
                Sync Google Classroom
              </>
            )}
          </button>
          <div className="user-badge">
            <span className="user-avatar">{userName.charAt(0).toUpperCase()}</span>
            <span className="user-name">{userName}</span>
            {isGuest && <span className="guest-badge">DEMO</span>}
          </div>
          <button className="btn-outline btn-sm" onClick={handleLogout} id="logout-btn">
            Logout
          </button>
        </div>
      </header>

      {isGuest && (
        <div className="guest-banner" style={{ gridColumn: '1 / -1' }}>
          🎭 <strong>Guest Mode</strong> — You&apos;re viewing demo data. <button className="guest-banner-cta" onClick={handleLogin}>Sign in with Google</button> to see your real courses.
        </div>
      )}

      {syncMsg && (
        <div className="sync-banner" style={{ gridColumn: '1 / -1' }}>
          {syncMsg}
        </div>
      )}

      <div className="main-content">
        <h2>📚 Enrolled Classes</h2>
        {loading ? (
          <div className="skeleton-row">
            {[1, 2, 3].map(i => <div key={i} className="skeleton-card" />)}
          </div>
        ) : courses.length === 0 ? (
          <div className="empty-state glass-panel">
            <span style={{ fontSize: '2rem' }}>🎓</span>
            <p>No classes yet. Click <strong>Sync Google Classroom</strong> to import your courses.</p>
          </div>
        ) : (
          <div className="course-grid">
            {courses.map((course) => (
              <div
                key={course.id}
                className="glass-panel course-card"
                id={`course-${course.id}`}
              >
                <div className="course-card-accent" />
                <div className="course-card-body">
                  <h3 className="course-name">{course.name}</h3>
                  {course.description && (
                    <p className="course-desc">{course.description}</p>
                  )}
                  {course.external_id && (
                    <span className="course-badge">Classroom ID: {course.external_id}</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}

        <h2 style={{ marginTop: '2.5rem' }}>🔥 Up Next For You</h2>
        <div className="task-list">
          {tasks.length === 0 && !loading ? (
            <div className="empty-state glass-panel">
              <span style={{ fontSize: '2rem' }}>✅</span>
              <p>No tasks yet. Tasks will appear here once courses are synced and assignments are found.</p>
            </div>
          ) : (
            tasks.map((task, idx) => (
              <TaskCard key={task.id} task={task} index={idx} />
            ))
          )}
        </div>
      </div>

      <aside className="sidebar">
        <div className="glass-panel stats-panel">
          <h2>📊 Today&apos;s Stats</h2>
          <div className="stats-grid">
            <div className="stat-item">
              <span className="stat-value">{courses.length}</span>
              <span className="stat-label">Courses</span>
            </div>
            <div className="stat-item">
              <span className="stat-value">{tasks.length}</span>
              <span className="stat-label">Tasks</span>
            </div>
            <div className="stat-item">
              <span className="stat-value">
                {tasks.filter(t => t.status === 'COMPLETED').length}
              </span>
              <span className="stat-label">Done</span>
            </div>
            <div className="stat-item">
              <span className="stat-value" style={{ color: 'var(--priority-high)' }}>
                {tasks.filter(t => (t.priority_score || 0) >= 75).length}
              </span>
              <span className="stat-label">High Priority</span>
            </div>
          </div>
        </div>

        <div className="glass-panel" style={{ padding: '1.5rem', marginTop: '1rem' }}>
          <h2 style={{ marginBottom: '1rem' }}>🚀 Quick Actions</h2>
          <button
            className="btn-primary"
            style={{ width: '100%', marginBottom: '0.75rem' }}
            onClick={handleSyncClassroom}
            disabled={syncing}
          >
            Sync Classroom Now
          </button>
          <button
            className="btn-outline"
            style={{ width: '100%' }}
            onClick={isGuest ? handleLogout : fetchData}
          >
            {isGuest ? 'Exit Guest Mode' : 'Refresh Data'}
          </button>
        </div>
      </aside>

      <ConflictModal
        conflict={activeConflict}
        onResolve={handleResolveConflict}
      />
    </main>
  );
}
