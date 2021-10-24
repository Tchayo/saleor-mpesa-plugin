# Sample Mpesa for Saleor

## Installation

In your project directory navigate to payments app located in the saleor directory

```sh
cp -R mpesa <YOUR_PROJECT_ROOT>/saleor/payment/gateways
```

Next step is add this plugin to your setting.py file in the saleor folder.
Locate the plugins constant and add the line below to the array

```
"saleor.payment.gateways.mpesa.plugin.MpesaGatewayPlugin",
```

### NB

The plugin only implements LIPA NA M-PESA ONLINE API also know as M-PESA express (STK Push). It lacks most of Mpesa SKD functionalities, such as

- Mpesa CallBack Processing
- C2B, B2C, B2B

Hopefully you can implement the above functionalities on your own.

## License

NONE
**Free Software! Do with it as you wish. Get it, modify it, secure it and fix or improve it where necessary. I will not assume or have any liability or responsibility for failures and/or bugs**
