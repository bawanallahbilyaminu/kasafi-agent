# WhatsApp message templates for hazard alerts

Drafts for submission to Meta (WhatsApp Manager → Message templates → Create template), from
`docs/hazard-and-services.md` section 9. Alerts go out **outside the 24-hour customer-service window**, so each one needs
an **approved template** and a payment method on the WhatsApp Business Account: each delivered alert is charged.
Submit these now, because approval takes time.

**For every template:**
- **Category:** Utility. These messages follow up on something the user signed up for; they aren't marketing. Don't
  add offers, links to promotions or anything that reads as marketing, or Meta may re-categorise the template as
  Marketing.
- **Languages:** submit each one twice, as **Hausa (`ha`)** and **English (`en`)**, under the same template name.
- **Variables** are `{{1}}`, `{{2}}` and so on. Meta asks for a sample value for each; use the ones given here.
- **Buttons:** quick replies. Their text arrives back as an ordinary message: MORE gives details or a map, STOP ends
  alerts.
- The body must not start or end with a variable, and must have no more than two consecutive line breaks.

---

## 1. `kasafi_hazard_alert`: the alert

Sent when a trigger fires for an LGA a user signed up for: a new official advisory, heat index reaching Danger, dust
or PM10 at "Very unhealthy", a river point above its 95th percentile, or a new NCDC outbreak report for Sokoto.
At most one per hazard per LGA per day. Quiet hours 22:00–06:00, except official warnings.

| Variable | Meaning | Sample (en) | Sample (ha) |
|---|---|---|---|
| `{{1}}` | hazard | Heat | Zafin rana |
| `{{2}}` | LGA | Wamakko | Wamakko |
| `{{3}}` | what and when (one line, with the figure) | heat index 41 °C (Danger) expected tomorrow afternoon | ma'aunin zafi 41 °C (Haɗari) gobe da rana |
| `{{4}}` | source and time | NiMet advisory, issued 30 Oct 2026, 06:00 | Sanarwar NiMet, 30 Oct 2026, 06:00 |

**English (`en`)**

- Header (text): `Kasafi hazard alert`
- Body:
  ```
  {{1}} alert for {{2}} LGA: {{3}}.

  Source: {{4}}.

  Reply MORE for details or a map. Reply STOP to stop these alerts.
  ```
- Footer: `Kasafi · hazard information, not emergency response`
- Buttons (quick reply): `MORE`, `STOP`

**Hausa (`ha`)**

- Header (text): `Faɗakarwar haɗari daga Kasafi`
- Body:
  ```
  Faɗakarwar {{1}} ga Ƙaramar Hukumar {{2}}: {{3}}.

  Majiya: {{4}}.

  Rubuta MORE don cikakken bayani ko taswira. Rubuta DAINA don daina karɓar waɗannan faɗakarwa.
  ```
- Footer: `Kasafi · bayanan haɗari, ba agajin gaggawa ba`
- Buttons (quick reply): `MORE`, `DAINA`

---

## 2. `kasafi_alert_signup`: sign-up confirmation

Sent after a user signs up ("Alert me about floods in Goronyo" / "Sanar da ni game da ambaliya a Goronyo"). It's
usually inside the 24-hour window, where a normal message would do. The template covers sign-ups confirmed later, for
example from a menu or after a delay.

| Variable | Meaning | Sample (en) | Sample (ha) |
|---|---|---|---|
| `{{1}}` | hazards | floods and heat | ambaliya da zafin rana |
| `{{2}}` | LGAs | Goronyo | Goronyo |

**English (`en`)**

- Body:
  ```
  You're signed up for Kasafi alerts about {{1}} in {{2}} LGA.

  You'll get at most one alert per hazard per day, and none at night except official warnings. Each alert names its source. Reply STOP at any time to stop.
  ```
- Buttons (quick reply): `STOP`

**Hausa (`ha`)**

- Body:
  ```
  An yi maka rajistar faɗakarwar Kasafi game da {{1}} a Ƙaramar Hukumar {{2}}.

  Ba za ka samu fiye da faɗakarwa ɗaya ga kowane haɗari a rana ba, kuma babu da daddare sai sanarwar hukuma. Kowace faɗakarwa tana faɗin majiyarta. Rubuta DAINA a kowane lokaci don dainawa.
  ```
- Buttons (quick reply): `DAINA`

---

## 3. `kasafi_alert_stopped`: stop confirmation

Sent after STOP / DAINA. Usually inside the window, where a normal message would do. The template covers a stop
confirmed later.

| Variable | Meaning | Sample (en) | Sample (ha) |
|---|---|---|---|
| `{{1}}` | what was stopped | all Kasafi alerts | dukkan faɗakarwar Kasafi |

**English (`en`)**

- Body:
  ```
  Done: you won't receive {{1}} any more.

  You can still ask Kasafi questions at any time. To sign up again, send a message such as "Alert me about heat in Wamakko".
  ```

**Hausa (`ha`)**

- Body:
  ```
  An gama: ba za ka sake karɓar {{1}} ba.

  Har yanzu kana iya tambayar Kasafi a kowane lokaci. Don sake yin rajista, aika saƙo kamar "Sanar da ni game da zafin rana a Wamakko".
  ```

---

## Steps in WhatsApp Manager

1. **business.facebook.com** → WhatsApp Manager → **Account tools → Message templates → Create template**.
2. Category **Utility**, then the template name exactly as above (lowercase with underscores). Add language **English**.
3. Fill in the header, body, footer and buttons as above, add the samples, then **Submit**.
4. Open the same template → **Add language → Hausa** and fill in the Hausa version, so it's one name with two
   languages.
5. Repeat for the other two templates.
6. Check **Payment methods** on the WhatsApp Business Account: utility messages outside the window are charged per
   delivered message.

Once approved, the alerts code (hazard step 6) sends `kasafi_hazard_alert` with the user's language code (`ha` or
`en`) and the four values. MORE and STOP / DAINA come back as ordinary messages.
