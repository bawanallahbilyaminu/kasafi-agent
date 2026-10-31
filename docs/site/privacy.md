---
title: Kasafi Privacy Policy
permalink: /privacy/
---

# Kasafi Privacy Policy

*Last updated: 30 October 2026 (location; road distances)*

Kasafi is a WhatsApp assistant run by **Halal Numeriq Limited**, Sokoto, Nigeria ("we"). We are the data controller
under the **Nigeria Data Protection Act 2023 (NDPA)**. Contact: [bilyaminu@halalnumeriq.com.ng](mailto:bilyaminu@halalnumeriq.com.ng).

## What we collect

- Your **WhatsApp phone number** (and the profile name WhatsApp sends with it)
- The **messages and voice notes** you send Kasafi, and Kasafi's replies
- Basic technical records: times, message types and errors. These don't include your message text or your full number.
- **Answer traces** (kept 30 days) and **review-queue entries** (kept 90 days): the English wording of a question,
  plus, for traces, Kasafi's reply. **No phone number or user ID is linked to them.** Before a trace is stored, phone
  numbers, email addresses and long digit strings (such as account or NIN numbers) are removed from the wording.
- A few **settings linked to a coded ID**: whether and when you agreed to the first-contact notice, your reply language
  (Hausa or English), and how many messages you sent each day (for the daily limits). The ID is made from your number
  with a secret key, so we don't store the number itself.

We don't ask for your name, ID or address. Please don't send private details about your health or anyone else's.

### Your location

Kasafi asks for a location only when a question needs a place, for example "where is the nearest health facility?"
or "will it be hot here tomorrow?". You can share it with WhatsApp's location button, type an LGA, ward or town, or
use the LGA you chose before. The first time, Kasafi says: *"Kasafi will use your location only to answer this and
won't keep it. Only your LGA is remembered for follow-ups."*

- Kasafi works out your **Local Government Area** (and ward) from the location on our own server. The exact location
  is never sent to an AI service.
- For **road distance, travel time and the route on the map** to the nearest health facilities, your location,
  **rounded to about 100 metres**, is sent to **OpenRouteService** (HeiGIT, Heidelberg) with the facilities'
  locations, and nothing else: no number, name or message. Without it, Kasafi gives straight-line distances. In an
  emergency it isn't sent at all. The map Kasafi sends you marks your location only as a circle about 1 km across.
- The **exact location** is kept only in our server's working memory for **up to 30 minutes**, for follow-up
  questions such as "the next one?", and is then forgotten. It is **never written to our database, logs or answer
  traces**. If you type coordinates into a question, they are removed before the question is logged.
- Only your **LGA** is stored with your coded ID, for **90 days**, so "here" means your LGA in later questions. Send
  GOGE BAYANAI NA or DELETE MY DATA to delete it, along with any location still in memory.
- A location outside Sokoto State isn't used: Kasafi only covers Sokoto State.

Location data is personal data under the NDPA. Kasafi uses it only for the request you made.

## Why

To **answer your questions about public documents**, such as Sokoto State budgets, plans and reports. That means turning
voice notes into text, searching the documents and replying to you. Our legal basis is your **consent**. The first time
you message Kasafi, you get a short notice, and **nothing you send goes to any AI service until you tap OK / Na yarda**.
You can withdraw your consent at any time by sending GOGE BAYANAI NA. We also review questions Kasafi could not answer, after separating
them from your phone number, to make it more accurate (**legitimate interest**).

We do not sell your data, use it for advertising, or profile your political views.

## Who processes it

- **Meta, WhatsApp Cloud API**: delivers messages between you and Kasafi.
- **Meta, Meta Model API**: AI models that transcribe voice notes and help write answers. **During the hackathon pilot,
  content sent to the Meta Model API may be used by Meta to improve its products.**
- **Baseten**: runs an open-weight Meta AI model that helps write answers.
- **Document search (Serper web search, World Bank and ReliefWeb search services)**: when Kasafi needs a public document
  it doesn't have yet, it searches for that document by its name, for example "Sokoto State Budget Implementation
  Report Q3 2025". Your question itself, your phone number and your name are never sent to them.
- **Our server (VPS) and our database (Microsoft Azure)**: host Kasafi and store conversations.

The AI services (Meta Model API and Baseten) receive your question and extracts from documents. **They never receive
your phone number or WhatsApp name.** Some of these providers process data outside Nigeria, under their own data
protection terms and the NDPA's rules on transfers.

## How long we keep it

- **Voice notes:** deleted as soon as they have been turned into text.
- **Conversations** (your messages and our replies): **90 days**, then deleted.
- **Technical logs:** 30 days. These include an **answer trace** for each question Kasafi answers: the English wording
  of the question, the steps Kasafi took (which documents and rows it read and checked) and the reply, with **no phone
  number or ID linked to you**, so our team can check that answers are accurate.
- **Daily usage counts:** 30 days. **Consent and language settings:** until you ask us to delete them.
- **Location:** the exact location for up to 30 minutes, in memory only; your LGA for 90 days.
- **Review queue:** when Kasafi can't answer a question, or can't find a document it needs, we keep the English
  wording of the question, what was missing and which trusted sites were searched for **90 days**, so our team can add
  the missing document. This record has **no phone number or ID linked to you**, so it can't be traced back to you
  (and so can't be picked out for deletion on request); it is deleted automatically after 90 days.

To keep the free pilot fair and affordable, each number has a daily limit (currently 20 voice notes and 50 questions),
and Kasafi has an overall daily limit. When a limit is reached, Kasafi tells you and starts again the next day.

## Your rights

Under the NDPA you can ask for a copy of your data, or ask us to correct it, delete it, limit how we use it, or give it
to you in a portable format. You can also object to how we use it and withdraw your consent. Email
[bilyaminu@halalnumeriq.com.ng](mailto:bilyaminu@halalnumeriq.com.ng) and we will reply within 30 days.

**To delete your data**, send **GOGE BAYANAI NA** or **DELETE MY DATA** to Kasafi on WhatsApp. See
[how to delete your data](../data-deletion/).

If you are unhappy with how we handle your data, you can complain to the **Nigeria Data Protection Commission (NDPC)**
at [ndpc.gov.ng](https://ndpc.gov.ng).

## Security

We use encrypted connections, check that incoming messages really come from WhatsApp, and limit access to authorised
staff. If a breach puts your rights at risk, we will report it to the NDPC as the NDPA requires and tell the people
affected.

## Changes

If this policy changes, we will update this page and the date at the top. Kasafi is meant for adults; anyone under 18
should use it with a parent or guardian.
