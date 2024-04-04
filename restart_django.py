import os
import sys
import signal
import subprocess

def restart_django():
    # Get the current process ID
    pid = os.getpid()

    # Send a SIGTERM signal to the current process
    os.kill(pid, signal.SIGTERM)

    # Restart the server by executing the runserver command again
    subprocess.Popen(
        ['python', 'manage.py', 'runserver', '127.0.0.1:8000'],
        cwd=os.path.abspath(os.path.join(os.getcwd(), os.pardir)),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

if __name__ == "__main__":
    restart_django()