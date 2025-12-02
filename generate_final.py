import os
import shutil
import textwrap
import sys

# --- UTILS ---
def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content.strip())
    print(f"✅ Generated: {path}")

def clean_directory(path):
    """Safely removes a directory, handling permission errors from previous sudo runs."""
    if os.path.exists(path):
        try:
            shutil.rmtree(path)
        except PermissionError:
            print(f"\n❌ ERROR: Permission denied while removing '{path}'.")
            print("   REASON: The previous build was run with 'sudo', so the files are owned by Root.")
            print(f"   FIX: Please run this command to clean up, then try again:")
            print(f"        sudo rm -rf {path}\n")
            sys.exit(1)

def setup_spring_project():
    base = "my-spring-app"
    clean_directory(base)
    print(f"\n🚀 Creating STATIC Spring Boot Project: {base}...")

    # 1. POM.XML
    pom = """
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
  <modelVersion>4.0.0</modelVersion>
  <groupId>com.company</groupId>
  <artifactId>my-spring-app</artifactId>
  <version>1.0</version>
  <parent>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-parent</artifactId>
    <version>2.7.0</version>
  </parent>
  <properties><java.version>17</java.version></properties>
  <dependencies>
    <dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-web</artifactId></dependency>
  </dependencies>
  <build><plugins><plugin><groupId>org.springframework.boot</groupId><artifactId>spring-boot-maven-plugin</artifactId></plugin></plugins></build>
</project>
"""
    create_file(f"{base}/pom.xml", pom)

    # 2. APPLICATION PROPERTIES (HARDCODED PORT 8080)
    # This embeds the port into the JAR file. It cannot be changed easily after build.
    props = "server.port=8080"
    create_file(f"{base}/src/main/resources/application.properties", props)

    # 3. Java Code
    java = """
package com.company;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@SpringBootApplication
@RestController
public class Application {
    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }
    @GetMapping("/")
    public String home() {
        return "<h1>Spring Boot is Live!</h1><p>Running on STATIC Port 8080</p>";
    }
}
"""
    create_file(f"{base}/src/main/java/com/company/Application.java", java)

    # 4. CONTROL SCRIPT
    bash = textwrap.dedent("""
        #!/bin/bash
        # Port is NO LONGER a variable here. It is read from the JAR file.
        LOG_FILE="server.log"

        if ! command -v mvn &> /dev/null; then echo "Maven missing"; exit 1; fi

        # Kill any process on 8080
        PID=$(lsof -t -i:8080)
        if [ -n "$PID" ]; then kill -9 $PID; sleep 2; fi

        echo "Building Project..."
        mvn clean package -DskipTests
        if [ $? -ne 0 ]; then echo "Build Failed"; exit 1; fi

        JAR_FILE=$(find target -name "*.jar" -not -name "*.original" | head -n 1)
        
        echo "Starting Server (Port defined in application.properties)..."
        # Notice: We removed the --server.port argument. 
        # It is now locked inside the JAR.
        nohup java -jar "$JAR_FILE" > $LOG_FILE 2>&1 &

        echo "Waiting for start..."
        sleep 5
        if lsof -t -i:8080 > /dev/null; then
            echo "SUCCESS! Online at http://localhost:8080"
        else
            echo "FAILED. Check logs."
        fi
    """)
    create_file(f"{base}/control.sh", bash)

    # 5. SERVICE INSTALLER (UPDATED WITH AUTO-BUILD)
    service = textwrap.dedent("""
        #!/bin/bash
        SERVICE_NAME="my-spring-app"
        WORK_DIR=$(pwd)
        
        # --- AUTO-BUILD LOGIC ---
        # If target folder is missing OR jar is missing, build it.
        if [ ! -d "target" ] || [ -z "$(find target -name "*.jar" -not -name "*.original" 2>/dev/null)" ]; then
            echo "⚠️  Artifact not found. Building Project first..."
            
            if ! command -v mvn &> /dev/null; then
                echo "❌ Maven not found. Install Maven first."
                exit 1
            fi

            mvn clean package -DskipTests
            
            if [ $? -ne 0 ]; then
                echo "❌ Build Failed."
                exit 1
            fi
        fi
        
        JAR_FILE=$(find "$WORK_DIR/target" -name "*.jar" -not -name "*.original" | head -n 1)
        
        if [ -z "$JAR_FILE" ]; then echo "❌ Critical Error: JAR file still not found after build."; exit 1; fi

        echo "Creating Service for $SERVICE_NAME..."

        # We do NOT pass the port here. It relies on the internal JAR config.
        sudo tee /etc/systemd/system/$SERVICE_NAME.service > /dev/null <<EOF
[Unit]
Description=Spring Boot Static Port
After=network.target

[Service]
User=$USER
WorkingDirectory=$WORK_DIR
ExecStart=/usr/bin/java -jar $JAR_FILE
SuccessExitStatus=143
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

        sudo systemctl daemon-reload
        sudo systemctl enable $SERVICE_NAME
        sudo systemctl start $SERVICE_NAME
        echo "✅ Service Installed. Port 8080 is locked."
    """)
    create_file(f"{base}/install_service.sh", service)

def setup_servlet_project():
    base = "my-servlet-app"
    clean_directory(base)
    print(f"\n🚀 Creating STATIC Servlet Project: {base}...")

    # 1. POM.XML (HARDCODED PORT 8081)
    pom = """
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/maven-v4_0_0.xsd">
  <modelVersion>4.0.0</modelVersion>
  <groupId>com.company</groupId>
  <artifactId>my-servlet-app</artifactId>
  <packaging>war</packaging>
  <version>1.0</version>
  <dependencies>
    <dependency><groupId>javax.servlet</groupId><artifactId>javax.servlet-api</artifactId><version>3.1.0</version><scope>provided</scope></dependency>
  </dependencies>
  <build><plugins><plugin>
    <groupId>org.apache.tomcat.maven</groupId><artifactId>tomcat7-maven-plugin</artifactId><version>2.2</version>
    <!-- PORT IS HARDCODED HERE. Changing script variable won't help. -->
    <configuration><port>8081</port><path>/</path></configuration>
  </plugin></plugins></build>
</project>
"""
    create_file(f"{base}/pom.xml", pom)

    # 2. Servlet Code
    java = """
package com.company;
import javax.servlet.*;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.*;
import java.io.IOException;
@WebServlet("/hello")
public class HelloServlet extends HttpServlet {
    protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws IOException {
        resp.getWriter().println("<h1>Servlet is Live!</h1><p>Port is fixed to 8081</p>");
    }
}
"""
    create_file(f"{base}/src/main/java/com/company/HelloServlet.java", java)

    # 3. CONTROL SCRIPT
    bash = textwrap.dedent("""
        #!/bin/bash
        LOG_FILE="servlet.log"
        
        # Kill 8081 if running
        PID=$(lsof -t -i:8081)
        if [ -n "$PID" ]; then kill -9 $PID; sleep 2; fi

        echo "Starting Tomcat..."
        # Notice: No -Dmaven.tomcat.port variable. It uses pom.xml setting.
        nohup mvn tomcat7:run > $LOG_FILE 2>&1 &

        echo "Waiting for Tomcat..."
        sleep 5
        if lsof -t -i:8081 > /dev/null; then
            echo "SUCCESS! http://localhost:8081/hello"
        else
            echo "FAILED. Check logs."
        fi
    """)
    create_file(f"{base}/control.sh", bash)
    create_file(f"{base}/src/main/webapp/WEB-INF/web.xml", '<web-app version="3.0" xmlns="http://java.sun.com/xml/ns/javaee"></web-app>')

    # 4. SERVICE INSTALLER
    service = textwrap.dedent("""
        #!/bin/bash
        SERVICE_NAME="my-servlet-app"
        WORK_DIR=$(pwd)
        MVN_PATH=$(command -v mvn)

        echo "Creating Service for $SERVICE_NAME..."
        
        sudo tee /etc/systemd/system/$SERVICE_NAME.service > /dev/null <<EOF
[Unit]
Description=Servlet Static Port
After=network.target

[Service]
User=$USER
WorkingDirectory=$WORK_DIR
# NO PORT ARGUMENT HERE. It is locked in pom.xml
ExecStart=$MVN_PATH tomcat7:run
SuccessExitStatus=143
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

        sudo systemctl daemon-reload
        sudo systemctl enable $SERVICE_NAME
        sudo systemctl start $SERVICE_NAME
        echo "✅ Service Installed. Port 8081 is locked."
    """)
    create_file(f"{base}/install_service.sh", service)

def main():
    setup_spring_project()
    setup_servlet_project()
    print("\n✅ STATIC PORT PROJECTS GENERATED.")
    print("Go into folders and run: sudo ./install_service.sh")

if __name__ == "__main__":
    main()
