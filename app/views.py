import logging
import json

from flask import Blueprint, request, jsonify, current_app

from .decorators.security import signature_required
from .utils.whatsapp_utils import (
    process_whatsapp_message,
    is_valid_whatsapp_message,
)

webhook_blueprint = Blueprint("webhook", __name__)


def handle_message():
    """
    Handle incoming webhook events from the WhatsApp API.

    This function processes incoming WhatsApp messages and other events,
    such as delivery statuses. If the event is a valid message, it gets
    processed. If the incoming payload is not a recognized WhatsApp event,
    an error is returned.

    Every message send will trigger 4 HTTP requests to your webhook: message, sent, delivered, read.

    Returns:
        response: A tuple containing a JSON response and an HTTP status code.
    """
    body = request.get_json()
    logging.info(f"request body: {json.dumps(body, indent=2)}")

    if not body:
        logging.error("Empty request body received")
        return jsonify({"status": "error", "message": "Empty body"}), 400

    # Check if it's a WhatsApp status update
    try:
        has_statuses = (
            body.get("entry", [{}])[0]
            .get("changes", [{}])[0]
            .get("value", {})
            .get("statuses")
        )
        if has_statuses:
            logging.info("Received a WhatsApp status update.")
            return jsonify({"status": "ok"}), 200
    except (KeyError, IndexError, AttributeError) as e:
        logging.warning(f"Error checking for statuses: {e}")

    # Check for messages
    try:
        if is_valid_whatsapp_message(body):
            logging.info("Valid WhatsApp message detected, processing...")
            process_whatsapp_message(body)
            return jsonify({"status": "ok"}), 200
        else:
            # Log what we received for debugging
            logging.warning(f"Invalid WhatsApp message structure. Body keys: {body.keys() if body else 'None'}")
            if body.get("entry"):
                try:
                    value = body["entry"][0]["changes"][0]["value"]
                    logging.warning(f"Value keys: {value.keys() if isinstance(value, dict) else 'Not a dict'}")
                except (KeyError, IndexError):
                    pass
            # if the request is not a WhatsApp API event, return an error
            return (
                jsonify({"status": "error", "message": "Not a WhatsApp API event"}),
                404,
            )
    except Exception as e:
        logging.error(f"Error processing webhook: {e}", exc_info=True)
        return jsonify({"status": "error", "message": f"Processing error: {str(e)}"}), 500


# Required webhook verifictaion for WhatsApp
def verify():
    # Parse params from the webhook verification request
    logging.info(f"request args: {request.args}")
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    # Check if a token and mode were sent
    if mode and token:
        # Check the mode and token sent are correct
        if mode == "subscribe" and token == current_app.config["VERIFY_TOKEN"]:
            # Respond with 200 OK and challenge token from the request
            logging.info("WEBHOOK_VERIFIED")
            return challenge, 200
        else:
            # Responds with '403 Forbidden' if verify tokens do not match
            logging.info("VERIFICATION_FAILED")
            return jsonify({"status": "error", "message": "Verification failed"}), 403
    else:
        # Responds with '400 Bad Request' if verify tokens do not match
        logging.info("MISSING_PARAMETER")
        return jsonify({"status": "error", "message": "Missing parameters"}), 400


@webhook_blueprint.route("/webhook", methods=["GET"])
def webhook_get():
    return verify()

@webhook_blueprint.route("/webhook", methods=["POST"])
@signature_required
def webhook_post():
    return handle_message()


