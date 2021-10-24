# Sample Mpesa plugin for Saleor

## Installation

Copy the mpesa folder to payment app folder name gateways located in the saleor directory

```sh
cp -R mpesa <YOUR_PROJECT_ROOT>/saleor/payment/gateways
```

Next step is add this plugin to your setting.py file in the saleor folder.
Locate the plugins constant and add the line below to the array

```
"saleor.payment.gateways.mpesa.plugin.MpesaGatewayPlugin",
```

From the admin dashboard plugin settings, set up your organization's BUSINESS_SHORT_CODE, CONSUMER_KEY, CONSUMER_SECRET and PASSKEY. Without these keys the plugin will not work.

Do Not forget to setup KES as your default currency.

Use the change_currency command to change defaut currency for all models to KES i.e.

```
change_currency KES
```

### NB

The plugin only implements LIPA NA M-PESA ONLINE API also know as M-PESA express (STK Push). It lacks most of Mpesa SKD functionalities, such as

- Mpesa CallBack Processing
- C2B, B2C, B2B

Hopefully you can implement the above functionalities on your own.

## License

NONE
**Free Software! Do with it as you wish. Get it, modify it, secure it and fix or improve it where necessary. I will not assume or have any liability or responsibility for failures and/or bugs**
