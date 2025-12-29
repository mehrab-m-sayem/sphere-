"""
Email Service for SPHERE
Handles sending 2FA codes and notifications
"""

import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import os


class EmailService:
    """Handles email sending for 2FA and notifications"""
    
    def __init__(self):
        # Email configuration (use environment variables in production)
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.from_email = os.getenv("FROM_EMAIL", "noreply@sphere-health.com")
        self.from_name = "SPHERE Health System"
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        body_text: str,
        body_html: Optional[str] = None
    ) -> bool:
        """
        Send email
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body_text: Plain text body
            body_html: Optional HTML body
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create message
            message = MIMEMultipart('alternative')
            message['From'] = f"{self.from_name} <{self.from_email}>"
            message['To'] = to_email
            message['Subject'] = subject
            
            # Attach text part
            message.attach(MIMEText(body_text, 'plain'))
            
            # Attach HTML part if provided
            if body_html:
                message.attach(MIMEText(body_html, 'html'))
            
            # For development: just print the code to console
            print(f"\n{'='*60}")
            print(f"EMAIL TO: {to_email}")
            print(f"SUBJECT: {subject}")
            print(f"{'='*60}")
            print(body_text)
            print(f"{'='*60}\n")
            
            return True
            
        except Exception as e:
            print(f"Error preparing email: {e}")
            return False
    
    async def send_2fa_code(self, to_email: str, code: str) -> bool:
        """
        Send 2FA code via email
        
        Args:
            to_email: Recipient email
            code: 6-digit verification code
        
        Returns:
            True if successful
        """
        subject = "SPHERE - Verification Code"
        body_text = f"Your verification code is: {code}\n\nThis code expires in 5 minutes."
        body_html = f"""
        <html>
            <body>
                <h2>SPHERE Verification Code</h2>
                <p>Your verification code is:</p>
                <h1 style="font-family: monospace; color: #667eea;">{code}</h1>
                <p>This code expires in 5 minutes.</p>
                <hr>
                <p style="color: #999; font-size: 12px;">
                    If you didn't request this code, please ignore this email.
                </p>
            </body>
        </html>
        """
        
        return await self.send_email(to_email, subject, body_text, body_html)