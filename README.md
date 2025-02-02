
<!-- /!\ Non OCA Context : Set here the badge of your runbot / runboat instance. -->
[![Pre-commit Status](https://github.com/shopinvader/odoo-shopinvader-payment/actions/workflows/pre-commit.yml/badge.svg?branch=14.0)](https://github.com/shopinvader/odoo-shopinvader-payment/actions/workflows/pre-commit.yml?query=branch%3A14.0)
[![Build Status](https://github.com/shopinvader/odoo-shopinvader-payment/actions/workflows/test.yml/badge.svg?branch=14.0)](https://github.com/shopinvader/odoo-shopinvader-payment/actions/workflows/test.yml?query=branch%3A14.0)
[![codecov](https://codecov.io/gh/shopinvader/odoo-shopinvader-payment/branch/14.0/graph/badge.svg)](https://codecov.io/gh/shopinvader/odoo-shopinvader-payment)
<!-- /!\ Non OCA Context : Set here the badge of your translation instance. -->

<!-- /!\ do not modify above this line -->

# Shopinvader payment modules

Payment methods for Odoo Shopinvader

<!-- /!\ do not modify below this line -->

<!-- prettier-ignore-start -->

[//]: # (addons)

Available addons
----------------
addon | version | maintainers | summary
--- | --- | --- | ---
[invader_invoice_payment](invader_invoice_payment/) | 14.0.1.0.1 |  | Invader addon to make invoice payment
[invader_payment](invader_payment/) | 14.0.1.0.1 |  | Payment integration for Shopinvader
[invader_payment_manual](invader_payment_manual/) | 14.0.1.0.0 |  | REST Services for manual payment like bank transfer, check ... (base module)
[invader_payment_stripe](invader_payment_stripe/) | 14.0.1.0.1 |  | REST Services for Stripe Payments (base module)
[shopinvader_payment](shopinvader_payment/) | 14.0.1.2.1 |  | Payment integration for Shopinvader
[shopinvader_payment_condition](shopinvader_payment_condition/) | 14.0.1.0.1 | [![ivantodorovich](https://github.com/ivantodorovich.png?size=30px)](https://github.com/ivantodorovich) | Filter available payment methods based on order conditions
[shopinvader_payment_manual](shopinvader_payment_manual/) | 14.0.1.0.1 |  | REST Services for manual payment (like bank transfer, check...)
[shopinvader_payment_stripe](shopinvader_payment_stripe/) | 14.0.1.0.1 |  | Shopinvader REST Services for Stripe Payments


Unported addons
---------------
addon | version | maintainers | summary
--- | --- | --- | ---
[invader_payment_sips](invader_payment_sips/) | 13.0.1.0.0 (unported) |  | REST Services for Worldline SIPS Payments (base module)
[shopinvader_locomotive_payment_adyen](shopinvader_locomotive_payment_adyen/) | 10.0.1.0.0 (unported) |  | Shopinvader Locomotive Adyen Payment Gateway
[shopinvader_payment_adyen](shopinvader_payment_adyen/) | 10.0.1.0.0 (unported) |  | Shopinvader Adyen Payment Gateway
[shopinvader_payment_paypal](shopinvader_payment_paypal/) | 10.0.1.0.0 (unported) |  | Shopinvader Paypal Payment Gateway
[shopinvader_payment_sips](shopinvader_payment_sips/) | 13.0.1.0.0 (unported) |  | Shopinvader REST Services for Worldline SIPS Payments
[shopinvader_quotation_payment](shopinvader_quotation_payment/) | 12.0.2.0.0 (unported) |  | Shopinvader Quotation Payment
[test_invader_payment](test_invader_payment/) | 12.0.2.0.0 (unported) |  | Test Invader payment
[test_shopinvader_payment](test_shopinvader_payment/) | 12.0.2.0.0 (unported) |  | Test shopinvader payment

[//]: # (end addons)

<!-- prettier-ignore-end -->

## Licenses

This repository is licensed under [AGPL-3.0](LICENSE).

However, each module can have a totally different license, as long as they adhere to Shopinvader
policy. Consult each module's `__manifest__.py` file, which contains a `license` key
that explains its license.

----
<!-- /!\ Non OCA Context : Set here the full description of your organization. -->
