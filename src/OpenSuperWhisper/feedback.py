"""
User feedback and analytics system for OpenSuperWhisper
"""

import json
import sqlite3
from datetime import datetime
from typing import Optional, Dict, Any, List
from pathlib import Path
import hashlib
import platform
from dataclasses import dataclass, asdict
from enum import Enum


class FeedbackType(Enum):
    """Types of user feedback"""
    BUG_REPORT = "bug_report"
    FEATURE_REQUEST = "feature_request"
    GENERAL_FEEDBACK = "general_feedback"
    RATING = "rating"
    TRANSCRIPTION_QUALITY = "transcription_quality"
    FORMATTING_QUALITY = "formatting_quality"


class EventType(Enum):
    """Analytics event types"""
    APP_START = "app_start"
    APP_CLOSE = "app_close"
    RECORDING_START = "recording_start"
    RECORDING_STOP = "recording_stop"
    TRANSCRIPTION_SUCCESS = "transcription_success"
    TRANSCRIPTION_FAILURE = "transcription_failure"
    FORMATTING_SUCCESS = "formatting_success"
    FORMATTING_FAILURE = "formatting_failure"
    SETTINGS_CHANGED = "settings_changed"
    PRESET_USED = "preset_used"
    ERROR_OCCURRED = "error_occurred"


@dataclass
class UserFeedback:
    """User feedback data structure"""
    feedback_type: FeedbackType
    content: str
    rating: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None
    timestamp: datetime = None
    user_id: Optional[str] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class AnalyticsEvent:
    """Analytics event data structure"""
    event_type: EventType
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime = None
    session_id: Optional[str] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class FeedbackManager:
    """Manages user feedback and analytics"""
    
    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize feedback manager
        
        Args:
            db_path: Path to SQLite database (creates in app data if None)
        """
        if db_path is None:
            db_path = self._get_default_db_path()
            
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self._init_database()
        self.session_id = self._generate_session_id()
        self.anonymous_user_id = self._get_anonymous_user_id()
        
    def _get_default_db_path(self) -> Path:
        """Get default database path based on OS"""
        system = platform.system()
        
        if system == "Windows":
            base = Path.home() / "AppData" / "Local"
        elif system == "Darwin":  # macOS
            base = Path.home() / "Library" / "Application Support"
        else:  # Linux
            base = Path.home() / ".local" / "share"
            
        return base / "OpenSuperWhisper" / "feedback.db"
        
    def _init_database(self):
        """Initialize SQLite database tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Feedback table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    feedback_type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    rating INTEGER,
                    metadata TEXT,
                    timestamp TEXT NOT NULL,
                    user_id TEXT,
                    synced BOOLEAN DEFAULT FALSE
                )
            """)
            
            # Analytics events table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL,
                    data TEXT,
                    timestamp TEXT NOT NULL,
                    session_id TEXT,
                    synced BOOLEAN DEFAULT FALSE
                )
            """)
            
            # User preferences table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS preferences (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            
            conn.commit()
            
    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        timestamp = datetime.now().isoformat()
        machine_id = platform.node()
        session_str = f"{timestamp}_{machine_id}"
        # Use SHA256 instead of MD5 for better security
        return hashlib.sha256(session_str.encode()).hexdigest()[:16]
        
    def _get_anonymous_user_id(self) -> str:
        """Get or create anonymous user ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Check if user ID exists
            cursor.execute(
                "SELECT value FROM preferences WHERE key = 'anonymous_user_id'"
            )
            result = cursor.fetchone()
            
            if result:
                return result[0]
            else:
                # Generate new user ID
                machine_info = f"{platform.node()}_{platform.system()}_{platform.machine()}"
                user_id = hashlib.sha256(machine_info.encode()).hexdigest()[:32]
                
                # Store user ID
                cursor.execute(
                    "INSERT INTO preferences (key, value, updated_at) VALUES (?, ?, ?)",
                    ('anonymous_user_id', user_id, datetime.now().isoformat())
                )
                conn.commit()
                
                return user_id
                
    def submit_feedback(
        self,
        feedback_type: FeedbackType,
        content: str,
        rating: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Submit user feedback
        
        Args:
            feedback_type: Type of feedback
            content: Feedback content
            rating: Optional rating (1-5)
            metadata: Additional metadata
            
        Returns:
            Success status
        """
        feedback = UserFeedback(
            feedback_type=feedback_type,
            content=content,
            rating=rating,
            metadata=metadata,
            user_id=self.anonymous_user_id
        )
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO feedback 
                    (feedback_type, content, rating, metadata, timestamp, user_id)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        feedback.feedback_type.value,
                        feedback.content,
                        feedback.rating,
                        json.dumps(feedback.metadata) if feedback.metadata else None,
                        feedback.timestamp.isoformat(),
                        feedback.user_id
                    )
                )
                conn.commit()
                return True
        except Exception as e:
            print(f"Error submitting feedback: {e}")
            return False
            
    def track_event(
        self,
        event_type: EventType,
        data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Track analytics event
        
        Args:
            event_type: Type of event
            data: Event data
            
        Returns:
            Success status
        """
        event = AnalyticsEvent(
            event_type=event_type,
            data=data,
            session_id=self.session_id
        )
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO events (event_type, data, timestamp, session_id)
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        event.event_type.value,
                        json.dumps(event.data) if event.data else None,
                        event.timestamp.isoformat(),
                        event.session_id
                    )
                )
                conn.commit()
                return True
        except Exception as e:
            print(f"Error tracking event: {e}")
            return False
            
    def get_feedback_summary(self) -> Dict[str, Any]:
        """Get summary of collected feedback"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Total feedback count
            cursor.execute("SELECT COUNT(*) FROM feedback")
            total_feedback = cursor.fetchone()[0]
            
            # Feedback by type
            cursor.execute("""
                SELECT feedback_type, COUNT(*) 
                FROM feedback 
                GROUP BY feedback_type
            """)
            feedback_by_type = dict(cursor.fetchall())
            
            # Average rating
            cursor.execute("SELECT AVG(rating) FROM feedback WHERE rating IS NOT NULL")
            avg_rating = cursor.fetchone()[0]
            
            # Recent feedback
            cursor.execute("""
                SELECT feedback_type, content, rating, timestamp
                FROM feedback
                ORDER BY timestamp DESC
                LIMIT 5
            """)
            recent_feedback = [
                {
                    'type': row[0],
                    'content': row[1],
                    'rating': row[2],
                    'timestamp': row[3]
                }
                for row in cursor.fetchall()
            ]
            
            return {
                'total_feedback': total_feedback,
                'by_type': feedback_by_type,
                'average_rating': avg_rating,
                'recent': recent_feedback
            }
            
    def get_analytics_summary(self) -> Dict[str, Any]:
        """Get analytics summary"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Total events
            cursor.execute("SELECT COUNT(*) FROM events")
            total_events = cursor.fetchone()[0]
            
            # Events by type
            cursor.execute("""
                SELECT event_type, COUNT(*) 
                FROM events 
                GROUP BY event_type
            """)
            events_by_type = dict(cursor.fetchall())
            
            # Sessions count
            cursor.execute("SELECT COUNT(DISTINCT session_id) FROM events")
            total_sessions = cursor.fetchone()[0]
            
            # Success rates
            cursor.execute("""
                SELECT 
                    SUM(CASE WHEN event_type = 'transcription_success' THEN 1 ELSE 0 END),
                    SUM(CASE WHEN event_type = 'transcription_failure' THEN 1 ELSE 0 END),
                    SUM(CASE WHEN event_type = 'formatting_success' THEN 1 ELSE 0 END),
                    SUM(CASE WHEN event_type = 'formatting_failure' THEN 1 ELSE 0 END)
                FROM events
            """)
            success_counts = cursor.fetchone()
            
            transcription_success_rate = 0
            if success_counts[0] or success_counts[1]:
                total_transcriptions = (success_counts[0] or 0) + (success_counts[1] or 0)
                transcription_success_rate = (success_counts[0] or 0) / total_transcriptions * 100
                
            formatting_success_rate = 0
            if success_counts[2] or success_counts[3]:
                total_formatting = (success_counts[2] or 0) + (success_counts[3] or 0)
                formatting_success_rate = (success_counts[2] or 0) / total_formatting * 100
                
            return {
                'total_events': total_events,
                'by_type': events_by_type,
                'total_sessions': total_sessions,
                'transcription_success_rate': transcription_success_rate,
                'formatting_success_rate': formatting_success_rate
            }
            
    def export_feedback(self, output_path: Path) -> bool:
        """
        Export feedback to JSON file
        
        Args:
            output_path: Path for output file
            
        Returns:
            Success status
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM feedback
                    ORDER BY timestamp DESC
                """)
                
                feedback_list = []
                for row in cursor.fetchall():
                    feedback_list.append({
                        'id': row[0],
                        'type': row[1],
                        'content': row[2],
                        'rating': row[3],
                        'metadata': json.loads(row[4]) if row[4] else None,
                        'timestamp': row[5],
                        'user_id': row[6],
                        'synced': row[7]
                    })
                    
            with open(output_path, 'w') as f:
                json.dump(feedback_list, f, indent=2, default=str)
                
            return True
        except Exception as e:
            print(f"Error exporting feedback: {e}")
            return False
            
    def clear_old_data(self, days: int = 90) -> bool:
        """
        Clear data older than specified days
        
        Args:
            days: Number of days to keep
            
        Returns:
            Success status
        """
        try:
            cutoff_date = datetime.now().timestamp() - (days * 24 * 60 * 60)
            cutoff_date_str = datetime.fromtimestamp(cutoff_date).isoformat()
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Clear old feedback
                cursor.execute(
                    "DELETE FROM feedback WHERE timestamp < ?",
                    (cutoff_date_str,)
                )
                
                # Clear old events
                cursor.execute(
                    "DELETE FROM events WHERE timestamp < ?",
                    (cutoff_date_str,)
                )
                
                conn.commit()
                
            return True
        except Exception as e:
            print(f"Error clearing old data: {e}")
            return False


# Singleton instance
_feedback_manager = None


def get_feedback_manager() -> FeedbackManager:
    """Get or create feedback manager instance"""
    global _feedback_manager
    if _feedback_manager is None:
        _feedback_manager = FeedbackManager()
    return _feedback_manager