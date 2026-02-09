from pyinfra.operations import server, files

# Define a function to update the remote uv installation itself (optional but recommended)
def update_uv_tool():
    # Use the standalone installer command to self-update uv on the remote host
    server.shell(
        name="Update uv to the latest version",
        commands=['curl -LsSf https://astral.sh/uv/install.sh | sh'],
    )

# Define a function to upgrade project packages in a virtual environment
def upgrade_project_packages(venv_path=".venv"):
    # Change into the project directory where the venv and pyproject.toml are located
    # and run uv sync --upgrade
    server.shell(
        name="Upgrade all packages in the project environment",
        commands=[f"uv lock --upgrade"],
        # Ensure the command runs in the correct environment/directory
    )
    # To upgrade a specific package to the latest compatible version:
    # server.shell(
    #     name="Upgrade a specific package (e.g., requests)",
    #     commands=[f"cd /path/to/my/project && uv sync --upgrade-package requests"],
    # )

# Run the operations within the pyinfra execution flow
# update_uv_tool() # Uncomment to run uv self-update
upgrade_project_packages()
