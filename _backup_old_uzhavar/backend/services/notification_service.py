from database.db import execute_db

class NotificationService:
    @staticmethod
    def notify(user_id, title, message, notif_type='system', link=None):
        """Insert in-app notification for a user."""
        try:
            return execute_db(
                """INSERT INTO notifications (user_id, title, message, type, link)
                   VALUES (?, ?, ?, ?, ?)""",
                (user_id, title, message, notif_type, link)
            )
        except Exception:
            return None

    @staticmethod
    def notify_all(title, message, notif_type='system', link=None):
        """Broadcast an alert to all active users."""
        from database.db import query_db
        users = query_db("SELECT id FROM users WHERE is_active = 1")
        for u in users:
            NotificationService.notify(u['id'], title, message, notif_type, link)
