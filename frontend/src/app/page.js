'use client';
import { useState, useEffect, useCallback } from 'react';
import TaskCard from '../components/TaskCard';
import ConflictModal from '../components/ConflictModal';

const API = 'http://localhost:8000';

export default function Dashboard() {
  const [tasks, setTasks] = useState([]);
  const [courses, setCourses] = useState([]);
  const [activeConflict, setActiveConflict] = useState(null);
  const [syncing, setSyncing] = useState(false);
  const [syncMsg, setSyncMsg] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const [coursesRes, tasksRes] = await Promise.all([
        fetch(`${API}/courses`),
        fetch(`${API}/tasks`),
      ]);
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
    fetchData();
  }, [fetchData]);

  const handleSyncClassroom = async () => {
    setSyncing(true);
    setSyncMsg(null);
    try {
      const res = await fetch(`${API}/courses/sync-classroom`, { method: 'POST' });
      const data = await res.json();
      if (res.ok) {
        setSyncMsg(`✅ Synced! Added ${data.added.length} new, updated ${data.updated.length} existing course(s).`);
        await fetchData(); // Refresh course list
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

  const priorityColor = (score) => {
    if (!score) return 'var(--priority-low)';
    if (score >= 75) return 'var(--priority-high)';
    if (score >= 40) return 'var(--priority-med)';
    return 'var(--priority-low)';
  };

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
          <button className="btn-outline" onClick={() => window.open(`${API}/auth/login`, '_blank')} id="connect-google-btn">
            Connect Google
          </button>
        </div>
      </header>

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
          <h2>📊 Today's Stats</h2>
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
            onClick={fetchData}
          >
            Refresh Data
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
