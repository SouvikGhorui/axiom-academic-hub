import './ConflictModal.css';

export default function ConflictModal({ conflict, onResolve }) {
  if (!conflict) return null;

  return (
    <div className="modal-overlay">
      <div className="glass-panel modal-content animate-slide-up">
        <h2>⚠️ Schedule Conflict Detected</h2>
        <p>The academic hub tried to schedule a study block, but it conflicts with an existing event on your Google Calendar.</p>
        
        <div className="conflict-details">
          <div className="conflict-card academic">
            <span className="badge">Academic Task</span>
            <h4>{conflict.academic_task}</h4>
            <p>{conflict.start_time} - {conflict.end_time}</p>
            <p className="impact">Priority Score: {conflict.priority_score}</p>
          </div>
          
          <div className="vs">VS</div>
          
          <div className="conflict-card non-academic">
            <span className="badge">Calendar Event</span>
            <h4>{conflict.calendar_event}</h4>
            <p>{conflict.start_time} - {conflict.end_time}</p>
          </div>
        </div>
        
        <div className="modal-actions">
          <button className="btn-outline" onClick={() => onResolve('KEEP_CALENDAR')}>
            Keep Calendar Event
          </button>
          <button className="btn-primary" onClick={() => onResolve('OVERRIDE')}>
            Override (Study Instead)
          </button>
        </div>
      </div>
    </div>
  );
}
