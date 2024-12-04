# QR-Based Access & Attendance System
## Overview
This project is a Gym/School Access and Attendance System built entirely using Python with Flask. It uses QR codes to manage user access based on payment and status, and provides user management features such as activating or deactivating users.

## User Management
- Register Users: Automatically generates a QR code for each user during registration.
- Edit Users: Update user details, such as name, phone number, and password.
- Delete Users: Remove users and their associated QR codes.
- Activate/Deactivate Users: Enable or disable user access as needed.
## Payment Management
- Automatically calculate payment status based on registration and payment dates.
- Prevent access if payments are pending.
## QR Code Management
- Generate QR codes during user registration.
- Download QR codes for offline use.
- Use QR codes to validate user access at gym or school gates.
## Attendance Tracking
- Keep track of attendance records for each user.
- Automatically mark attendance upon successful QR validation.

## How to Use
### 1. Clone the repository:
```bash
git clone https://github.com/SonuSubhadip/Qr_Attendance.git
cd Qr_Attendance
```
### 2 Requirements Python Dependencies
Install required libraries using
```bash
pip install -r library/requirements.txt
```

### 3. Run the Flask application:
```bash
python Attendence.py
```

### 4. Open the application in your browser:
```bash
http://127.0.0.1:5000/
```

### 5. Use the interface to:
- Register users
- Manage payments
- Download QR codes
- Track attendance

## Important:
Installed MICROSOFT VISUAL C++ REDISTRIBUTABLE FOR VISUAL STUDIO 2013 

## Screenshots:
![Screenshot (51)](https://github.com/user-attachments/assets/b7536da5-1861-421d-b610-fc2ec843bdf8)

## License
This project is licensed under the MIT License.

##
With this README.md, anyone visiting your GitHub project will understand what it's about and how to use it. Let me know if you need help adding anything!

