'use client';
import { useState, useEffect } from 'react';
import './TaskCard.css';

export default function TaskCard({ task, index }) {
  const [isStudying, setIsStudying] = useState(false);
  const [elapsedTime, setElapsedTime] = useState(0);

  useEffect(() => {
    let interval = null;
    if (isStudying) {
      interval = setInterval(() => {
        setElapsedTime(prev => prev + 1);
      }, 1000);
    } else if (!isStudying && elapsedTime !== 0) {
      clearInterval(interval);
    }
    return () => clearInterval(interval);
  }, [isStudying, elapsedTime]);

  const formatTime = (seconds) => {
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = seconds % 60;
    if (h > 0) return `${h}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
    return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  };

  const toggleStudying = () => {
    setIsStudying(!isStudying);
  };

  // Determine priority color based on score
  let priorityClass = 'priority-low';
  if (task.priority_score > 70) priorityClass = 'priority-high';
  else if (task.priority_score > 40) priorityClass = 'priority-med';

  return (
    <div className={`glass-panel task-card animate-slide-up`} style={{ animationDelay: `${index * 0.1}s` }}>
      <div className="task-header">
        <h3>{task.title}</h3>
        <span className={`priority-badge ${priorityClass}`}>
          {task.priority_score.toFixed(1)} Pts
        </span>
      </div>
      
      <p className="task-course">{task.course}</p>
      
      <div className="task-meta">
        <div className="meta-item">
          <span className="icon">⏱️</span>
          <span>{task.effort_estimate_hrs} hrs est.</span>
        </div>
        <div className="meta-item">
          <span className="icon">📅</span>
          <span>Due: {new Date(task.due_date).toLocaleDateString()}</span>
        </div>
      </div>
      
      <div className="task-actions">
        <button 
          className={isStudying ? "btn-active" : "btn-primary"}
          onClick={toggleStudying}
        >
          {isStudying ? `Stop Studying (${formatTime(elapsedTime)})` : (elapsedTime > 0 ? `Resume (${formatTime(elapsedTime)})` : "Start Studying")}
        </button>
      </div>
    </div>
  );
}
