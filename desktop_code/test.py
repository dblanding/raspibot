import subprocess

try:
    # capture_output=True captures stdout and stderr. text=True decodes output to string
    result = subprocess.run(
        ["python3", "restart_scanner.py"],
        capture_output=True,
        text=True,
        check=True  # check=True raises a CalledProcessError if the command fails
    )
    print("Output:", result.stdout)
except subprocess.CalledProcessError as e:
    print("Error:", e.stderr)
except FileNotFoundError:
    print("Error: Command not found. Check your command name and path.")
