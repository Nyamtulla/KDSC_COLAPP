# Email Configuration Guide

This guide explains how to configure email functionality for the password reset feature in ColApp.

## Environment Variables

Set these environment variables in your deployment environment:

### For Gmail (Recommended for testing)
```bash
EMAIL_ENABLED=true
EMAIL_SMTP_SERVER=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_USERNAME=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
EMAIL_FROM_NAME=ColApp Support
EMAIL_FROM_ADDRESS=your-email@gmail.com
```

### For Outlook/Hotmail
```bash
EMAIL_ENABLED=true
EMAIL_SMTP_SERVER=smtp-mail.outlook.com
EMAIL_SMTP_PORT=587
EMAIL_USERNAME=your-email@outlook.com
EMAIL_PASSWORD=your-password
EMAIL_FROM_NAME=ColApp Support
EMAIL_FROM_ADDRESS=your-email@outlook.com
```

### For Custom SMTP Server
```bash
EMAIL_ENABLED=true
EMAIL_SMTP_SERVER=your-smtp-server.com
EMAIL_SMTP_PORT=587
EMAIL_USERNAME=your-username
EMAIL_PASSWORD=your-password
EMAIL_FROM_NAME=ColApp Support
EMAIL_FROM_ADDRESS=your-email@yourdomain.com
```

## Gmail App Password Setup

If using Gmail, you need to create an App Password:

1. Go to your Google Account settings
2. Navigate to Security
3. Enable 2-Step Verification if not already enabled
4. Go to App passwords
5. Generate a new app password for "Mail"
6. Use this password in the `EMAIL_PASSWORD` environment variable

## Development Mode

For development/testing, you can leave `EMAIL_ENABLED=false` (default). This will print emails to the console instead of sending them.

## Testing

1. Set up the environment variables
2. Restart your Flask application
3. Try the "Forgot Password" feature
4. Check your email (or console output if `EMAIL_ENABLED=false`)

## Security Notes

- Never commit email credentials to version control
- Use environment variables for all sensitive information
- Consider using a dedicated email service for production (SendGrid, Mailgun, etc.)
- The reset tokens expire after 1 hour for security 