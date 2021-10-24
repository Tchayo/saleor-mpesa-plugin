import base64
import datetime
import json
import requests
from requests.auth import HTTPBasicAuth

from django.core.exceptions import ImproperlyConfigured

from saleor.payment import TransactionKind
from ...interface import (
    GatewayConfig,
    PaymentData
)

from saleor.payment.interface import GatewayResponse

# set in settings file
MPESA_EXPRESS_CALLBACK_URL = "https://some-non-existent-site.co.ke/mpesa-callback"


# **config.connection_params from GatewayConfig object as params
def get_mpesa_gateway(sandbox_mode, mpesa_business_short_code, mpesa_consumer_key, mpesa_consumer_secret, mpesa_passkey):
    if not all([mpesa_business_short_code, mpesa_consumer_key, mpesa_consumer_secret, mpesa_passkey]):
        raise ImproperlyConfigured("Incorrectly configured Mpesa gateway. All setup fields required.")

    access_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    express_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"

    if not sandbox_mode:
        access_url = "https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
        express_url = "https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest"

    return {
        "access_url": access_url,
        "express_url": express_url,
        "short_code": mpesa_business_short_code,
        "key": mpesa_consumer_key,
        "secret": mpesa_consumer_secret,
        "passkey": mpesa_passkey
    }


def generate_access_token(api_url, consumer_key, consumer_secret):
    try:
        access_token = None

        req = requests.get(api_url, auth=HTTPBasicAuth(consumer_key, consumer_secret))
        data = json.loads(req.text)

        if 'access_token' in data:
            access_token = data['access_token']

        return access_token

    except requests.ConnectionError as e:
        print('{}'.format(e))
        return None


def express_request(payment_information: PaymentData, config: GatewayConfig):
    gateway_config = get_mpesa_gateway(**config.connection_params)
    try:
        if (gateway_config and payment_information.billing.phone):
            # phone formatting
            phone = format_mobile(payment_information.billing.phone)

            current_dt = datetime.datetime.now()
            timestamp = current_dt.strftime("%Y%m%d%H%M%S")

            pass_word = base64.b64encode(
                (gateway_config["short_code"] + gateway_config["passkey"] + timestamp).encode(
                    'utf-8')).decode('utf-8')

            # Mpesa Express request
            access_token = generate_access_token(gateway_config["access_url"], gateway_config["key"],
                                                 gateway_config["secret"])

            express_api_url = gateway_config["express_url"]

            if access_token is None:
                # error message if keys are not set
                message = "Express payment cannot be processed. Select a different " \
                          "payment method"
                return GatewayResponse(
                    is_success=False,
                    action_required=False,
                    kind=TransactionKind.CAPTURE,
                    amount=payment_information.amount,
                    currency=payment_information.currency,
                    transaction_id=payment_information.token,
                    error=message,
                )
            else:
                headers = {
                    "Authorization": "Bearer %s" % access_token
                }

                integer_amount = round(payment_information.amount)

                mpesa_request_body = {
                    "BusinessShortCode": gateway_config["short_code"],
                    "Password": pass_word,
                    "Timestamp": timestamp,
                    "TransactionType": "CustomerPayBillOnline",
                    "Amount": str(integer_amount),
                    "PartyA": phone,
                    "PartyB": gateway_config["short_code"],
                    "PhoneNumber": phone,
                    "CallBackURL": MPESA_EXPRESS_CALLBACK_URL,
                    "AccountReference": payment_information.payment_id,
                    "TransactionDesc": "Online Checkout",
                }

                mpesa_response = requests.post(express_api_url, json=mpesa_request_body, headers=headers)

                data = mpesa_response.json()

                if 'CustomerMessage' in data and 'CheckoutRequestID' in data:
                    data['CheckoutRequestID']
                    mpesa_success_response = data['ResponseCode']
                    return GatewayResponse(
                        is_success=True,
                        action_required=False,
                        kind=TransactionKind.AUTH,
                        amount=payment_information.amount,
                        currency=payment_information.currency,
                        transaction_id=payment_information.token,
                        error=mpesa_success_response,
                    )

                if 'errorMessage' in data:
                    error_message = data['errorMessage']

                    return GatewayResponse(
                        is_success=False,
                        action_required=False,
                        kind=TransactionKind.CAPTURE,
                        amount=payment_information.amount,
                        currency=payment_information.currency,
                        transaction_id=payment_information.token,
                        error=error_message,
                    )
        else:
            # error message if keys are not set
            message = "Express payment failed! Make sure your phone number is in your billing address"
            return GatewayResponse(
                is_success=False,
                action_required=False,
                kind=TransactionKind.CAPTURE,
                amount=payment_information.amount,
                currency=payment_information.currency,
                transaction_id=payment_information.token,
                error=message,
            )

    except requests.ConnectionError as e:
        # error message if any network issue is experienced
        print('{}'.format(e))
        message = "Express payment failed, try again later"
        return GatewayResponse(
            is_success=False,
            action_required=False,
            kind=TransactionKind.CAPTURE,
            amount=payment_information.amount,
            currency=payment_information.currency,
            transaction_id=payment_information.token,
            error=message,
        )


def format_mobile(mobile):
    formated_mobile  = mobile.replace(" ", "")
    if formated_mobile[0] == '0':
        formated_mobile = formated_mobile.replace('0', '254', 1)
    if formated_mobile[0] == '+':
        formated_mobile = formated_mobile.replace('+', '', 1)

    return formated_mobile
