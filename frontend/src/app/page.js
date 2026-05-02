'use client';
import { useState, useEffect } from 'react';
import TaskCard from '../components/TaskCard';
import ConflictModal from '../components/ConflictModal';

export default function Dashboard() {
  const [tasks, setTasks] = useState([]);
  const [activeConflict, setActiveConflict] = useState(null);

  // Mock data for display purposes
  useEffect(() => {
    // Simulate fetching tasks
    setTasks([
      {
        id: 1,
        title: "Calculus III Midterm",
        course: "MATH 301",
        priority_score: 85.5,
        effort_estimate_hrs: 10,
        due_date: new Date(Date.now() + 86400000 * 2).toISOString(), // 2 days from now
      },
      {
        id: 2,
        title: "Data Structures Final Project",
        course: "CS 202",
        priority_score: 75.0,
        effort_estimate_hrs: 15,
        due_date: new Date(Date.now() + 86400000 * 5).toISOString(),
      },
      {
        id: 3,
        title: "Read Chapter 4: Thermodynamics",
        course: "PHYS 101",
        priority_score: 35.2,
        effort_estimate_hrs: 2,
        due_date: new Date(Date.now() + 86400000 * 7).toISOString(),
      }
    ]);

    // Simulate a conflict event popping up after 3 seconds
    setTimeout(() => {
      setActiveConflict({
        academic_task: "Study for Calculus III Midterm",
        calendar_event: "Coffee with Alex",
        start_time: "Tomorrow 2:00 PM",
        end_time: "Tomorrow 4:00 PM",
        priority_score: 85.5
      });
    }, 3000);
  }, []);

  const handleResolveConflict = (decision) => {
    console.log("User decision:", decision);
    setActiveConflict(null);
  };

  return (
    <main className="dashboard-container">
      <header className="header">
        <div>
          <h1>Axiom</h1>
          <p>Your prioritized study schedule, automatically generated.</p>
        </div>
        <button className="btn-outline" onClick={() => alert('Google OAuth flow initiated.')}>
          Connect Google Apps
        </button>
      </header>

      <div className="main-content">
        <h2>🔥 Up Next for You</h2>
        <div className="task-list">
          {tasks.map((task, idx) => (
            <TaskCard key={task.id} task={task} index={idx} />
          ))}
        </div>
      </div>

      <aside className="sidebar">
        <div className="glass-panel" style={{ padding: '1.5rem' }}>
          <h2>Today's Stats</h2>
          <div style={{ marginTop: '1rem' }}>
            <p style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
              <span>Tasks Completed:</span>
              <span style={{ color: 'white', fontWeight: 'bold' }}>2</span>
            </p>
            <p style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span>Hours Studied:</span>
              <span style={{ color: 'white', fontWeight: 'bold' }}>3.5 hrs</span>
            </p>
          </div>
        </div>
      </aside>

      <ConflictModal 
        conflict={activeConflict} 
        onResolve={handleResolveConflict} 
      />
    </main>
  );
}
