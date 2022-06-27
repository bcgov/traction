# GRIP - Temporary Name Until Something Better Comes Along

## Minimal Viable Product

- Accept a key and secret and store them in the browser.
- Use the key and secret to authenticate with the server.
- Make a request to the server.

## Running the Development Environment

Node version `>=12.2.0`.

```bash
cd frontend
npm ci
npm run dev
```

## Running Docker

```bash
docker build -t grip .
docker run -d --name grip -p 3000:80 grip
```

The web page will now be hosted [here](localhost:3000).
