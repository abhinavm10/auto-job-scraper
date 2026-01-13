# 📧 Email Notifications Feature - TODO

## Overview

Add Gmail SMTP email notifications to alert when new matching jobs are found.

---

## Prerequisites

- [ ] Enable 2-Factor Authentication on your Google account
- [ ] Generate an App Password at https://myaccount.google.com/apppasswords
- [ ] Store credentials securely in `.env` file

---

## Implementation TODOs

### 1. Environment Setup

- [ ] Add email config to `.env`:
  ```
  SMTP_EMAIL=your-email@gmail.com
  SMTP_APP_PASSWORD=your-app-password
  NOTIFICATION_EMAIL=your-email@gmail.com
  ```

### 2. Create Notification Service

- [ ] Create `app/services/notification_service.py`
- [ ] Implement `EmailNotifier` class with:
  - [ ] `send_job_alert(job_title, company, link)` - Single job notification
  - [ ] `send_daily_digest(jobs_list)` - Daily summary of all matches
  - [ ] `send_application_confirmation(job_title, company)` - After auto-apply

### 3. Email Templates

- [ ] Create HTML email templates in `app/templates/emails/`
  - [ ] `job_alert.html` - Single job match
  - [ ] `daily_digest.html` - Daily summary
  - [ ] `application_sent.html` - Confirmation

### 4. Integration

- [ ] Hook notifications into job matching pipeline
- [ ] Add notification toggle in config (enable/disable)
- [ ] Add rate limiting (avoid spam)

---

## Code Reference

```python
# app/services/notification_service.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings

class EmailNotifier:
    def __init__(self):
        self.smtp_email = settings.SMTP_EMAIL
        self.smtp_password = settings.SMTP_APP_PASSWORD
        self.notification_email = settings.NOTIFICATION_EMAIL

    def send_job_alert(self, job_title: str, company: str, link: str) -> bool:
        """Send notification for a single job match."""
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = f"🚀 New Job Match: {job_title} at {company}"
            msg["From"] = self.smtp_email
            msg["To"] = self.notification_email

            # Plain text version
            text = f"""
New Job Match Found!

Position: {job_title}
Company: {company}
Apply here: {link}

---
Job Auto-Applier
            """

            # HTML version
            html = f"""
            <html>
            <body style="font-family: Arial, sans-serif; padding: 20px;">
                <h2>🎯 New Job Match Found!</h2>
                <div style="background: #f5f5f5; padding: 15px; border-radius: 8px;">
                    <p><strong>Position:</strong> {job_title}</p>
                    <p><strong>Company:</strong> {company}</p>
                    <a href="{link}" style="display: inline-block; background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                        Apply Now →
                    </a>
                </div>
                <p style="color: #888; margin-top: 20px; font-size: 12px;">
                    Sent by Job Auto-Applier
                </p>
            </body>
            </html>
            """

            msg.attach(MIMEText(text, "plain"))
            msg.attach(MIMEText(html, "html"))

            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(self.smtp_email, self.smtp_password)
                server.send_message(msg)

            return True
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False

    def send_daily_digest(self, jobs: list) -> bool:
        """Send daily summary of all matched jobs."""
        # TODO: Implement
        pass

    def send_application_confirmation(self, job_title: str, company: str) -> bool:
        """Send confirmation after successful auto-apply."""
        # TODO: Implement
        pass
```

---

## Testing

- [ ] Test with a simple script first:

  ```python
  from app.services.notification_service import EmailNotifier

  notifier = EmailNotifier()
  notifier.send_job_alert(
      job_title="Software Engineer",
      company="Google",
      link="https://careers.google.com/jobs/123"
  )
  ```

---

## Notes

- Gmail allows 500 emails/day (more than enough)
- Consider adding retry logic for failed sends
- Add logging for email send attempts
