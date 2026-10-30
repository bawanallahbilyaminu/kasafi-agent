# WhatsApp message template for hazard alerts

The draft for submission to Meta (WhatsApp Manager → Message templates → Create template), from
`docs/hazard-and-services.md` section 9. Alerts go out **outside the 24-hour customer-service window**, so they need
an **approved template** and a payment method on the WhatsApp Business Account: each delivered alert is charged.

**Only `kasafi_hazard_alert` is sent as a template.** Sign-up and stop confirmations always answer a message the user
has just sent ("Alert me about floods in Goronyo", STOP / DAINA), so they are inside the 24-hour window and go out as
normal messages. No template is needed for them.

**Template settings:**
- **Category:** Utility. These messages follow up on something the user signed up for; they aren't marketing. Don't
  add offers, links to promotions or anything that reads as marketing, or Meta may re-categorise the template as
  Marketing.
- **Languages:** submit it twice, as **Hausa (`ha`)** and **English (`en`)**, under the same template name.
- **Message validity period: 6 hours.** An alert that can't be delivered within 6 hours is dropped, not delivered
  late.
- **Variables** are `{{1}}` to `{{4}}`. Meta asks for a sample value for each; use the ones given here.
- **Variable values are one line and never end with a full stop**: the template supplies the punctuation. The
  alerts code strips line breaks and a trailing full stop from every value before sending.
- The body must not start or end with a variable, and must have no more than two consecutive line breaks.
- **Buttons:** quick replies. Their text arrives back as an ordinary message: MORE gives details or a map, STOP /
  DAINA ends alerts.

---

## `kasafi_hazard_alert`

Sent when a trigger fires for an LGA a user signed up for: a new official advisory; heat reaching Danger (by
max(air temperature, NWS heat index)); dust at "Hazardous" on the US AQI, or high for the time of year; a river point
above its 95th percentile for the same time of year; or a new NCDC outbreak report for Sokoto. At most one per
hazard per LGA per day. Quiet hours 22:00–06:00, except official warnings.

| Variable | Meaning | Sample (en) | Sample (ha) |
|---|---|---|---|
| `{{1}}` | hazard | heat | zafin rana |
| `{{2}}` | LGA | Wamakko | Wamakko |
| `{{3}}` | what and when, with the figure (one line, no full stop) | 41 °C expected tomorrow afternoon, Danger level | 41 °C gobe da rana, matakin Haɗari |
| `{{4}}` | source and time (one line, no full stop) | Open-Meteo forecast, 30 Oct 2026 06:00 | Hasashen Open-Meteo, 30 Oct 2026 06:00 |

**English (`en`)**

- Body:
  ```
  Kasafi {{1}} alert for {{2}} LGA: {{3}}.

  Source: {{4}}.

  Reply MORE for details or a map. Reply STOP to stop these alerts.
  ```
- Footer: `Kasafi · hazard information, not emergency response`
- Buttons (quick reply): `MORE`, `STOP`

**Hausa (`ha`)**

- Body:
  ```
  Faɗakarwar Kasafi game da {{1}} a Ƙaramar Hukumar {{2}}: {{3}}.

  Majiya: {{4}}.

  Rubuta MORE don cikakken bayani ko taswira. Rubuta DAINA don daina karɓar waɗannan faɗakarwa.
  ```
- Footer: `Kasafi · bayanan haɗari, ba agajin gaggawa ba`
- Buttons (quick reply): `MORE`, `DAINA`

---

## Normal messages (no template): sign-up and stop confirmations

Sent as ordinary replies, inside the 24-hour window:

- **Sign-up (en):** "You're signed up for Kasafi alerts about floods in Goronyo LGA. You'll get at most one alert per
  hazard per day, and none at night except official warnings. Each alert names its source. Reply STOP at any time
  to stop."
- **Sign-up (ha):** "An yi maka rajistar faɗakarwar Kasafi game da ambaliya a Ƙaramar Hukumar Goronyo. Ba za ka samu
  fiye da faɗakarwa ɗaya ga kowane haɗari a rana ba, kuma babu da daddare sai sanarwar hukuma. Kowace faɗakarwa tana
  faɗin majiyarta. Rubuta DAINA a kowane lokaci don dainawa."
- **Stop (en):** "Done: you won't receive Kasafi alerts any more. You can still ask Kasafi questions at any time."
- **Stop (ha):** "An gama: ba za ka sake karɓar faɗakarwar Kasafi ba. Har yanzu kana iya tambayar Kasafi a kowane
  lokaci."

---

## Steps in WhatsApp Manager

1. **business.facebook.com** → WhatsApp Manager → **Account tools → Message templates → Create template**.
2. Category **Utility**, name `kasafi_hazard_alert`. Add language **English**.
3. Fill in the body, footer and buttons as above, and add the samples.
4. Under **Message validity period**, turn on the custom period and choose **6 hours**. Then **Submit**.
5. Open the same template → **Add language → Hausa** and fill in the Hausa version, so it's one name with two
   languages.
6. If `kasafi_alert_signup` or `kasafi_alert_stopped` were submitted earlier, delete them: they aren't used.
7. Check **Payment methods** on the WhatsApp Business Account: utility messages outside the window are charged per
   delivered message.

Once approved, the alerts code (hazard step 6) sends `kasafi_hazard_alert` with the user's language code (`ha` or
`en`) and the four values. MORE and STOP / DAINA come back as ordinary messages.
