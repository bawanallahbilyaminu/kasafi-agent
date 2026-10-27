# WhatsApp Cloud API setup notes

Steps and gotchas from getting the echo bot working (Oct 27, 2026). IDs and numbers live in `.env` or the Meta
dashboard, never in this repo.

## Webhook

1. Run the server and expose it over HTTPS. During development that's a Cloudflare quick tunnel:
   `cloudflared tunnel --url http://127.0.0.1:8000`. The URL changes on every restart.
2. Put `WHATSAPP_VERIFY_TOKEN` (any long random string, e.g. `openssl rand -hex 32`) and `WHATSAPP_APP_SECRET`
   (App settings → Basic → App secret) in `.env`, then restart the server. Settings are read once at startup.
   An **empty** value counts as unset, and the webhook replies 503.
3. App Dashboard → WhatsApp → Configuration → Webhook → Edit: set Callback URL `https://<host>/webhook` and the
   same verify token, then click **Verify and save**. Subscribe the **messages** field.

## Gotcha: the dashboard "Test" works, but real messages never arrive

The dashboard **Test** button and the "Check test webhooks" panel do **not** show that real messages will reach us.
Real messages are only delivered if the **WhatsApp Business Account (WABA) is subscribed to our app**. In our case
only Meta's helper app ("WA DevX Webhook Events 1P App") was subscribed.

- Find the WABA ID on WhatsApp → API Setup, or in any webhook payload as `entry[0].id`.
- Check: `GET https://graph.facebook.com/v26.0/<WABA_ID>/subscribed_apps`. Our app must be listed.
- Fix: `POST https://graph.facebook.com/v26.0/<WABA_ID>/subscribed_apps` with the WhatsApp token.
  Undo: `DELETE` on the same URL.
- **Do this again for the production number's WABA.**

## Graph error codes seen

- **131030**: the recipient isn't on the test number's allowed list (WhatsApp → API Setup → Manage phone number list).
  The dashboard's sample sender always triggers this, which is expected.

## Legal pages registered in the Meta app

Privacy `https://halalnumeriq.com.ng/kasafi/privacy`, terms `https://halalnumeriq.com.ng/kasafi/terms`, data deletion
`https://halalnumeriq.com.ng/kasafi/data-deletion`. Their text is version-controlled in `docs/site/`, and the
backend's `/privacy`, `/terms` and `/data-deletion` redirect to them.
