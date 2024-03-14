import socket
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import ssl
import smtplib
from email.mime.text import MIMEText
from email.message import EmailMessage

# Function to scan ports in parallel
def port_scanner(host, ports):
    open_ports = []
    for port in ports:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                result = sock.connect_ex((host, port))
                if result == 0:
                    open_ports.append(port)
        except Exception as e:
            print(f"Error scanning port {port}: {e}")
    return open_ports

# Function to send email alerts
def send_email(subject, message):
    sender_email = 'EMAIL'
    password = 'PASSWORD' # You should ensure `password` is correctly imported from `app`
    receiver_email = 'EMAIL'

    msg = MIMEText(message)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = receiver_email

    context = ssl.create_default_context()

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        print("Email sent successfully.")
    except smtplib.SMTPException as e:
        print(f"Error sending email: {e}")

if __name__ == "__main__":
    host = input("Enter the IP address to scan: ")
    start_port = int(input("Enter the start port: "))
    end_port = int(input("Enter the end port: "))

    try:
        while True:
            # Divide ports into chunks for parallel scanning
            port_chunks = [range(start_port + i, min(start_port + i + 100, end_port + 1)) for i in range(0, end_port - start_port + 1, 100)]

            open_ports = []
            with ThreadPoolExecutor(max_workers=os.cpu_count() or 1) as executor:
                future_to_ports = {executor.submit(port_scanner, host, port_chunk): port_chunk for port_chunk in port_chunks}
                for future in as_completed(future_to_ports):
                    open_ports.extend(future.result())

            if open_ports:
                message = f"Unauthorized port scan detected on {host} with open ports: {open_ports}"
                subject = "Port Scan Alert"
                send_email(subject, message)
            else:
                print(f"No unauthorized port scans detected on {host} within the range {start_port}-{end_port}.")

            time.sleep(60)  # Wait for 60 seconds before checking again
    except KeyboardInterrupt:
        print("Script stopped by user.")