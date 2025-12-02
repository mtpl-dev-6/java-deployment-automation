Java Deployment Automation Tool 🚀

📖 About The Project

This project is a DevOps Automation Tool written in Python. It is designed to streamline the deployment of Java Web Applications on Linux servers.

Instead of manually configuring servers, compiling code, and writing service files, this tool generates Production-Ready Maven projects that are pre-configured to:

Auto-Build: Compiles Java code into executable artifacts (JAR/WAR).

Auto-Deploy: Installs applications as native Linux Systemd Services.

Auto-Heal: Automatically restarts applications if they crash or if the server reboots.

No Docker is required. This solution runs directly on the OS for maximum performance and simplicity.

🛠 Key Features

Dual Architecture: Generates both Modern (Spring Boot) and Legacy (Servlet) project structures.

Static Port Binding: * Spring Boot is locked to Port 8080.

Servlet is locked to Port 8081.

Infrastructure as Code: The entire deployment logic is contained within a single Python script.

Production Grade: Includes logic to detect old processes, kill them gracefully, and deploy the new version with zero conflict.

⚙️ Prerequisites

Before running the generator, ensure your Linux environment has the following installed:

Python 3

Java JDK 17 (or higher)

Apache Maven (mvn)

🚀 How to Use

Step 1: Generate the Infrastructure

Run the main Python automation script. This will create the project directories and all necessary control scripts.

python3 generate_final.py


Step 2: Install Spring Boot Service (Port 8080)

This will build the Spring Boot app and register it as a background service.

cd my-spring-app
chmod +x install_service.sh
sudo ./install_service.sh


Step 3: Install Servlet Service (Port 8081)

This will build the Servlet app (using Tomcat plugin) and register it as a background service.

cd ../my-servlet-app
chmod +x install_service.sh
sudo ./install_service.sh



👨‍💻 Management Commands (Cheat Sheet)

Once installed, the applications run in the background. Use these standard Linux commands to monitor them.

Check Status

Verify if the applications are running:

sudo systemctl status my-spring-app
sudo systemctl status my-servlet-app


View Real-Time Logs

If something goes wrong, check the live logs:

# For Spring Boot
sudo journalctl -u my-spring-app -f

# For Servlet
sudo journalctl -u my-servlet-app -f


Stop/Restart Services

# Restart (e.g., after an update)
sudo systemctl restart my-spring-app

# Stop completely
sudo systemctl stop my-spring-app


🏗 Architecture Overview

Generator (generate_final.py): Creates the folder structure, pom.xml, Java Source Code, and Bash control scripts.

Builder (Maven): Compiles the source code into target/ artifacts.

Service Manager (Systemd): * The install_service.sh script creates a file in /etc/systemd/system/.

It configures Restart=always policy.

It enables WantedBy=multi-user.target so the app starts when the OS boots up.
