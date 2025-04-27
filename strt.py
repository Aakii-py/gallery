import os

# Define folders and files
folders = [
    "static",
    "templates",
    "uploads"
]

files = {
    "app.py": "# main app file\n",
    "models.py": "# database models\n",
    "config.py": "# config settings\n",
    "requirements.txt": "Flask\nFlask-SQLAlchemy\nFlask-Login\nFlask-Mail\nWerkzeug\npython-dotenv\n",
    ".env": "SECRET_KEY=your_secret_key_here\nDATABASE_URL=sqlite:///site.db\nMAIL_SERVER=smtp.gmail.com\nMAIL_PORT=587\nMAIL_USE_TLS=True\nMAIL_USERNAME=your_email@gmail.com\nMAIL_PASSWORD=your_email_app_password\n",
    "static/darkmode.js": "// Dark mode toggle\n",
    "static/custom.css": "/* Custom styles */\n",
    "templates/base.html": "<!-- Base HTML template -->\n",
    "templates/login.html": "<!-- Login page -->\n",
    "templates/register.html": "<!-- Register page -->\n",
    "templates/gallery.html": "<!-- Gallery page -->\n",
    "templates/upload.html": "<!-- Upload page -->\n",
    "templates/admin_dashboard.html": "<!-- Admin Dashboard -->\n",
    "templates/change_password.html": "<!-- Change Password page -->\n"
}

# Create folders
for folder in folders:
    os.makedirs(folder, exist_ok=True)

# Create files
for path, content in files.items():
    # If inside a folder, make sure folder exists
    folder_path = os.path.dirname(path)
    if folder_path and not os.path.exists(folder_path):
        os.makedirs(folder_path)
    # Write content
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

print("Project structure created successfully!")
