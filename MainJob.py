import os 
import schedule
import time

def run_monitor():
    os.system('python Monitor.py')

#schedule.every().day.at("11:00").do(os.system('python Monitor.py'))    
schedule.every().day.at("10:00").do(run_monitor)    


while True:
    schedule.run_pending()
    time.sleep(1)