# Pre-Deployment Checklist

## ✅ Completed

### Code Quality
- [x] Removed test files (algorithms.cpp, calculator.js, etc.)
- [x] Removed AI emoji from PR reviews
- [x] Removed "Copilot" mentions from config
- [x] Cleaned up marketing AI language
- [x] Removed duplicate reviewer_agent/ folder
- [x] All core files audited for AI traces

### Project Structure
- [x] agent/ folder - complete
- [x] demo/ folder - clean production code only
- [x] .github/ folder - workflows configured
- [x] Root documentation - complete

### Core Files Status
```
agent/
├── server.py              ✓ Clean
├── worker.py              ✓ Clean
├── pr_review_worker.py    ✓ Clean (emoji removed)
├── issue_solver.py        ✓ Clean
├── pr_reviewer.py         ✓ Clean
├── ai_client.py           ✓ Clean
├── repo_manager.py        ✓ Clean
├── database.py            ✓ Clean
├── cli.py                 ✓ Clean
├── Dockerfile             ✓ Ready
├── docker-compose.yml     ✓ Ready
└── supervisord.conf       ✓ Ready

demo/
├── app.py                 ✓ Clean
├── broken_logic.py        ✓ Clean (has intentional bugs)
├── utils.py               ✓ Clean
└── tests/                 ✓ Clean
```

## 🚀 VPS Deployment Steps

### 1. SSH to VPS
```bash
ssh root@31.187.64.94
# Password: 9GE3drxNOHoDR
```

### 2. Install Dependencies
```bash
# Update system
apt update && apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
apt install docker-compose -y

# Install Git
apt install git -y
```

### 3. Clone Repository
```bash
cd /opt
git clone https://github.com/nidzhadizzatov/megaschool-ai-izzatov-nidzhad-2026.git
cd megaschool-ai-izzatov-nidzhad-2026/agent
```

### 4. Configure Environment
```bash
# Copy .env template
cp .env.example .env

# Edit .env with real credentials
nano .env
```

**Required .env variables:**
```env
# OpenAI (use provided key from instructor)
OPENAI_API_KEY=sk-proj-XXXXX...XXXXX  # Replace with actual key
OPENAI_MODEL=gpt-4o-mini

# GitHub (your token)
GITHUB_TOKEN=ghp_YOUR_TOKEN_HERE
GITHUB_WEBHOOK_SECRET=your_webhook_secret

# Server
SERVER_PORT=8000
WEBHOOK_PATH=/webhook
```

### 5. Configure GitHub App
Go to: https://github.com/settings/apps

**Webhook URL:** `http://31.187.64.94:8000/webhook`

**Webhook events:**
- [x] Issues (opened)
- [x] Pull requests (opened, synchronize)

**Permissions:**
- [x] Contents: Read & Write
- [x] Issues: Read & Write
- [x] Pull requests: Read & Write

### 6. Open Firewall Port
```bash
ufw allow 8000/tcp
ufw status
```

### 7. Start Services
```bash
cd /opt/megaschool-ai-izzatov-nidzhad-2026/agent
docker-compose up -d
```

### 8. Verify Deployment
```bash
# Check containers
docker-compose ps

# Check logs
docker-compose logs -f

# Test health endpoint
curl http://31.187.64.94:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "pending_issues": 0,
  "stats": {...}
}
```

### 9. Test with Issue
1. Go to your GitHub repo
2. Create new Issue: "Fix broken logic in demo/broken_logic.py"
3. Check webhook received: `docker-compose logs server`
4. Wait 5 seconds for worker to process
5. Verify PR created

## 🔍 Monitoring

### Check Status
```bash
# Container status
docker-compose ps

# Live logs
docker-compose logs -f

# Specific service logs
docker-compose logs server
docker-compose logs worker
docker-compose logs pr_review_worker
```

### Database
```bash
# View database content
cat /opt/megaschool-ai-izzatov-nidzhad-2026/agent/db.json | jq
```

### Restart Services
```bash
docker-compose restart
```

### Update Code
```bash
cd /opt/megaschool-ai-izzatov-nidzhad-2026
git pull
cd agent
docker-compose down
docker-compose up -d --build
```

## 🎯 Production Checklist

Before submission:
- [ ] VPS deployed and running
- [ ] Webhook receiving events
- [ ] Successfully processed 1 test Issue
- [ ] PR created automatically
- [ ] PR review posted comment
- [ ] All services stable (no crashes)
- [ ] Logs clean (no errors)

## 📊 Performance Metrics

Target SLA:
- Issue processing: < 2 minutes
- PR creation: < 30 seconds after analysis
- Review posting: < 1 minute
- Uptime: 99%+

## 🆘 Troubleshooting

### Webhook not received
```bash
# Check server logs
docker-compose logs server | grep webhook

# Verify GitHub App webhook URL
# Should be: http://31.187.64.94:8000/webhook

# Test webhook manually
curl -X POST http://31.187.64.94:8000/webhook \
  -H "Content-Type: application/json" \
  -d '{"action":"opened","issue":{"number":1}}'
```

### Worker not processing
```bash
# Check worker logs
docker-compose logs worker

# Verify database has pending issues
cat db.json | jq '.issues'

# Restart worker
docker-compose restart worker
```

### Out of memory
```bash
# Check resources
docker stats

# Cleanup old repos
rm -rf /opt/megaschool-ai-izzatov-nidzhad-2026/agent/repos/*
```

## ✅ Final Validation

Run these tests before submitting:

1. **Smoke Test**: Create Issue → Wait → Verify PR created
2. **Review Test**: Create PR → Wait → Verify review comment
3. **Stability Test**: Check logs for 5 minutes - no crashes
4. **Resource Test**: `docker stats` - memory < 1GB

---

**Repository**: https://github.com/nidzhadizzatov/megaschool-ai-izzatov-nidzhad-2026
**VPS IP**: 31.187.64.94
**Webhook**: http://31.187.64.94:8000/webhook
**Status**: Ready for deployment ✅
