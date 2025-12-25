# Database Access Guide (The "Easy" Way)

This guide shows you how to see your data (users, scores, etc.) using visual tools instead of code.

## Option 1: The Local Database (On your PC)
This is the file named `db.sqlite3` in your project folder. This is what you use when running `python manage.py runserver`.

### Steps:
1.  **Download this tool**: [DB Browser for SQLite](https://sqlitebrowser.org/dl/).
    *   *It's free and safe. Pick the "Standard Installer" for Windows.*
2.  **Install and Open it**.
3.  **Open your Database**:
    *   Click **"Open Database"** at the top.
    *   Navigate to your project folder: `Documents\trae_projects\ai_shooter`.
    *   Select the file named `db.sqlite3`.
4.  **See the Data**:
    *   Click the **"Browse Data"** tab (second tab at the top).
    *   Use the **"Table"** dropdown to switch between tables (e.g., `auth_user` for your users, `account_emailaddress` for emails).

---

## Option 2: The Production Database (On Coolify/Contabo)
This is the "Real" database that your live website uses. It is PostgreSQL, not SQLite, so we need a different tool.

### Steps:
1.  **Download this tool**: [TablePlus](https://tableplus.com/windows).
    *   *There is a free version that works perfectly.*
2.  **Get your Login Info**:
    *   Go to your **Coolify Dashboard**.
    *   Click on your Project -> Click on the **Database** resource (PostgreSQL).
    *   Look for the **"Connection Details"** or **"Public Connection"** section.
    *   *Note: You might need to turn on "Public Access" or "Expose Port" in Coolify settings first to connect from your home computer.*
3.  **Connect**:
    *   Open **TablePlus**.
    *   Click **"Create a new connection"**.
    *   Select **PostgreSQL**.
    *   Fill in the boxes with the info from Coolify:
        *   **Host**: (Usually an IP address like `144.x.x.x`)
        *   **Port**: `5432` (or whatever Coolify says)
        *   **User**: `ai_user` (or what is in your setting)
        *   **Password**: (The long chaotic password from Coolify)
        *   **Database**: `ai_shooter`
    *   Click **"Test"** (it should turn green), then **"Connect"**.
4.  **Browse**:
    *   Click on the table icons on the left to see your data.

---

## Which one should I use?
*   **Developing code?** -> Use **Option 1** (Local).
*   **Checking live users?** -> Use **Option 2** (Production).
