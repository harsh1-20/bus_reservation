import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime


def send_confirmation_email(user_email, booking_details):
    """
    Send booking confirmation email to user
    """
    try:
        # Email configuration (you'll need to set up your SMTP server)
        # For demo purposes, this will just return the email content

        bus_number = booking_details.get(
            'bus_number', 'BUS-' + str(hash(user_email))[-6:])
        driver_number = booking_details.get(
            'driver_number', '+91-98765-43210', 'driver_name', 'Mr.sharma')

        email_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px; }}
                .container {{ background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; text-align: center; }}
                .details {{ margin: 20px 0; padding: 15px; background-color: #f8f9fa; border-radius: 5px; }}
                .detail-row {{ margin: 10px 0; padding: 8px; border-bottom: 1px solid #dee2e6; }}
                .label {{ font-weight: bold; color: #495057; }}
                .value {{ color: #212529; }}
                .footer {{ text-align: center; margin-top: 30px; color: #6c757d; font-size: 12px; }}
                .button {{ background-color: #28a745; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎉 Booking Confirmed! 🎉</h1>
                    <p>Your journey awaits!</p>
                </div>
                
                <div class="details">
                    <h2>Booking Details</h2>
                    <div class="detail-row">
                        <span class="label">Booking ID:</span>
                        <span class="value">{booking_details.get('booking_id', 'N/A')}</span>
                    </div>
                    <div class="detail-row">
                        <span class="label">From:</span>
                        <span class="value">{booking_details.get('from_city', 'N/A')}</span>
                    </div>
                    <div class="detail-row">
                        <span class="label">To:</span>
                        <span class="value">{booking_details.get('to_city', 'N/A')}</span>
                    </div>
                    <div class="detail-row">
                        <span class="label">Date:</span>
                        <span class="value">{booking_details.get('date', 'N/A')}</span>
                    </div>
                    <div class="detail-row">
                        <span class="label">Passengers:</span>
                        <span class="value">{booking_details.get('passengers', 'N/A')}</span>
                    </div>
                    <div class="detail-row">
                        <span class="label">Seats:</span>
                        <span class="value">{', '.join(map(str, booking_details.get('seats', [])))}</span>
                    </div>
                    <div class="detail-row">
                        <span class="label">Bus Type:</span>
                        <span class="value">{booking_details.get('bus_type', 'N/A')}</span>
                    </div>
                </div>
                
                <div class="details" style="background-color: #fff3cd; border-left: 4px solid #ffc107;">
                    <h3>🚌 Travel Information</h3>
                    <div class="detail-row">
                        <span class="label">Bus Number:</span>
                        <span class="value" style="font-size: 18px; color: #d63384;">{bus_number}</span>
                    </div>
                    <div class="detail-row">
                        <span class="label">Driver Contact:</span>
                        <span class="value" style="font-size: 18px; color: #d63384;">{driver_number}</span>
                    </div>
                </div>
                
                <div class="details" style="background-color: #d1ecf1; border-left: 4px solid #0dcaf0;">
                    <h3>💰 Payment Details</h3>
                    <div class="detail-row">
                        <span class="label">Total Amount:</span>
                        <span class="value">₹{booking_details.get('total_amount', 'N/A')}</span>
                    </div>
                    <div class="detail-row">
                        <span class="label">Discount Applied:</span>
                        <span class="value">{booking_details.get('discount', '0')}%</span>
                    </div>
                    <div class="detail-row">
                        <span class="label">Payment Mode:</span>
                        <span class="value">Cash on Boarding</span>
                    </div>
                </div>
                
                <div style="text-align: center; margin-top: 30px;">
                    <p style="font-size: 18px; color: #28a745; font-weight: bold;">
                        ✅ Your booking is confirmed!
                    </p>
                    <p style="font-size: 14px; color: #6c757d;">
                        Please arrive at the boarding point 15 minutes before departure.
                    </p>
                </div>
                
                <div class="footer">
                    <p>Thank you for choosing our service!</p>
                    <p>For any queries, contact us at support@busbooking.com</p>
                    <p>&copy; 2024 Bus Booking Service. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """

        # In a real application, you would send this via SMTP
        # For now, we'll just return the content
        return {
            'success': True,
            'message': 'Email would be sent in production',
            'email_content': email_content,
            'bus_number': bus_number,
            'driver_number': driver_number
        }

    except Exception as e:
        return {
            'success': False,
            'message': f'Error: {str(e)}'
        }
