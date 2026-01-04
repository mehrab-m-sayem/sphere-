"""
Email Service for SPHERE
Handles sending 2FA codes and notifications via Gmail SMTP
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import os


class EmailService:
    """Handles email sending for 2FA and notifications via Gmail SMTP"""
    
    def __init__(self):
        # Email configuration from environment variables
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.from_email = os.getenv("SMTP_USER", "")  # Use SMTP_USER as from email for Gmail
        self.from_name = "SPHERE Health System"
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        body_text: str,
        body_html: Optional[str] = None
    ) -> bool:
        """
        Send email via Gmail SMTP
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body_text: Plain text body
            body_html: Optional HTML body
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if SMTP credentials are configured
            if not self.smtp_user or not self.smtp_password:
                print(f"\n{'='*60}")
                print(f"⚠️  SMTP not configured - Printing email to console")
                print(f"EMAIL TO: {to_email}")
                print(f"SUBJECT: {subject}")
                print(f"{'='*60}")
                print(body_text)
                print(f"{'='*60}\n")
                return True
            
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
            
            # Send via Gmail SMTP
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()  # Enable TLS encryption
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(message)
            
            print(f"✅ Email sent successfully to {to_email}")
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            print(f"❌ SMTP Authentication Error: {e}")
            print("   Make sure you're using a Gmail App Password, not your regular password")
            return False
        except smtplib.SMTPException as e:
            print(f"❌ SMTP Error: {e}")
            return False
        except Exception as e:
            print(f"❌ Error sending email: {e}")
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

    async def send_password_reset_code(self, to_email: str, code: str) -> bool:
        """
        Send password reset OTP code via email
        
        Args:
            to_email: Recipient email
            code: 6-digit verification code
        
        Returns:
            True if successful
        """
        subject = "SPHERE - Password Reset Code"
        body_text = f"Your password reset code is: {code}\n\nThis code expires in 5 minutes.\n\nIf you didn't request this, please ignore this email and your password will remain unchanged."
        body_html = f"""
        <html>
            <body>
                <h2>SPHERE Password Reset</h2>
                <p>You requested to reset your password. Your verification code is:</p>
                <h1 style="font-family: monospace; color: #667eea;">{code}</h1>
                <p>This code expires in 5 minutes.</p>
                <hr>
                <p style="color: #999; font-size: 12px;">
                    If you didn't request this password reset, please ignore this email and your password will remain unchanged.
                </p>
            </body>
        </html>
        """
        
        return await self.send_email(to_email, subject, body_text, body_html)