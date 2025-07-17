import schedule
import time
from data.collector import populate_database

def job():
    print("Running database update...")
    populate_database()

schedule.every().day.at("02:00").do(job)

while True:
    schedule.run_pending()
    time.sleep(60)
