import sqlite3
import pytz
from datetime import datetime

def update_ticket_to_new_flight(ticket_no: str, new_flight_id: int) -> str:
    """Update the user's ticket to a new valid flight.

    Args:
        ticket_no (str): The ticket number to be updated.
        new_flight_id (int): The ID of the new flight to which the ticket should be updated.

    Returns:
        str: A message indicating whether the ticket was successfully updated or if there were errors.
    """
    config = ensure_config()
    configuration = config.get("configurable", {})
    passenger_id = configuration.get("passenger_id", None)
    if not passenger_id:
        raise ValueError("No passenger ID configured.")

    conn = sqlite3.connect(db)
    cursor = conn.cursor()

    try:
        # 获取新航班信息
        cursor.execute(
            "SELECT departure_airport, arrival_airport, scheduled_departure FROM flights WHERE flight_id = ?",
            (new_flight_id,),
        )
        new_flight = cursor.fetchone()
        if not new_flight:
            return "Invalid new flight ID provided."

        column_names = [column[0] for column in cursor.description]
        new_flight_dict = dict(zip(column_names, new_flight))
        
        # 时间校验（可选）
        timezone = pytz.timezone("Etc/GMT-3")
        current_time = datetime.now(tz=timezone)
        departure_time = datetime.strptime(
            new_flight_dict["scheduled_departure"], "%Y-%m-%d %H:%M:%S.%f%z"
        )
        time_until = (departure_time - current_time).total_seconds()
        # if time_until < (3 * 3600):
        #     return f"Not permitted to reschedule to a flight that is less than 3 hours from the current time. Selected flight is at {departure_time}."

        # 检查原航班信息
        cursor.execute(
            "SELECT flight_id FROM ticket_flights WHERE ticket_no = ?", (ticket_no,)
        )
        current_flight = cursor.fetchone()
        if not current_flight:
            return "No existing ticket found for the given ticket number."

        # 检查票是否属于当前用户
        cursor.execute(
            "SELECT * FROM tickets WHERE ticket_no = ? AND passenger_id = ?",
            (ticket_no, passenger_id),
        )
        current_ticket = cursor.fetchone()
        if not current_ticket:
            return f"Current signed-in passenger with ID {passenger_id} not the owner of ticket {ticket_no}"

        # 更新 ticket_flights 表的 flight_id
        cursor.execute(
            "UPDATE ticket_flights SET flight_id = ? WHERE ticket_no = ?",
            (new_flight_id, ticket_no),
        )

        # **同步更新 boarding_passes 表**
        cursor.execute(
            "UPDATE boarding_passes SET flight_id = ? WHERE ticket_no = ?",
            (new_flight_id, ticket_no),
        )

        # 提交事务
        conn.commit()
        return "Ticket successfully updated to new flight."

    except Exception as e:
        conn.rollback()  # 发生错误时回滚
        return f"Error updating ticket: {str(e)}"

    finally:
        cursor.close()
        conn.close()
