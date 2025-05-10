Test


For Whatsapp:

1. Register the number
```
curl -i -X POST \
 "https://graph.facebook.com/v22.0/665008633363562/register" \
-H "Authorization: Bearer <Bearer>" \
-H "Content-Type: application/json" \
-d '{ "messaging_product": "whatsapp", "pin": "154315" }'
```

2. Send a Hello World
```
curl -i -X POST \
 "https://graph.facebook.com/v22.0/665008633363562/messages" \
-H "Authorization: Bearer <Bearer>" \
-H "Content-Type: application/json" \
-d '{ "messaging_product": "whatsapp", "to": "33684152167", "type": "template", "template": { "name": "hello_world", "language": { "code": "en_US" } } }'
```

3. The receiver must answer in Whatsapp

4. Send a text message
```
curl -i -X POST \
 "https://graph.facebook.com/v22.0/665008633363562/messages" \
-H "Authorization: Bearer <Bearer>" \
-H "Content-Type: application/json" \
-d '{ "messaging_product": "whatsapp", "recipient_type": "group", "to": "JSHURsM7QWO7uoSfTi7Yn3", "type": "text", "text": { "preview_url": false, "body": "yolo" } }'
```

Note: Currently it's no more possible to send message to a Group