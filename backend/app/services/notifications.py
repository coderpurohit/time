"""
Notification Service for Teacher Substitution System
Handles email/SMS notifications for substitute assignments
"""

from typing import Dict, Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class NotificationService:
    """
    Service for sending notifications to substitute teachers and students.
    Currently implements email functionality (SMS can be added later).
    """
    
    def __init__(
        self,
        smtp_host: str = "smtp.gmail.com",
        smtp_port: int = 587,
        sender_email: Optional[str] = None,
        sender_password: Optional[str] = None
    ):
        """
        Initialize notification service with email configuration.
        
        Note: For production, these should come from environment variables.
        """
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.enabled = sender_email is not None and sender_password is not None
    
    def send_substitute_assignment_email(
        self,
        recipient_email: str,
        substitute_name: str,
        absent_teacher_name: str,
        date: str,
        classes: list,
        substitution_id: int = None
    ) -> Dict:
        """
        Send email notification to substitute teacher about their assignment.
        
        Args:
            recipient_email: Substitute teacher's email
            substitute_name: Name of the substitute teacher
            absent_teacher_name: Name of the absent teacher
            date: Date of substitution
            classes: List of class details
            substitution_id: ID for confirmation link
        
        Returns:
            Dict with success status and message
        """
        if not self.enabled:
            return {
                "sent": False,
                "reason": "Email service not configured",
                "message": "To enable notifications, configure SMTP settings in environment variables"
            }
        
        subject = f"Substitute Assignment - {date}"
        
        # Build class list
        class_details = "\n".join([
            f"  • {cls.get('subject')} - {cls.get('time_slot')} - {cls.get('class_group')} ({cls.get('room')})"
            for cls in classes
        ])
        
        # Create email body
        body = f"""
Dear {substitute_name},

You have been assigned as a substitute teacher for {absent_teacher_name} on {date}.

Classes Assigned:
{class_details}

Please confirm your availability by clicking the link below:
[Confirmation link would go here - substitution ID: {substitution_id}]

Thank you for your cooperation!

Best regards,
Timetable Management System
"""
        
        try:
            return self._send_email(recipient_email, subject, body)
        except Exception as e:
            return {
                "sent": False,
                "error": str(e),
                "message": f"Failed to send email: {str(e)}"
            }
    
    def send_class_cancellation_email(
        self,
        recipient_emails: list,
        class_details: Dict,
        date: str,
        reason: str = "Teacher absence"
    ) -> Dict:
        """
        Send notification about class cancellation to students.
        
        Args:
            recipient_emails: List of student/class representative emails
            class_details: Details about the cancelled class
            date: Date of cancellation
            reason: Reason for cancellation
        
        Returns:
            Dict with success status
        """
        if not self.enabled:
            return {"sent": False, "reason": "Email service not configured"}
        
        subject = f"Class Cancelled - {date}"
        body = f"""
Dear Students,

The following class has been cancelled on {date}:

Subject: {class_details.get('subject')}
Time: {class_details.get('time_slot')}
Room: {class_details.get('room')}

Reason: {reason}

Please check for updates regarding rescheduling.

Best regards,
Timetable Management System
"""
        
        results = []
        for email in recipient_emails:
            try:
                result = self._send_email(email, subject, body)
                results.append(result)
            except Exception as e:
                results.append({"sent": False, "email": email, "error": str(e)})
        
        return {
            "sent": all(r.get("sent", False) for r in results),
            "total": len(recipient_emails),
            "details": results
        }
    
    def _send_email(self, to_email: str, subject: str, body: str) -> Dict:
        """
        Internal method to send email via SMTP.
        
        Returns:
            Dict with sent status and message
        """
        if not self.enabled:
            return {"sent": False, "reason": "Not configured"}
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = to_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))
            
            # Connect and send
            server = smtplib.SMTP(self.smtp_host, self.smtp_port)
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            server.send_message(msg)
            server.quit()
            
            return {
                "sent": True,
                "to": to_email,
                "subject": subject,
                "message": "Email sent successfully"
            }
        
        except Exception as e:
            return {
                "sent": False,
                "to": to_email,
                "error": str(e),
                "message": f"Failed to send email: {str(e)}"
            }


# Singleton instance (can be configured via environment variables)
notification_service = NotificationService(
    # These should be loaded from environment variables in production:
    # sender_email=os.getenv("SMTP_EMAIL"),
    # sender_password=os.getenv("SMTP_PASSWORD")
)


def get_notification_service() -> NotificationService:
    """Get the notification service instance"""
    return notification_service
