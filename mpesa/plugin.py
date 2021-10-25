from saleor.payment.interface import GatewayResponse, PaymentData
from saleor.plugins.base_plugin import BasePlugin, ConfigurationTypeField

from ..utils import get_supported_currencies

from . import (
    GatewayConfig,
    authorize,
    capture,
    get_client_token,
    process_payment,
    refund,
    void,
)



GATEWAY_NAME = 'Mpesa'

def require_active_plugin(fn):
    def wrapped(self, *args, **kwargs):
        previous = kwargs.get("previous_value", None)
        if not self.active:
            return previous
        return fn(self, *args, **kwargs)

    return wrapped


class MpesaGatewayPlugin(BasePlugin):
    PLUGIN_ID = "custom.payments.mpesa"
    PLUGIN_NAME = GATEWAY_NAME
    DEFAULT_ACTIVE = True
    DEFAULT_CONFIGURATION = [
        {"name": "Mpesa Business Short Code", "value": "174379"},
        {"name": "Mpesa Consumer Key", "value": None},
        {"name": "Mpesa Consumer Secret", "value": None},
        {"name": "Mpesa Passkey", "value": None},
        {"name": "Use sandbox", "value": True},
        {"name": "Store customers card", "value": False},
        {"name": "Automatic payment capture", "value": False},
        {"name": "Supported currencies", "value": "KES"},
    ]

    CONFIG_STRUCTURE = {
        "Mpesa Business Short Code": {
            "type": ConfigurationTypeField.STRING,
            "help_text": "Provide Mpesa Short Code ie. 12345",
            "label": "Mpesa Business Short Code",
        },
        "Mpesa Consumer Key": {
            "type": ConfigurationTypeField.SECRET,
            "help_text": "Provide Mpesa Consumer key.",
            "label": "Mpesa Consumer key",
        },
        "Mpesa Consumer Secret": {
            "type": ConfigurationTypeField.SECRET,
            "help_text": "Provide Mpesa Consumer Secret.",
            "label": "Mpesa Consumer Secret",
        },
        "Mpesa Passkey": {
            "type": ConfigurationTypeField.SECRET,
            "help_text": "Provide Mpesa Passkey.",
            "label": "Mpesa Passkey",
        },
        "Use sandbox": {
            "type": ConfigurationTypeField.BOOLEAN,
            "help_text": "Determines if Saleor should use Mpesa sandbox API.",
            "label": "Use sandbox",
        },
        "Store customers card": {
            "type": ConfigurationTypeField.BOOLEAN,
            "help_text": "Determines if Saleor should store cards on payments "
            "in Stripe customer.",
            "label": "Store customers card",
        },
        "Automatic payment capture": {
            "type": ConfigurationTypeField.BOOLEAN,
            "help_text": "Determines if Saleor should automaticaly capture payments.",
            "label": "Automatic payment capture",
        },
        "Supported currencies": {
            "type": ConfigurationTypeField.STRING,
            "help_text": "Determines currencies supported by gateway."
            " Please enter currency codes separated by a comma.",
            "label": "Supported currencies",
        },
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        configuration = {item["name"]: item["value"] for item in self.configuration}
        self.config = GatewayConfig(
            gateway_name=GATEWAY_NAME,
            auto_capture=configuration["Automatic payment capture"],
            supported_currencies=configuration["Supported currencies"],
            connection_params={
                "sandbox_mode": configuration["Use sandbox"],
                "mpesa_business_short_code": configuration["Mpesa Business Short Code"],
                "mpesa_consumer_key": configuration["Mpesa Consumer Key"],
                "mpesa_consumer_secret": configuration["Mpesa Consumer Secret"],
                "mpesa_passkey": configuration["Mpesa Passkey"],
            },
            store_customer=configuration["Store customers card"],
        )

    def _get_gateway_config(self):
        return self.config

    @require_active_plugin
    def authorize_payment(
        self, payment_information: "PaymentData", previous_value
    ) -> "GatewayResponse":
        return authorize(payment_information, self._get_gateway_config())

    @require_active_plugin
    def capture_payment(
        self, payment_information: "PaymentData", previous_value
    ) -> "GatewayResponse":
        return capture(payment_information, self._get_gateway_config())

    @require_active_plugin
    def refund_payment(
        self, payment_information: "PaymentData", previous_value
    ) -> "GatewayResponse":
        return refund(payment_information, self._get_gateway_config())

    @require_active_plugin
    def void_payment(
        self, payment_information: "PaymentData", previous_value
    ) -> "GatewayResponse":
        return void(payment_information, self._get_gateway_config())

    @require_active_plugin
    def process_payment(
        self, payment_information: "PaymentData", previous_value
    ) -> "GatewayResponse":
        return process_payment(payment_information, self._get_gateway_config())
    
    @require_active_plugin
    def get_client_token(self, token_config: "TokenConfig", previous_value):
        return get_client_token()

    @require_active_plugin
    def get_supported_currencies(self, previous_value):
        config = self._get_gateway_config()
        return get_supported_currencies(config, GATEWAY_NAME)

    @require_active_plugin
    def get_payment_config(self, previous_value):
        config = self._get_gateway_config()
        return [
            {"field": "store_customer_card", "value": config.store_customer},
        ]
