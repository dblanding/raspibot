import subprocess

def restart_scanner():
    try:
        # capture_output=True captures stdout and stderr. text=True decodes output to string
        result = subprocess.run(
            ["pyinfra", "../inventory.py", "deploy/restart_scanner.py", "-y"],
            capture_output=True,
            text=True,
            check=True  # check=True raises a CalledProcessError if the command fails
        )
        print("Output:", result.stdout)
    except subprocess.CalledProcessError as e:
        print("Error:", e.stderr)
    except FileNotFoundError:
        print("Error: Command not found. Check your command name and path.")

def start_odometer():
    try:
        # capture_output=True captures stdout and stderr. text=True decodes output to string
        result = subprocess.run(
            ["pyinfra", "../inventory.py", "deploy/start_odom.py", "-y"],
            capture_output=True,
            text=True,
            check=True  # check=True raises a CalledProcessError if the command fails
        )
        print("Output:", result.stdout)
    except subprocess.CalledProcessError as e:
        print("Error:", e.stderr)
    except FileNotFoundError:
        print("Error: Command not found. Check your command name and path.")

def stop_odometer():
    try:
        # capture_output=True captures stdout and stderr. text=True decodes output to string
        result = subprocess.run(
            ["pyinfra", "../inventory.py", "deploy/stop_odom.py", "-y"],
            capture_output=True,
            text=True,
            check=True  # check=True raises a CalledProcessError if the command fails
        )
        print("Output:", result.stdout)
    except subprocess.CalledProcessError as e:
        print("Error:", e.stderr)
    except FileNotFoundError:
        print("Error: Command not found. Check your command name and path.")
