import sched
import time
import subprocess

# Define the interval in seconds
interval = 60  # 1 minute

def execute_script():
    # Replace 'python' with the appropriate command if needed
    subprocess.call(['python3', 'main.py'])

# Create a scheduler instance
scheduler = sched.scheduler(time.time, time.sleep)

# Define a function to repeatedly execute the script
def repeatedly_execute_script(sc):
    execute_script()  # Execute the script
    # Reschedule the function to run after the defined interval
    scheduler.enter(interval, 1, repeatedly_execute_script, (sc,))

# Schedule the first execution of the script
scheduler.enter(0, 1, repeatedly_execute_script, (scheduler,))

# Start the scheduler
scheduler.run()