'use client';
import { useState } from 'react';
import './TaskCard.css';

export default function TaskCard({ task, index }) {
  const [isStudying, setIsStudying] = useState(false);

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
          onClick={() => setIsStudying(true)}
          disabled={isStudying}
        >
          {isStudying ? "In Progress..." : "Start Studying"}
        </button>
      </div>
    </div>
  );
}
