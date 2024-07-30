# import pywhatkit as kit



# # Phone number (with country code) and message
# phone_number = "+91 9923643968"  # Replace with the recipient's phone number
# message = "Customer Name: John Doe Thank you for shopping with us!,Total Cost: $9.50"

# # Send the message
# kit.sendwhatmsg(phone_number, message, 0, 0)  # Sending immediately
import pywhatkit as kit
import time

# Parameters: phone number (with country code) and message
phone_number = "+91 9923643968"  # Replace with the recipient's phone number
message = "Hello, this is a test message!"

try:
    # This will send the message instantly
    kit.sendwhatmsg_instantly(phone_number, message)
    print("Message sent successfully!")
except Exception as e:
    print(f"An error occurred: {e}")
