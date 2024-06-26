from database import connection
import datetime
import client


def get_current_week():
    cursor = connection.cursor()
    cursor.execute(f'''
                    SELECT week_number FROM Weeks ORDER BY week_number DESC LIMIT 1
                   ''')
    current_week = cursor.fetchone()
    connection.commit()
    cursor.close()

    if current_week:
        return current_week[0]
    return None

def get_current_week_start_end():
    cursor = connection.cursor()
    cursor.execute(f'''
                    SELECT start_date, end_date FROM Weeks ORDER BY week_number DESC LIMIT 1
                   ''')
    current_week = cursor.fetchone()
    connection.commit()
    cursor.close()

    if current_week:
        return current_week
    return None


def add_week():
    print("INSERTED A NEW ONE HEHE")
    cursor = connection.cursor()

    start_date = datetime.datetime.now()
    start_date = client.TIMEZONE.localize(start_date)
    
    # get the days ahead to reach the next Thursday
    days_ahead = (3 - start_date.weekday() + 7) % 7
    end_date = start_date + datetime.timedelta(days=days_ahead)
    end_date = end_date.replace(hour=23, minute=59, second=59)

    cursor.execute(f'''
                    INSERT INTO Weeks (start_date, end_date) VALUES  (?, ?)
                   ''', (start_date, end_date))

    connection.commit()
    cursor.close()