# 🚀 Quick DNS Changer

A simple and fast desktop application for Windows that allows you to easily manage and switch your DNS profiles. Built with Python and the [Flet](https://flet.dev/) framework.



---

### ✨ Features

* **Graphical User Interface:** Easily manage DNS settings without complex commands.
* **Profile Management:** Add, delete, and select custom DNS profiles.
* **One-Click Apply:** Change your active DNS with a single click.
* **Automatic Reset:** Revert DNS settings back to automatic (DHCP) effortlessly.
* **Local Storage:** Your custom profiles are securely saved in your local `AppData` folder.

---

### ⚠️ Prerequisites

1.  **Operating System:** **Windows** is required due to the use of `netsh` commands.
2.  **Admin Privileges:** The application must be **run as an administrator** to modify network settings.

---

### 📥 How to Use (Users)

1.  Go to the **[Releases](https://github.com/EFFIESL/Quick-DNS-Changer/releases)** page of this repository.
2.  Download the latest version's `.zip` file (e.g., `QuickDNSChanger-windows.zip`).
3.  Extract the archive and run `main.exe` as an administrator.

---

### 🛠️ How to Run (Developers)

1.  Clone this repository:
    ```bash
    git clone [https://github.com/EFFIESL/Quick-DNS-Changer.git](https://github.com/EFFIESL/Quick-DNS-Changer.git)
    cd YOUR_REPO
    ```
2.  Create and activate a Python virtual environment:
    ```bash
    python -m venv venv
    .\venv\Scripts\activate
    ```
3.  Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```
4.  Run the application:
    ```bash
    flet run src/main.py
    ```

---

### 📄 License

This project is licensed under the MIT License.