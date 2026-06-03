# Deployment Guide

This guide covers how to deploy CineMatch to the internet.

---

## Option 1: Laptop + Cloudflare Tunnel (Recommended)

Run CineMatch from your laptop with **no open ports**, **free SSL**, and a public domain via Cloudflare Tunnel.

### Prerequisites

- A domain name (e.g., `mironshoh.me`) managed by Cloudflare
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed
- [cloudflared](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/install-and-setup/tunnel-guide/) installed

### Step 1: Set up Docker

Make sure Docker is running on your machine, then build and start the services:

```bash
cd CineMatch
docker compose up -d --build
```

- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8000/health`

Verify both are working locally before continuing.

### Step 2: Install cloudflared and set up the tunnel

```bash
# macOS (Homebrew)
brew install cloudflare/cloudflare/cloudflared

# Linux (direct download)
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64
sudo mv cloudflared-linux-amd64 /usr/local/bin/cloudflared
sudo chmod +x /usr/local/bin/cloudflared

# Windows (winget)
winget install cloudflare.cloudflared
```

### Step 3: Authenticate with Cloudflare

```bash
cloudflared tunnel login
```

This opens a browser window. Log in to your Cloudflare account and select the domain you want to use (e.g., `mironshoh.me`). This saves a certificate to `~/.cloudflared/cert.pem`.

### Step 4: Create a tunnel

```bash
cloudflared tunnel create cinematch
```

This creates a tunnel and outputs a **tunnel ID** (a UUID like `a1b2c3d4-...`). It also creates a credentials JSON file at `~/.cloudflared/<tunnel-id>.json`.

### Step 5: Configure DNS

In your Cloudflare dashboard:

1. Go to **DNS** → **Records**
2. Click **Add Record**
3. Enter:
   - **Type**: `CNAME`
   - **Name**: `cinematch` (your app will be at `cinematch.yourdomain.com`)
   - **Target**: `<your-tunnel-id>.cfargotunnel.com`
   - **Proxy status**: **Proxied** (orange cloud)
4. Click **Save**

### Step 6: Create tunnel config

Create `~/.cloudflared/config.yml`:

```yaml
tunnel: <your-tunnel-id>
credentials-file: /Users/<your-username>/.cloudflared/<tunnel-id>.json

ingress:
  - hostname: cinematch.yourdomain.com
    service: http://localhost:5173
  - service: http_status:404
```

Replace `<your-tunnel-id>`, `<your-username>`, and `yourdomain.com` with your actual values.

### Step 7: Run the tunnel

```bash
cloudflared tunnel run cinematch
```

Your app is now live at `https://cinematch.yourdomain.com`.

To keep it running in the background:

```bash
cloudflared tunnel install cinematch
cloudflared tunnel run cinematch &
```

### Updating the app

```bash
cd CineMatch
git pull
docker compose up -d --build
# Tunnel stays running automatically
```

---

## Option 2: VPS (DigitalOcean / Hetzner / AWS)

For a dedicated server with 24/7 uptime, use a VPS.

### Recommended Specs

| Provider | Plan | Cost | Notes |
|----------|------|------|-------|
| Hetzner | CX22 (2 vCPU, 4 GB RAM) | ~€4/month | Best value |
| DigitalOcean | Basic Droplet (2 vCPU, 4 GB RAM) | ~$6/month | Easy to set up |
| AWS | t3.medium (2 vCPU, 4 GB RAM) | ~$30/month | Overkill for this project |

The model file is ~221 MB and requires ~4 GB RAM at inference time.

### Setup steps

```bash
# SSH into your server
ssh root@your-server-ip

# Install Docker
curl -fsSL https://get.docker.com | sh

# Clone the project
git clone https://github.com/yourusername/CineMatch.git
cd CineMatch

# Create .env file
cat > .env << 'EOF'
DEBUG=false
MODEL_PATH=models/als_model.pkl
TMDB_API_KEY=your_tmdb_api_key
GEMINI_API_KEY=your_gemini_api_key
EOF

# Start the application
docker compose up -d --build
```

### Reverse proxy with Nginx (SSL)

Install Nginx and certbot:

```bash
apt install nginx certbot python3-certbot-nginx
```

Create an Nginx site config `/etc/nginx/sites-available/cinematch`:

```nginx
server {
    listen 80;
    server_name cinematch.yourdomain.com;

    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_buffering off;
        proxy_cache off;
    }

    location / {
        proxy_pass http://localhost:5173;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Enable the site and get SSL:

```bash
ln -s /etc/nginx/sites-available/cinematch /etc/nginx/sites-enabled/
certbot --nginx -d cinematch.yourdomain.com
```

---

## Option 3: Render (Free Tier)

[Render](https://render.com) offers a free tier suitable for low-traffic apps.

### Backend

1. Push your code to GitHub
2. In Render dashboard: **New** → **Web Service**
3. Connect your repository
4. Settings:
   - **Name**: `cinematch-backend`
   - **Root Directory**: `backend`
   - **Runtime**: `Docker`
   - **Plan**: Free
5. Add environment variables:
   - `MODEL_PATH`: `models/als_model.pkl`
6. Deploy

⚠️ The free tier spins down after 15 minutes of inactivity. First request after idle takes ~30 seconds to wake up.

### Frontend

1. **New** → **Static Site**
2. Connect your repository
3. Settings:
   - **Root Directory**: `frontend`
   - **Build Command**: `npm install && npm run build`
   - **Publish Directory**: `dist`
4. Set environment variable:
   - `VITE_API_BASE`: `https://cinematch-backend.onrender.com`

---

## Domain DNS Quick Reference

### Cloudflare DNS Records

| Type | Name | Content | Proxy |
|------|------|---------|-------|
| CNAME | `cinematch` | `<tunnel-id>.cfargotunnel.com` | Proxied |

### Namecheap → Cloudflare Nameservers

If your domain is on Namecheap, point it to Cloudflare:

1. In Namecheap: **Domain List** → **Manage** → **Nameservers**
2. Select **Custom DNS**
3. Enter Cloudflare's nameservers (shown in Cloudflare dashboard → your site)
4. Save

Propagation takes 5–30 minutes.

---

## Troubleshooting

### Backend won't start

```bash
# Check Docker logs
docker logs cine-match-backend-1

# Test locally
cd backend
OPENBLAS_NUM_THREADS=1 python3 -m uvicorn app.main:app --port 8000
```

### Tunnel fails to connect

```bash
# Verify the app is running locally
curl http://localhost:5173

# Restart the tunnel with verbose logging
cloudflared tunnel --loglevel debug run cinematch
```

### Model loading error

Ensure `models/als_model.pkl` exists. If not, run `notebooks/final_model.ipynb` to train and save it.

### Port already in use

```bash
# Find what's using the port
lsof -i :8000
lsof -i :5173

# Kill the process
kill -9 <PID>
```

### AI Chat not responding / truncated

- Check that `GEMINI_API_KEY` is set in `.env` and docker-compose picks it up (`docker compose exec backend env | grep GEMINI`)
- Ensure `data/processed/descriptions.json` exists (run `python3 scripts/fetch_descriptions.py`)
- Nginx must have `proxy_buffering off;` in the `/api/` location block

### TMDB fetch errors

```bash
# DNS / network errors — retry failed entries on a working network
python3 scripts/fetch_posters.py --retry-failed
python3 scripts/fetch_descriptions.py --retry-failed
```
