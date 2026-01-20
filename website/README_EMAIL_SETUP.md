# Email Setup for Maharaja Chef Services

This project now uses direct SMTP email sending without third-party services.

## Files Modified:
- `send_email.php` - New PHP script for sending emails
- `js/script.js` - Updated to use fetch API for AJAX form submission
- `contact-us.html` - Removed EmailJS dependency
- `book-a-chef.html` - Removed EmailJS dependency

## Setup Instructions:

### 1. Install PHPMailer
Download PHPMailer from: https://github.com/PHPMailer/PHPMailer

Extract the contents and place the `PHPMailer` folder in your project root directory.

Your directory structure should look like:
```
chef services new/
├── PHPMailer/
│   ├── src/
│   │   ├── Exception.php
│   │   ├── PHPMailer.php
│   │   └── SMTP.php
│   └── ...
├── send_email.php
└── ... (other files)
```

### 2. Server Requirements
Your web server must support PHP. The following PHP extensions are required:
- `php-mbstring`
- `php-openssl`

### 3. SMTP Configuration
The SMTP settings in `send_email.php` are already configured with your details:
- **Host**: mail.mydgv.com
- **Username**: dgv@mydgv.com
- **Password**: 0123456789
- **Port**: 587 (STARTTLS)

### 4. Testing Locally
To test locally, you need a PHP server. Options:
- Use XAMPP, WAMP, or MAMP
- Use PHP's built-in server: `php -S localhost:8000`
- Upload to a hosting provider that supports PHP

### 5. Email Flow
- Contact form sends to: contact@myDGV.com
- Booking form sends to: contact@myDGV.com
- From address: dgv@mydgv.com

## Troubleshooting:
- If emails fail, check your SMTP server settings
- Ensure PHPMailer is properly installed
- Check PHP error logs
- Verify firewall allows SMTP connections

## Security Note:
The password is stored in plain text in the PHP file. For production, consider using environment variables or a secure configuration file outside the web root.
