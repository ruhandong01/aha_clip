# Quick Start Guide - Deploy Aha Clip in 10 Minutes

## 🚀 Fastest Deployment Options

### Option 1: Heroku (Recommended for MVP)
**Time**: 5-10 minutes
**Cost**: $7/month

```bash
# 1. Install Heroku CLI
brew install heroku/brew/heroku  # macOS
# or download from https://devcenter.heroku.com/articles/heroku-cli

# 2. Login to Heroku
heroku login

# 3. Create app
heroku create your-aha-clip-app

# 4. Set environment variables
heroku config:set OPENAI_API_KEY="your-openai-api-key"
heroku config:set SECRET_KEY="your-secret-key"
heroku config:set FLASK_ENV="production"

# 5. Deploy
git add .
git commit -m "Initial deployment"
git push heroku main

# 6. Open your app
heroku open
```

### Option 2: DigitalOcean App Platform
**Time**: 10-15 minutes
**Cost**: $12/month

1. Go to [DigitalOcean App Platform](https://cloud.digitalocean.com/apps)
2. Click "Create App"
3. Connect your GitHub repository
4. Configure:
   - **Source**: `server.py`
   - **Environment**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Run Command**: `gunicorn --config gunicorn.conf.py wsgi:app`
5. Add environment variables:
   - `OPENAI_API_KEY`: your-openai-api-key
   - `SECRET_KEY`: your-secret-key
   - `FLASK_ENV`: production
6. Click "Create Resources"

### Option 3: Local Development
**Time**: 2-3 minutes
**Cost**: $0

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Create .env file
cp env.example .env
# Edit .env with your OpenAI API key

# 3. Run locally
python server.py

# 4. Open http://localhost:5001
```

## 🔧 Required Setup

### 1. Environment Variables
Create a `.env` file:
```bash
cp env.example .env
```

Edit `.env`:
```env
SECRET_KEY=your-super-secret-key-here
OPENAI_API_KEY=your-openai-api-key-here
FLASK_ENV=production
```

### 2. OpenAI API Key
1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Create an account or sign in
3. Go to API Keys
4. Create a new API key
5. Add it to your `.env` file

### 3. Domain Name (Optional)
- Register a domain (Namecheap, GoDaddy, etc.)
- Point it to your hosting provider
- Enable HTTPS

## 📊 Cost Breakdown

### Monthly Costs:
- **Heroku Basic**: $7/month
- **DigitalOcean App Platform**: $12/month
- **Domain**: $10-15/year
- **OpenAI API**: $5-50/month (depends on usage)

### Total Monthly Cost:
- **Minimum**: $12-17/month
- **With heavy usage**: $50-100/month

## 🎯 Next Steps

1. **Deploy your app** using one of the options above
2. **Test all features**:
   - Image generation
   - Voice generation
   - Video creation
3. **Set up monitoring**:
   - Uptime monitoring (UptimeRobot - free)
   - Error tracking (Sentry - free tier)
4. **Optimize costs**:
   - Monitor OpenAI API usage
   - Implement rate limiting
   - Add caching

## 🆘 Troubleshooting

### Common Issues:

**1. OpenAI API Key Error**
```bash
# Check your environment variable
echo $OPENAI_API_KEY
# Make sure it's set correctly in your hosting platform
```

**2. Port Issues**
```bash
# For local development, make sure port 5001 is free
lsof -i :5001
# Kill process if needed
kill -9 <PID>
```

**3. Memory Issues**
- Upgrade to a larger plan
- Optimize image processing
- Implement background jobs

**4. Video Processing Timeout**
- Increase timeout settings in `gunicorn.conf.py`
- Consider using background jobs for video processing

## 📞 Support

- **Documentation**: Check `DEPLOYMENT_GUIDE.md`
- **Hosting Comparison**: See `HOSTING_COMPARISON.md`
- **Issues**: Create an issue in your repository

## 🚀 Ready to Deploy?

Choose your preferred option and follow the steps above. Your Aha Clip application will be live in minutes!

**Recommended for first-time deployment**: Start with **Heroku** - it's the easiest and most reliable for beginners. 