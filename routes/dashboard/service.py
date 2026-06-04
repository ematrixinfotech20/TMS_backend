from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

class DashboardService:
    @staticmethod
    def get_dashboard_data(current_user_id: int, db):
        if not current_user_id:
            raise HTTPException(status_code=401, detail="Unauthorized")
        with db.cursor() as cursor:
            # 1. Assigned tickets count
            cursor.execute("SELECT COUNT(*) as count FROM assigned_tickets WHERE assign_to = %s", (current_user_id,))
            result = cursor.fetchone()
            ticket_count = result['count'] if result else 0

            # 2. Get all assigned tickets for current user, joined with metadata
            query = """
                SELECT t.id, t.ticket_no, t.title, t.due_date, t.created_date, t.created_by,
                       p.name AS project_name, d.name AS department_name, s.name AS status_name,
                       CONCAT(u.first_name, ' ', u.last_name) AS created_by_name
                FROM assigned_tickets at
                JOIN tickets t ON at.ticket_id = t.id
                LEFT JOIN projects p ON t.project_id = p.id
                LEFT JOIN departments d ON t.department_id = d.id
                LEFT JOIN status s ON t.status_id = s.id
                LEFT JOIN users u ON t.created_by = u.id
                WHERE at.assign_to = %s
            """
            cursor.execute(query, (current_user_id,))
            assigned_tickets = cursor.fetchall()

            unanswered_tickets = []
            for ticket in assigned_tickets:
                # 3. Find the last comment for the ticket
                comment_query = """
                    SELECT created_by, created_date_time
                    FROM ticket_comments
                    WHERE ticket_id = %s
                    ORDER BY created_date_time DESC, id DESC
                    LIMIT 1
                """
                cursor.execute(comment_query, (ticket['id'],))
                last_comment = cursor.fetchone()

                # If no comments, or the last comment creator was not the current user
                if not last_comment or last_comment['created_by'] != current_user_id:
                    unanswered_tickets.append({
                        "id": ticket['id'],
                        "ticket_no": ticket['ticket_no'],
                        "project_name": ticket['project_name'] or "N/A",
                        "department_name": ticket['department_name'] or "N/A",
                        "title": ticket['title'],
                        "status_name": ticket['status_name'] or "N/A",
                        "created_by_name": ticket['created_by_name'] or "Unknown",
                        "last_post_date": last_comment['created_date_time'] if last_comment else None,
                        "due_date": ticket['due_date']
                    })

            # Sort unanswered tickets by ID desc (most recent first)
            unanswered_tickets.sort(key=lambda x: x['id'], reverse=True)

        return {
            "assigned_tickets_count": ticket_count,
            "assigned_tickets": [
                {
                    "id": ticket["id"],
                    "ticket_no": ticket["ticket_no"],
                    "title": ticket["title"]
                }
                for ticket in assigned_tickets
            ],
            "unanswered_tickets": unanswered_tickets
        }
