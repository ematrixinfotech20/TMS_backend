from fastapi import HTTPException
from database import get_db_connection

class ReportsService:
    @staticmethod
    def get_daily_report(date: str):
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                # Query daily tickets worked on by developers for the given date
                sql = """
                    SELECT 
                        tw.user_id as developer_id,
                        CONCAT(u.first_name, ' ', u.last_name) as developer_name,
                        u.work_hours as total_working_hours,
                        tw.ticket_id,
                        t.ticket_no,
                        p.name as project_name,
                        t.title as ticket_title,
                        tw.hours,
                        tw.minutes
                    FROM today_ticket_work tw
                    JOIN users u ON tw.user_id = u.id
                    JOIN tickets t ON tw.ticket_id = t.id
                    LEFT JOIN projects p ON t.project_id = p.id
                    WHERE tw.date = %s
                    ORDER BY u.id ASC, t.ticket_no ASC
                """
                cursor.execute(sql, (date,))
                results = cursor.fetchall()
                
                developers = {}
                for row in results:
                    dev_id = row['developer_id']
                    if dev_id not in developers:
                        developers[dev_id] = {
                            "developer_id": str(dev_id),
                            "developer_name": row['developer_name'],
                            "total_working_hours": str(row['total_working_hours']) if row['total_working_hours'] is not None else "0.0",
                            "tickets": []
                        }
                    
                    # Formatting hours and minutes to something like 1.20 for 1 hour 20 minutes
                    hours_val = int(row['hours'] or 0)
                    minutes_val = int(row['minutes'] or 0)
                    today_working_hours = f"{hours_val}.{minutes_val:02d}"
                    
                    developers[dev_id]["tickets"].append({
                        "ticket_id": str(row['ticket_id']),
                        "ticket_no": row['ticket_no'],
                        "project_name": row['project_name'],
                        "title": row['ticket_title'],
                        "today_working_hours": today_working_hours
                    })
                
                return list(developers.values())
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            conn.close()

    @staticmethod
    def get_monthly_report(start_date: str, end_date: str):
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                # Query daily tickets worked on by developers between start_date and end_date
                sql = """
                    SELECT 
                        tw.ticket_id,
                        t.ticket_no,
                        p.name as project_name,
                        t.title as ticket_title,
                        tw.user_id as developer_id,
                        CONCAT(u.first_name, ' ', u.last_name) as developer_name,
                        tw.hours,
                        tw.minutes
                    FROM today_ticket_work tw
                    JOIN users u ON tw.user_id = u.id
                    JOIN tickets t ON tw.ticket_id = t.id
                    LEFT JOIN projects p ON t.project_id = p.id
                    WHERE tw.date BETWEEN %s AND %s
                    ORDER BY t.ticket_no ASC, u.id ASC
                """
                cursor.execute(sql, (start_date, end_date))
                results = cursor.fetchall()
                
                # Group by ticket, and sum hours for each ticket and each user on that ticket
                tickets = {}
                for row in results:
                    t_id = row['ticket_id']
                    if t_id not in tickets:
                        tickets[t_id] = {
                            "ticket_id": str(t_id),
                            "ticket_no": row['ticket_no'],
                            "project_name": row['project_name'],
                            "title": row['ticket_title'],
                            "total_minutes": 0,
                            "users_map": {}
                        }
                    
                    # Convert to minutes for precise summation
                    hours_val = int(row['hours'] or 0)
                    minutes_val = int(row['minutes'] or 0)
                    row_mins = hours_val * 60 + minutes_val
                    
                    tickets[t_id]["total_minutes"] += row_mins
                    
                    dev_id = row['developer_id']
                    if dev_id not in tickets[t_id]["users_map"]:
                        tickets[t_id]["users_map"][dev_id] = {
                            "developer_id": str(dev_id),
                            "developer_name": row['developer_name'],
                            "minutes": 0
                        }
                    tickets[t_id]["users_map"][dev_id]["minutes"] += row_mins
                
                # Build the response list
                report = []
                for t_id, t_data in tickets.items():
                    # Format total working hours
                    total_h = t_data["total_minutes"] // 60
                    total_m = t_data["total_minutes"] % 60
                    total_working_hours = f"{total_h}.{total_m:02d}"
                    
                    # Build users list
                    users_list = []
                    for dev_id, u_data in t_data["users_map"].items():
                        uh = u_data["minutes"] // 60
                        um = u_data["minutes"] % 60
                        working_hours = f"{uh}.{um:02d}"
                        users_list.append({
                            "developer_id": u_data["developer_id"],
                            "developer_name": u_data["developer_name"],
                            "working_hours": working_hours
                        })
                    
                    report.append({
                        "ticket_id": t_data["ticket_id"],
                        "ticket_no": t_data["ticket_no"],
                        "project_name": t_data["project_name"],
                        "title": t_data["title"],
                        "total_working_hours": total_working_hours,
                        "users": users_list
                    })
                
                return report
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            conn.close()
