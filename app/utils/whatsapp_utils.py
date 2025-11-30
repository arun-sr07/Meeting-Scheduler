import logging
from flask import current_app, jsonify
import json
import requests
import asyncio
import re

# Import MCP client service
from app.services.mcp_client_service import process_message_with_mcp, get_help_message, is_help_command, is_status_command


def log_http_response(response):
    logging.info(f"Status: {response.status_code}")
    logging.info(f"Content-type: {response.headers.get('content-type')}")
    logging.info(f"Body: {response.text}")


def get_text_message_input(recipient, text):
    return json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": recipient,
            "type": "text",
            "text": {"preview_url": False, "body": text},
        }
    )


async def generate_response_async(message_text):
    """Generate response using MCP client"""
    try:
        # Check for special commands
        if is_help_command(message_text):
            return get_help_message()
        
        if is_status_command(message_text):
            return "✅ Meeting Scheduler Bot is online and ready to help!"
        
        # Process message with MCP client
        response = await process_message_with_mcp(message_text)
        return response
        
    except Exception as e:
        logging.error(f"Error generating response: {e}")
        return f"❌ Sorry, I encountered an error: {str(e)}"

def generate_response(message_text):
    """Synchronous wrapper for async MCP client"""
    try:
        # Use nest_asyncio to allow nested event loops
        import nest_asyncio
        nest_asyncio.apply()
        
        # Run the async function in a new event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            response = loop.run_until_complete(generate_response_async(message_text))
        finally:
            loop.close()
        
        return response
    except Exception as e:
        logging.error(f"Error in generate_response: {e}")
        return f"❌ Sorry, I encountered an error: {str(e)}"


def send_message(data):
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {current_app.config['ACCESS_TOKEN']}",
    }

    url = f"https://graph.facebook.com/{current_app.config['VERSION']}/{current_app.config['PHONE_NUMBER_ID']}/messages"

    try:
        response = requests.post(
            url, data=data, headers=headers, timeout=10
        )  # 10 seconds timeout as an example
        response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code
    except requests.Timeout:
        logging.error("Timeout occurred while sending message")
        return jsonify({"status": "error", "message": "Request timed out"}), 408
    except (
        requests.RequestException
    ) as e:  # This will catch any general request exception
        logging.error(f"Request failed due to: {e}")
        return jsonify({"status": "error", "message": "Failed to send message"}), 500
    else:
        # Process the response as normal
        log_http_response(response)
        return response


def process_text_for_whatsapp(text):
    # Remove brackets
    pattern = r"\【.*?\】"
    # Substitute the pattern with an empty string
    text = re.sub(pattern, "", text).strip()

    # Pattern to find double asterisks including the word(s) in between
    pattern = r"\*\*(.*?)\*\*"

    # Replacement pattern with single asterisks
    replacement = r"*\1*"

    # Substitute occurrences of the pattern with the replacement
    whatsapp_style_text = re.sub(pattern, replacement, text)

    return whatsapp_style_text


def process_whatsapp_message(body):
    """Process incoming WhatsApp message with MCP client integration"""
    wa_id = None
    try:
        # Extract contact information
        contacts = body["entry"][0]["changes"][0]["value"].get("contacts", [])
        if not contacts:
            logging.error("No contacts found in message")
            return
        
        wa_id = contacts[0]["wa_id"]
        name = contacts[0].get("profile", {}).get("name", "Unknown")

        # Extract message
        messages = body["entry"][0]["changes"][0]["value"].get("messages", [])
        if not messages:
            logging.error("No messages found in webhook body")
            return
        
        message = messages[0]
        message_type = message.get("type")
        
        # Only process text messages for now
        if message_type != "text":
            logging.info(f"Received non-text message type: {message_type}. Only text messages are supported.")
            error_message = f"❌ I can only process text messages. You sent a {message_type} message."
            data = get_text_message_input(wa_id, error_message)
            send_message(data)
            return
        
        if "text" not in message or "body" not in message["text"]:
            logging.error(f"Message does not contain text body: {message}")
            return
        
        message_body = message["text"]["body"]
        logging.info(f"Processing WhatsApp message from {name} ({wa_id}): {message_body}")

        # Generate response using MCP client
        response = generate_response(message_body)
        
        # Process text for WhatsApp formatting
        formatted_response = process_text_for_whatsapp(response)
        
        logging.info(f"Sending response to {name}: {formatted_response}")

        # Send response back to the user
        data = get_text_message_input(wa_id, formatted_response)
        send_message(data)
        
    except KeyError as e:
        logging.error(f"Missing key in message structure: {e}. Full body: {json.dumps(body, indent=2)}")
        if wa_id:
            error_message = "❌ Sorry, I encountered an error processing your message. Please try again."
            data = get_text_message_input(wa_id, error_message)
            send_message(data)
    except Exception as e:
        logging.error(f"Error processing WhatsApp message: {e}", exc_info=True)
        if wa_id:
            # Send error message to user
            error_message = "❌ Sorry, I encountered an error processing your message. Please try again."
            data = get_text_message_input(wa_id, error_message)
            send_message(data)


def is_valid_whatsapp_message(body):
    """
    Check if the incoming webhook event has a valid WhatsApp message structure.
    """
    return (
        body.get("object")
        and body.get("entry")
        and body["entry"][0].get("changes")
        and body["entry"][0]["changes"][0].get("value")
        and body["entry"][0]["changes"][0]["value"].get("messages")
        and body["entry"][0]["changes"][0]["value"]["messages"][0]
    )
