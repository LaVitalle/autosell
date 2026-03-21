# Evolution API v2 - Comprehensive Technical Reference

> Generated from official documentation (doc.evolution-api.com/v2) and source code analysis (EvolutionAPI/evolution-api on GitHub).
> API Version: 2.1.1

---

## Table of Contents

1. [Authentication](#authentication)
2. [Send Text](#1-send-text)
3. [Send Media](#2-send-media)
4. [Find Contacts](#3-find-contacts)
5. [Find Messages](#4-find-messages)
6. [Find Chats](#5-find-chats)
7. [Mark Message As Read](#6-mark-message-as-read)
8. [Check Is WhatsApp](#7-check-is-whatsapp-whatsappnumbers)
9. [Send Presence](#8-send-presence)
10. [Fetch Profile Picture URL](#9-fetch-profile-picture-url)
11. [Update Message](#10-update-message)
12. [Set Webhook](#11-set-webhook)
13. [Find Webhook](#12-find-webhook)
14. [Webhook Events Reference](#13-webhook-events-reference)
15. [Webhook Payload Structure](#14-webhook-payload-structure)
16. [LID vs JID Handling](#15-lid-vs-jid-handling)
17. [Number Parameter Behavior](#16-number-parameter-behavior)
18. [DTOs / Data Types Reference](#17-dtos--data-types-reference)
19. [Internal Architecture Notes](#18-internal-architecture-notes)

---

## Authentication

All endpoints require an API key passed as a header:

```
apikey: YOUR_API_KEY
```

- **Type**: apiKey
- **Location**: header
- **Header name**: `apikey`

---

## 1. Send Text

### Endpoint
```
POST /message/sendText/{instance}
```

### Headers
| Header | Required | Description |
|--------|----------|-------------|
| `apikey` | Yes | Authorization key |
| `Content-Type` | Yes | `application/json` |

### Path Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `instance` | string | Yes | Name of the instance |

### Request Body
```json
{
  "number": "5531999999999",
  "text": "Hello world",
  "delay": 1200,
  "linkPreview": true,
  "mentionsEveryOne": false,
  "mentioned": ["5531988888888@s.whatsapp.net"],
  "quoted": {
    "key": {
      "id": "BAE594145F4C59B4"
    },
    "message": {
      "conversation": "Original message text"
    }
  }
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `number` | string | **Yes** | Recipient number with country code (e.g. `"5531999999999"`). Also accepts JID format (`"5531999999999@s.whatsapp.net"`) or group JID (`"123456789-987654321@g.us"`). |
| `text` | string | **Yes** | Text message content. Must be non-empty (trimmed). |
| `delay` | integer | No | Presence time in milliseconds before sending message. If >20000ms, chunked into 20s intervals. |
| `linkPreview` | boolean | No | Shows URL preview if message contains a link. |
| `mentionsEveryOne` | boolean | No | Mentions all group participants. |
| `mentioned` | string[] | No | Array of JIDs to mention (format: `remoteJID`). |
| `quoted` | object | No | Quote/reply to a message. Contains `key.id` (message ID) and `message.conversation` (original text). |

### Response (201 Created)
```json
{
  "key": {
    "remoteJid": "553198296801@s.whatsapp.net",
    "fromMe": true,
    "id": "BAE594145F4C59B4"
  },
  "message": {
    "extendedTextMessage": {
      "text": "Hello world"
    }
  },
  "messageTimestamp": "1717689097",
  "status": "PENDING"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `key.remoteJid` | string | Recipient JID |
| `key.fromMe` | boolean | Always `true` for sent messages |
| `key.id` | string | Unique message ID |
| `message.extendedTextMessage.text` | string | The sent text |
| `messageTimestamp` | string | Unix timestamp as string |
| `status` | string | Message status: `PENDING`, `SERVER_ACK`, `DELIVERY_ACK`, `READ`, `PLAYED`, `DELETED`, `ERROR` |

### Internal Behavior (from source)
```typescript
// The text method validates then delegates:
public async textMessage(data: SendTextDto, isIntegration = false) {
  const text = data.text;
  if (!text || text.trim().length === 0) {
    throw new BadRequestException('Text is required');
  }
  return await this.sendMessageWithTyping(
    data.number,
    { conversation: data.text },
    { delay: data?.delay, presence: 'composing', quoted: data?.quoted,
      linkPreview: data?.linkPreview, mentionsEveryOne: data?.mentionsEveryOne,
      mentioned: data?.mentioned },
    isIntegration,
  );
}
```

---

## 2. Send Media

### Endpoint
```
POST /message/sendMedia/{instance}
```

### Headers
| Header | Required | Description |
|--------|----------|-------------|
| `apikey` | Yes | Authorization key |
| `Content-Type` | Yes | `application/json` |

### Request Body
```json
{
  "number": "5531999999999",
  "mediatype": "image",
  "mimetype": "image/png",
  "caption": "Check this out",
  "media": "https://example.com/image.png",
  "fileName": "image.png",
  "delay": 1200,
  "mentionsEveryOne": false,
  "mentioned": [],
  "quoted": null
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `number` | string | **Yes** | Recipient number with country code. Accepts same formats as sendText. |
| `mediatype` | string | **Yes** | Media type: `"image"`, `"video"`, or `"document"` |
| `mimetype` | string | **Yes** | MIME type string (e.g. `"image/png"`, `"video/mp4"`, `"application/pdf"`) |
| `caption` | string | **Yes** | Caption text for the media |
| `media` | string | **Yes** | URL or base64-encoded media content |
| `fileName` | string | **Yes** | File name with extension (e.g. `"Image.png"`) |
| `delay` | integer | No | Presence time in milliseconds before sending |
| `linkPreview` | boolean | No | Shows URL preview if caption contains link |
| `mentionsEveryOne` | boolean | No | Mention all group participants |
| `mentioned` | string[] | No | Array of JIDs to mention |
| `quoted` | object | No | Quote/reply context (same structure as sendText) |

### Response (201 Created)
```json
{
  "key": {
    "remoteJid": "553198296801@s.whatsapp.net",
    "fromMe": true,
    "id": "BAE594145F4C59B4"
  },
  "message": {
    "imageMessage": {
      "url": "https://mmg.whatsapp.net/...",
      "mimetype": "image/png",
      "caption": "Check this out",
      "fileSha256": "base64hash==",
      "fileLength": "123456",
      "height": 600,
      "width": 800,
      "mediaKey": "base64key==",
      "fileEncSha256": "base64hash==",
      "directPath": "/v/t62...",
      "mediaKeyTimestamp": "1717689097",
      "jpegThumbnail": "base64thumbnail==",
      "contextInfo": {}
    }
  },
  "messageTimestamp": "1717689097",
  "status": "PENDING"
}
```

### Notes
- For `mediatype: "image"`, images are converted to JPEG via the `sharp` library before upload.
- Media is uploaded to WhatsApp servers via Baileys' `prepareWAMessageMedia` + `waUploadToServer`.
- The `media` field accepts either a full URL or a base64-encoded string.
- Response `message` object key varies by type: `imageMessage`, `videoMessage`, `documentMessage`, `audioMessage`.

---

## 3. Find Contacts

### Endpoint
```
POST /chat/findContacts/{instance}
```

### Request Body
```json
{
  "where": {
    "id": "553198296801@s.whatsapp.net"
  }
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `where` | object | Yes | Filter criteria |
| `where.id` | string | No | Contact JID to filter by. Omit to list all contacts. |

### Response (200 OK)
Returns an array of contact objects. Schema not formally documented, but from source code each contact contains:

| Field | Type | Description |
|-------|------|-------------|
| `remoteJid` | string | Contact JID |
| `pushName` | string | Contact display name (from WhatsApp push name, verified name, or number) |
| `profilePicUrl` | string/null | Profile picture URL |
| `instanceId` | string | Instance identifier |

---

## 4. Find Messages

### Endpoint
```
POST /chat/findMessages/{instance}
```

### Request Body
```json
{
  "where": {
    "key": {
      "remoteJid": "553198296801@s.whatsapp.net"
    }
  }
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `where` | object | No | Filter criteria |
| `where.key` | object | No | Key-based filter |
| `where.key.remoteJid` | string | No | Contact or group remote JID |

### Response (200 OK)
Returns a paginated object (from source code analysis):

```json
{
  "total": 150,
  "pages": 3,
  "currentPage": 1,
  "records": [
    {
      "id": "...",
      "key": { "id": "...", "remoteJid": "...", "fromMe": true },
      "pushName": "John",
      "messageType": "conversation",
      "message": { "conversation": "Hello" },
      "contextInfo": {},
      "status": "READ",
      "messageTimestamp": 1717689097
    }
  ]
}
```

### Internal Behavior (from source)
- Filters by `instanceId`, `source`, `messageType`
- Supports timestamp range filters (converts milliseconds to seconds)
- Default pagination: offset 50, page 1
- Ordered descending by `messageTimestamp`
- Selected fields: `id`, `key`, `pushName`, `messageType`, `message`, `contextInfo`, `MessageUpdate.status`

---

## 5. Find Chats

### Endpoint
```
POST /chat/findChats/{instance}
```

### Response (200 OK)
Returns chat list. From source code analysis, each chat contains:

| Field | Type | Description |
|-------|------|-------------|
| `remoteJid` | string | Chat JID |
| `lastMessage` | object | Last message in chat (cleaned of binary data) |
| `unreadMessages` | number | Count of unread messages |
| `24hExpiration` | boolean | Whether within 24-hour messaging window |
| `contact` | object | Contact metadata (from LEFT JOIN) |
| `chat` | object | Chat metadata (from LEFT JOIN) |

### Internal Behavior
- Uses raw SQL WITH clause for ranked distinct messages per remoteJid
- LEFT JOINs Contact and Chat tables
- Calculates unreadMessages and 24-hour window expiration

---

## 6. Mark Message As Read

### Endpoint
```
POST /chat/markMessageAsRead/{instance}
```

### Request Body
```json
{
  "readMessages": [
    {
      "remoteJid": "553198296801@s.whatsapp.net",
      "fromMe": false,
      "id": "BAE594145F4C59B4"
    }
  ]
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `readMessages` | array | **Yes** | Array of message keys to mark as read |
| `readMessages[].remoteJid` | string | No | Chat contact or group remote JID |
| `readMessages[].fromMe` | boolean | No | Whether message was sent by instance owner |
| `readMessages[].id` | string | No | Message ID |

### Response (201 Created)
```json
{
  "message": "Read messages",
  "read": "success"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `message` | string | Action description |
| `read` | string | Status of the read action |

### Internal Behavior
- Calls Baileys' `this.client.readMessages([received.key])` with the message key array
- Auto-read can be configured via instance settings:
  - `readMessages` setting: auto-reads incoming messages (excludes status@broadcast)
  - `readStatus` setting: auto-reads status broadcasts

---

## 7. Check Is WhatsApp (whatsappNumbers)

### Endpoint
```
POST /chat/whatsappNumbers/{instance}
```

### Request Body
```json
{
  "numbers": ["553198296801", "5511999998888"]
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `numbers` | string[] | **Yes** | Phone numbers with country code to check |

### Response (200 OK)
```json
[
  {
    "exists": true,
    "jid": "553198296801@s.whatsapp.net",
    "number": "553198296801"
  },
  {
    "exists": false,
    "jid": "5511999998888@s.whatsapp.net",
    "number": "5511999998888"
  }
]
```

| Field | Type | Description |
|-------|------|-------------|
| `exists` | boolean | Whether the number has an active WhatsApp account |
| `jid` | string | The WhatsApp JID for the number |
| `number` | string | The phone number checked |

### Notes
- This is the primary endpoint for validating numbers before sending messages.
- Returns both `jid` and `number` fields.
- From source: `OnWhatsAppDto` also has `name` and `lid` fields (not always populated).
- Internally used by `sendMessageWithTyping` to resolve number -> JID before every send.

---

## 8. Send Presence

### Endpoint
```
POST /chat/sendPresence/{instance}
```

### Request Body
```json
{
  "number": "553198296801",
  "options": {
    "delay": 3000,
    "presence": "composing",
    "number": "553198296801"
  }
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `number` | string | **Yes** | Receiver phone number with country code |
| `options` | object | **Yes** | Presence configuration |
| `options.delay` | integer | **Yes** | Presence display time in milliseconds |
| `options.presence` | string | **Yes** | Presence type. Enum: `"composing"`, `"recording"` |
| `options.number` | string | **Yes** | Contact number |

### Response (201 Created)
Empty response body.

### Notes
- `"composing"` = typing indicator
- `"recording"` = recording audio indicator
- From DTO source: `SendPresenceDto` extends `Metadata` with `presence` and `delay` fields

---

## 9. Fetch Profile Picture URL

### Endpoint
```
POST /chat/fetchProfilePictureUrl/{instance}
```

### Request Body
```json
{
  "number": "553198296801@s.whatsapp.net"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `number` | string | **Yes** | Number or JID to fetch profile picture for (format: `{{remoteJid}}`) |

### Response (200 OK)
```json
{
  "wuid": "553198296801@s.whatsapp.net",
  "profilePictureUrl": "https://pps.whatsapp.net/v/t61.2..."
}
```

| Field | Type | Description |
|-------|------|-------------|
| `wuid` | string | WhatsApp User ID (JID) |
| `profilePictureUrl` | string/null | URL of profile picture, or `null` if unavailable |

### Internal Implementation
```typescript
public async profilePicture(number: string) {
  const jid = createJid(number);
  try {
    const profilePictureUrl = await this.client.profilePictureUrl(jid, 'image');
    return { wuid: jid, profilePictureUrl };
  } catch {
    return { wuid: jid, profilePictureUrl: null };
  }
}
```

---

## 10. Update Message

### Endpoint
```
POST /chat/updateMessage/{instance}
```

### Request Body
```json
{
  "number": 553198296801,
  "text": "Updated message content",
  "key": {
    "remoteJid": "553198296801@s.whatsapp.net",
    "fromMe": true,
    "id": "BAE594145F4C59B4"
  }
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `number` | integer | **Yes** | Receiver phone number with country code |
| `text` | string | **Yes** | New message content |
| `key` | object | **Yes** | Message key to update |
| `key.remoteJid` | string | Yes | Chat contact or group remote JID |
| `key.fromMe` | boolean | Yes | If the message was sent by the instance owner |
| `key.id` | string | Yes | Message ID |

### Response (200 OK)
Empty response body.

### Notes
- This updates message **content**, not message read status. Use markMessageAsRead for read receipts.

---

## 11. Set Webhook

### Endpoint
```
POST /webhook/set/{instance}
```

### Request Body
```json
{
  "enabled": true,
  "url": "https://your-server.com/webhook",
  "webhookByEvents": true,
  "webhookBase64": false,
  "events": [
    "MESSAGES_UPSERT",
    "MESSAGES_UPDATE",
    "SEND_MESSAGE",
    "CONNECTION_UPDATE"
  ]
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `enabled` | boolean | **Yes** | Enable/disable webhook for the instance |
| `url` | string | **Yes** | Webhook destination URL |
| `webhookByEvents` | boolean | **Yes** | When `true`, appends event name to URL (e.g. `/messages-upsert`) |
| `webhookBase64` | boolean | **Yes** | When `true`, sends media files as base64 in webhook payloads |
| `events` | string[] | **Yes** | Event types to subscribe to (minimum 1 item) |

### Available Events (enum values)
```
APPLICATION_STARTUP
QRCODE_UPDATED
MESSAGES_SET
MESSAGES_UPSERT
MESSAGES_UPDATE
MESSAGES_DELETE
SEND_MESSAGE
CONTACTS_SET
CONTACTS_UPSERT
CONTACTS_UPDATE
PRESENCE_UPDATE
CHATS_SET
CHATS_UPSERT
CHATS_UPDATE
CHATS_DELETE
GROUPS_UPSERT
GROUP_UPDATE
GROUP_PARTICIPANTS_UPDATE
CONNECTION_UPDATE
CALL
NEW_JWT_TOKEN
TYPEBOT_START
TYPEBOT_CHANGE_STATUS
```

### Response (201 Created)
```json
{
  "webhook": {
    "instanceName": "my-instance",
    "webhook": {
      "url": "https://your-server.com/webhook",
      "events": ["MESSAGES_UPSERT"],
      "enabled": true
    }
  }
}
```

### Webhook Headers / JWT Authentication
The webhook controller supports custom headers and JWT authentication:
```typescript
// If headers include jwt_key, a JWT token is generated:
if ('jwt_key' in webhookHeaders) {
  const jwtToken = this.generateJwtToken(jwtKey);
  webhookHeaders['Authorization'] = `Bearer ${jwtToken}`;
}
// JWT payload: { iat, exp (10min), app: "evolution", action: "webhook" }
```

---

## 12. Find Webhook

### Endpoint
```
GET /webhook/find/{instance}
```

### Request
No body required. Only the `apikey` header and `instance` path parameter.

### Response (200 OK)
```json
{
  "enabled": true,
  "url": "https://example.com",
  "events": ["APPLICATION_STARTUP", "MESSAGES_UPSERT"]
}
```

| Field | Type | Description |
|-------|------|-------------|
| `enabled` | boolean | Whether the webhook is enabled |
| `url` | string | Webhook URL |
| `events` | string[] | List of subscribed events |

### cURL Example
```bash
curl -X GET "https://your-server.com/webhook/find/your-instance" \
  -H "apikey: your-api-key"
```

---

## 13. Webhook Events Reference

### Complete Events List (from source code `Events` enum)

| Event Constant | Event String | Webhook URL Suffix | Description |
|---------------|-------------|-------------------|-------------|
| `APPLICATION_STARTUP` | `application.startup` | `/application-startup` | App initialization notification |
| `INSTANCE_CREATE` | `instance.create` | `/instance-create` | New instance created |
| `INSTANCE_DELETE` | `instance.delete` | `/instance-delete` | Instance deleted |
| `QRCODE_UPDATED` | `qrcode.updated` | `/qrcode-updated` | QR code generated (base64) for scanning |
| `CONNECTION_UPDATE` | `connection.update` | `/connection-update` | WhatsApp connection status change |
| `STATUS_INSTANCE` | `status.instance` | `/status-instance` | Instance status change |
| `MESSAGES_SET` | `messages.set` | `/messages-set` | One-time bulk message load on connection |
| `MESSAGES_UPSERT` | `messages.upsert` | `/messages-upsert` | **New message received or sent** |
| `MESSAGES_EDITED` | `messages.edited` | `/messages-edited` | Message was edited |
| `MESSAGES_UPDATE` | `messages.update` | `/messages-update` | Message status update (delivery, read receipt) |
| `MESSAGES_DELETE` | `messages.delete` | `/messages-delete` | Message deleted |
| `SEND_MESSAGE` | `send.message` | `/send-message` | Outbound message sent via API |
| `SEND_MESSAGE_UPDATE` | `send.message.update` | `/send-message-update` | Sent message status update |
| `CONTACTS_SET` | `contacts.set` | `/contacts-set` | One-time initial contact roster load |
| `CONTACTS_UPSERT` | `contacts.upsert` | `/contacts-upsert` | Contact added/reloaded with metadata |
| `CONTACTS_UPDATE` | `contacts.update` | `/contacts-update` | Contact information changed |
| `PRESENCE_UPDATE` | `presence.update` | `/presence-update` | User status: online, typing, recording, paused, last seen |
| `CHATS_SET` | `chats.set` | `/chats-set` | Complete chat list delivery |
| `CHATS_UPDATE` | `chats.update` | `/chats-update` | Chat modification |
| `CHATS_UPSERT` | `chats.upsert` | `/chats-upsert` | New chat information |
| `CHATS_DELETE` | `chats.delete` | `/chats-delete` | Chat deleted |
| `GROUPS_UPSERT` | `groups.upsert` | `/groups-upsert` | Group created |
| `GROUPS_UPDATE` | `groups.update` | `/groups-update` | Group metadata changed |
| `GROUP_PARTICIPANTS_UPDATE` | `group-participants.update` | `/group-participants-update` | Member add/remove/promote/demote |
| `CALL` | `call` | `/call` | Incoming call event |
| `TYPEBOT_START` | `typebot.start` | `/typebot-start` | Typebot integration started |
| `TYPEBOT_CHANGE_STATUS` | `typebot.change-status` | `/typebot-change-status` | Typebot status change |
| `LABELS_EDIT` | `labels.edit` | `/labels-edit` | Label edited |
| `LABELS_ASSOCIATION` | `labels.association` | `/labels-association` | Label associated to chat |
| `CREDS_UPDATE` | `creds.update` | `/creds-update` | Credentials updated |
| `MESSAGING_HISTORY_SET` | `messaging-history.set` | `/messaging-history-set` | Messaging history loaded |
| `REMOVE_INSTANCE` | `remove.instance` | `/remove-instance` | Instance removed |
| `LOGOUT_INSTANCE` | `logout.instance` | `/logout-instance` | Instance logged out |

### URL Construction with `webhookByEvents`
When enabled, event names are transformed for URL:
- Dots/hyphens replaced with underscores, then uppercased for matching
- URL suffix: underscores replaced with hyphens, lowercased
- Example: `MESSAGES_UPSERT` -> URL becomes `https://your-server.com/webhook/messages-upsert`

---

## 14. Webhook Payload Structure

### Generic Webhook Payload Envelope

Every webhook event is wrapped in this structure:

```json
{
  "event": "messages.upsert",
  "instance": "my-instance-name",
  "data": { ... },
  "destination": "https://your-webhook-url.com/messages-upsert",
  "date_time": "2024-06-06T12:34:56.789Z",
  "sender": "553198296801@s.whatsapp.net",
  "server_url": "https://your-evolution-server.com",
  "apikey": "your-api-key-or-null"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `event` | string | Event name (e.g. `"messages.upsert"`) |
| `instance` | string | Instance name |
| `data` | object | Event-specific payload (see below) |
| `destination` | string | Target URL this was sent to |
| `date_time` | string | ISO 8601 timestamp (timezone-adjusted) |
| `sender` | string | Instance owner's JID |
| `server_url` | string | Evolution API server URL |
| `apikey` | string/null | API key (only if `AUTHENTICATION.EXPOSE_IN_FETCH_INSTANCES` is enabled) |

### MESSAGES_UPSERT Payload (`data` field)

This is the most important event. The `data` object contains:

```json
{
  "key": {
    "remoteJid": "553198296801@s.whatsapp.net",
    "fromMe": false,
    "id": "3EB0A0B1234567890",
    "participant": "553198296801@s.whatsapp.net"
  },
  "pushName": "John Doe",
  "messageType": "conversation",
  "message": {
    "conversation": "Hello, how are you?"
  },
  "contextInfo": {},
  "messageTimestamp": 1717689097,
  "status": "PENDING",
  "base64": "..."
}
```

| Field | Type | Description |
|-------|------|-------------|
| `key.remoteJid` | string | Chat/sender JID. For LID mode, this is **replaced** with `remoteJidAlt` (phone-based JID). |
| `key.fromMe` | boolean | `true` if sent by instance owner |
| `key.id` | string | Unique message ID |
| `key.participant` | string | Sender JID in group chats |
| `pushName` | string | Sender's display name |
| `messageType` | string | Type classification (see below) |
| `message` | object | Message content (varies by type) |
| `contextInfo` | object | Quoted message context, mentions, etc. |
| `messageTimestamp` | number | Unix timestamp |
| `status` | string | `PENDING`, `SERVER_ACK`, `DELIVERY_ACK`, `READ`, `PLAYED`, `DELETED`, `ERROR` |
| `base64` | string | Base64-encoded media (only if `webhookBase64: true` and message has media) |
| `mediaUrl` | string | S3/MinIO URL (only if S3 storage is configured) |

### Message Types in `messageType`
- `conversation` - Plain text
- `extendedTextMessage` - Text with link preview or mentions
- `imageMessage` - Image
- `videoMessage` - Video
- `audioMessage` - Audio
- `documentMessage` - Document/file
- `stickerMessage` - Sticker
- `ptvMessage` - Push-to-talk video (video note)
- `contactMessage` - Contact card
- `locationMessage` - Location
- `reactionMessage` - Reaction emoji
- `pollCreationMessage` - Poll
- `pollUpdateMessage` - Poll vote
- `protocolMessage` - Protocol/system message (edits, deletes)
- `viewOnceMessage` / `viewOnceMessageV2` - View-once media
- `ephemeralMessage` - Disappearing message
- `documentWithCaptionMessage` - Document with caption wrapper

### Media Message Content (when `messageType` = `imageMessage`)
```json
{
  "message": {
    "imageMessage": {
      "url": "https://mmg.whatsapp.net/...",
      "mimetype": "image/jpeg",
      "caption": "Photo caption",
      "fileSha256": "...",
      "fileLength": "123456",
      "height": 600,
      "width": 800,
      "mediaKey": "...",
      "fileEncSha256": "...",
      "directPath": "/v/...",
      "mediaKeyTimestamp": "1717689097",
      "jpegThumbnail": "base64...",
      "contextInfo": {}
    },
    "base64": "..."
  }
}
```

### Webhook Data Cleaning (before transmission)
The `cleanMessageData` method strips binary data before sending:
- Removes `message.base64`
- Strips `imageMessage` to caption only
- Strips `videoMessage` to caption only
- Strips `audioMessage` to seconds duration only
- Strips `stickerMessage` to empty object
- Preserves `documentMessage` caption and file name
- Preserves `mediaUrl` if present

**Note**: This cleaning happens for internal storage/API responses. When `webhookBase64` is enabled, the base64 content IS included in the webhook payload before cleaning.

### MESSAGES_UPDATE Payload
```json
{
  "key": {
    "remoteJid": "553198296801@s.whatsapp.net",
    "fromMe": true,
    "id": "BAE594145F4C59B4"
  },
  "update": {
    "status": "DELIVERY_ACK"
  }
}
```

### SEND_MESSAGE Payload
Same structure as MESSAGES_UPSERT but triggered when a message is sent via the API (not via WhatsApp directly).

### CONNECTION_UPDATE Payload
```json
{
  "state": "open",
  "statusReason": 200
}
```
States: `"open"`, `"close"`, `"connecting"`

### PRESENCE_UPDATE Payload
```json
{
  "id": "553198296801@s.whatsapp.net",
  "presences": {
    "553198296801@s.whatsapp.net": {
      "lastKnownPresence": "composing"
    }
  }
}
```
Presence values: `"available"`, `"unavailable"`, `"composing"`, `"recording"`, `"paused"`

### GROUP_PARTICIPANTS_UPDATE Payload
```json
{
  "id": "123456789-987654321@g.us",
  "participants": [
    {
      "jid": "553198296801@s.whatsapp.net",
      "phoneNumber": "553198296801",
      "name": "John",
      "imgUrl": "https://..."
    }
  ],
  "action": "add"
}
```
Actions: `"add"`, `"remove"`, `"promote"`, `"demote"`

**Note on participant resolution**: The system resolves participant phone numbers from LID data:
```typescript
const resolvedParticipants = participantsUpdate.participants.map((participantId) => {
  const participantData = groupParticipants.participants.find((p) => p.id === participantId);
  let phoneNumber;
  if (participantData?.phoneNumber) {
    phoneNumber = participantData.phoneNumber;
  } else {
    phoneNumber = normalizePhoneNumber(participantId); // strips @suffix
  }
  return { jid: participantId, phoneNumber, name: participantData?.name, imgUrl: participantData?.imgUrl };
});
```

### Webhook Delivery
- **Transport**: HTTP POST via axios
- **Timeout**: 30 seconds (configurable via `webhookConfig.REQUEST.TIMEOUT_MS`)
- **Retry**: Exponential backoff, max 10 attempts, initial delay 5 seconds, with jitter
- **Content-Type**: application/json

---

## 15. LID vs JID Handling

### O que é LID?
LID (Linked ID) é um modo de endereçamento do WhatsApp onde contatos são identificados por um LID (`xxxxx@lid`) ao invés do JID baseado em telefone (`xxxxx@s.whatsapp.net`). O WhatsApp está migrando gradualmente para LID.

### Comportamento REAL observado (instância AutoSell)

> **IMPORTANTE**: O código fonte da Evolution API indica que o `remoteJid` deveria ser substituído pelo JID (telefone) antes de enviar o webhook. **Na prática isso NÃO acontece** — o `remoteJid` chega como LID e o telefone vem em `key.senderPn`.

#### Payload REAL - Mensagem recebida (fromMe=false)
```json
{
  "key": {
    "remoteJid": "132985256960177@lid",
    "fromMe": false,
    "id": "AC9E03C258E9C305F4F5FB377E528BC2",
    "senderPn": "554599037399@s.whatsapp.net"
  },
  "pushName": "Caroline Paiva",
  "messageType": "imageMessage",
  "messageTimestamp": 1774098792,
  "source": "android"
}
```
- `key.remoteJid` = LID (NÃO é o telefone)
- `key.senderPn` = JID com telefone real do contato (SÓ presente em fromMe=false)
- `pushName` = Nome do contato (SÓ confiável em fromMe=false)

#### Payload REAL - Mensagem enviada externamente (fromMe=true)
```json
{
  "key": {
    "remoteJid": "132985256960177@lid",
    "fromMe": true,
    "id": "AC9783550E78AD35F7425FCE920A3242"
  },
  "pushName": "Vitor Fernandes",
  "messageType": "conversation",
  "messageTimestamp": 1774099310,
  "source": "android"
}
```
- `key.remoteJid` = LID do destinatário
- `key.senderPn` = NÃO EXISTE
- `pushName` = Nome da instância (NÃO do contato)

#### Payload REAL - Mensagem enviada via API/LiveChat (send.message)
```json
{
  "event": "send.message",
  "data": {
    "key": {
      "remoteJid": "132985256960177@lid",
      "fromMe": true,
      "id": "3EB070F0584DDE07E04CDAC948322F0DB37A27E4"
    },
    "pushName": "Você",
    "status": "PENDING",
    "messageType": "conversation",
    "source": "unknown"
  },
  "sender": "554598231771@s.whatsapp.net"
}
```
- `key.remoteJid` = LID do destinatário
- `sender` (top-level) = Número da instância, NÃO do contato

#### Payload REAL - Atualização de contato (contacts.update)
```json
{
  "event": "contacts.update",
  "data": [{
    "remoteJid": "132985256960177@lid",
    "profilePicUrl": "https://pps.whatsapp.net/..."
  }],
  "sender": "554598231771@s.whatsapp.net"
}
```

### Envio de mensagens e LID
- Enviar para LID é **instável** — funciona para alguns LIDs, falha para outros
- O endpoint sendText aceita número de telefone com código do país (ex: `554599037399`)
- **Recomendação**: Sempre enviar pelo telefone (JID), usar LID apenas como fallback

### Resumo dos campos por tipo de evento

| Campo | fromMe=false | fromMe=true (externo) | send.message (API) |
|-------|-------------|----------------------|-------------------|
| `key.remoteJid` | LID | LID | LID |
| `key.senderPn` | Telefone real | Ausente | Ausente |
| `pushName` | Nome do contato | Nome da instância | "Você" |
| `sender` (top-level) | Instância | Instância | Instância |

### Regras de Negócio derivadas
1. `senderPn` é a ÚNICA fonte confiável do telefone do contato
2. `pushName` só deve ser usado para nome quando `fromMe=false`
3. Mensagens `fromMe=true` devem criar contato apenas com LID, sem nome/telefone
4. O telefone será preenchido quando o contato enviar uma mensagem (fromMe=false)

---

## 16. Number Parameter Behavior

### How the `number` parameter works in send endpoints

The `number` field in sendText, sendMedia, and other send endpoints accepts multiple formats:

#### Accepted Formats
1. **Plain phone number** (recommended): `"5531999999999"` - Must include country code
2. **JID format**: `"5531999999999@s.whatsapp.net"` - Full WhatsApp JID
3. **Group JID**: `"123456789-987654321@g.us"` - Group chat JID
4. **Broadcast**: `"status@broadcast"` - Status broadcast

#### Internal Resolution Flow
```
number → createJid() → whatsappNumber() → sender JID
```

1. **`createJid(number)`**: Converts raw input to proper JID format:
   - If already contains `@g.us`, `@s.whatsapp.net`, `@lid`, or `@broadcast` → returned as-is
   - If 24+ chars with hyphen → treated as group, appends `@g.us`
   - For MX/AR numbers (country code 52/54): reformats 13-digit numbers
   - For BR numbers (country code 55): applies specific regex formatting
   - Otherwise: appends `@s.whatsapp.net`

2. **`whatsappNumber()`**: Validates the number exists on WhatsApp:
   - Returns `{ jid, exists, number, name, lid }`
   - If `exists === false` AND not a group/broadcast → throws `BadRequestException`

3. **Final sender**: `isWA.jid.toLowerCase()` - the validated, lowercased JID

#### Country-Specific Formatting
- **Brazil (55)**: Regex `/^(\d{2})(\d{2})\d{1}(\d{8})$/` with conditional logic based on digit positions
- **Mexico (52)** / **Argentina (54)**: 13-digit numbers are reformatted (country code + substring from position 3)

---

## 17. DTOs / Data Types Reference

### Base Metadata Class (shared by all send endpoints)
```typescript
export class Metadata {
  number: string;           // Recipient number/JID
  delay?: number;           // Typing presence delay in ms
  quoted?: Quoted;          // Quote/reply context
  linkPreview?: boolean;    // Show URL preview
  mentionsEveryOne?: boolean; // Mention all in group
  mentioned?: string[];     // Specific JIDs to mention
  encoding?: boolean;       // Encoding option
  notConvertSticker?: boolean; // Skip sticker conversion
}
```

### SendTextDto
```typescript
export class SendTextDto extends Metadata {
  text: string;
}
```

### SendMediaDto
```typescript
export class SendMediaDto extends Metadata {
  mediatype: MediaType;    // 'image' | 'video' | 'document'
  mimetype?: string;       // MIME type
  caption?: string;        // Caption text
  fileName?: string;       // File name
  media: string;           // URL or base64
}
```

### Other Send DTOs (all extend Metadata)
| DTO | Additional Fields |
|-----|-------------------|
| `SendAudioDto` | `audio: string` |
| `SendStickerDto` | `sticker: string` |
| `SendPtvDto` | `video: string` (push-to-talk video) |
| `SendLocationDto` | `latitude: number`, `longitude: number`, `name: string`, `address: string` |
| `SendContactDto` | `contact: ContactMessage[]` |
| `SendPollDto` | `name: string`, `selectableCount: number`, `values: string[]`, `messageSecret: string` |
| `SendReactionDto` | `key: Key`, `reaction: string` (does NOT extend Metadata) |
| `SendButtonsDto` | `thumbnailUrl`, `title`, `description`, `footer`, `buttons` |
| `SendListDto` | `title`, `description`, `footerText`, `buttonText`, `sections` |
| `SendStatusDto` | `type`, `content`, `statusJidList`, `allContacts`, `caption`, `backgroundColor`, `font` |
| `SendTemplateDto` | `name`, `language`, `components`, `webhookUrl` |

### Chat DTOs
| DTO | Fields |
|-----|--------|
| `OnWhatsAppDto` | `jid`, `exists`, `number`, `name`, `lid` |
| `WhatsAppNumberDto` | `numbers: string[]` |
| `NumberDto` | `number: string` |
| `ReadMessageDto` | `readMessages: Key[]` |
| `Key` | `id`, `fromMe`, `remoteJid` |
| `SendPresenceDto` | extends Metadata + `presence`, `delay` |
| `UpdateMessageDto` | extends Metadata + `key`, `text` |
| `ProfilePictureDto` | `number`, `picture` |
| `ArchiveChatDto` | `lastMessage`, `chat`, `archive` |
| `MarkChatUnreadDto` | `lastMessage`, `chat` |
| `BlockUserDto` | `number`, `status` |
| `DeleteMessage` | `id`, `fromMe`, `remoteJid`, `participant` |

### Type Constants
```typescript
// Media message types
export const TypeMediaMessage = [
  'imageMessage', 'documentMessage', 'audioMessage',
  'videoMessage', 'stickerMessage', 'ptvMessage',
];

// Message subtypes (wrappers)
export const MessageSubtype = [
  'ephemeralMessage', 'documentWithCaptionMessage',
  'viewOnceMessage', 'viewOnceMessageV2',
];

// Status values
export type StatusMessage =
  'ERROR' | 'PENDING' | 'SERVER_ACK' | 'DELIVERY_ACK' | 'READ' | 'DELETED' | 'PLAYED';
```

---

## 18. Internal Architecture Notes

### Message Send Pipeline
```
API Request → DTO Validation → sendMessageWithTyping() → whatsappNumber() validation
  → createJid() → typing delay (chunked 20s) → client.sendMessage() (Baileys)
  → prepareMessage() → save to DB → sendDataWebhook(SEND_MESSAGE)
```

### Message Receive Pipeline
```
Baileys messages.upsert event → BaileysMessageProcessor (RxJS queue, 3 retries)
  → Filter decrypt errors → Handle edits → Type filter (notify/append)
  → Chat upsert → prepareMessage() → Poll decryption (if poll)
  → LID resolution (remoteJidAlt swap) → Media download (if webhookBase64)
  → S3 upload (if configured) → Save to DB → Chatwoot sync → sendDataWebhook(MESSAGES_UPSERT)
```

### Event Manager Architecture
The `EventManager` broadcasts events to 7 channels simultaneously:
1. **WebSocket** - Real-time browser/client notifications
2. **Webhook** - HTTP POST to configured URLs (with retry)
3. **RabbitMQ** - Message queue integration
4. **NATS** - NATS messaging integration
5. **SQS** - AWS SQS integration
6. **Pusher** - Pusher real-time integration
7. **Kafka** - Kafka streaming integration

### Webhook Configuration (Global Environment Variables)
```env
WEBHOOK_GLOBAL_URL=https://your-global-webhook.com
WEBHOOK_GLOBAL_ENABLED=true
WEBHOOK_GLOBAL_WEBHOOK_BY_EVENTS=true
WEBHOOK_EVENTS_APPLICATION_STARTUP=true
WEBHOOK_EVENTS_QRCODE_UPDATED=true
WEBHOOK_EVENTS_ERRORS=true
WEBHOOK_EVENTS_ERRORS_WEBHOOK=https://custom-error-webhook.com
```

### Webhook LocalType Definition
```typescript
export type LocalWebHook = LocalEvent & {
  url?: string;
  headers?: JsonValue;       // Custom headers (supports JWT via jwt_key)
  webhookByEvents?: boolean; // Append event name to URL
  webhookBase64?: boolean;   // Include base64 media in payloads
};
```

---

## Global Configuration Notes

### Instance vs Global Webhooks
- **Instance-level**: Configured per instance via `POST /webhook/set/{instance}`. Preferred for granular control.
- **Global-level**: Configured via `.env` file. Applies to all instances. Use for unified event handling.

### JSON Validation
The documentation emphasizes: "It is extremely necessary that the payload follows the rules to create a JSON file." Validate syntax at https://jsonlint.com/ before API calls.

### OpenAPI Specification
Available at:
- `https://doc.evolution-api.com/openapi/openapi-v2.json`
- `https://doc.evolution-api.com/openapi/openapi-v1.json`
