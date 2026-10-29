# 🚀 Render + UptimeRobot 24/7 Deployment Guide

This guide allows you to run your Instagram Agent 24/7 in the cloud on Render's Free Tier **without ever sleeping**, using UptimeRobot (100% Free, NO credit card needed).

---

## 📋 Step 1: Push Project to GitHub

1. Create a free account on [GitHub.com](https://github.com) (if you haven't already).
2. Create a new **Private** repository named `instagram-agent`.
3. In PowerShell, push your code:
   ```powershell
   cd "D:\instagram agent"
   git remote add origin https://github.com/YOUR_USERNAME/instagram-agent.git
   git branch -M main
   git push -u origin main
   ```

---

## ☁️ Step 2: Create Free Web Service on Render

1. Sign up on [Render.com](https://render.com) using your GitHub account (No Card Needed).
2. Click **New +** → **Web Service**.
3. Connect your `instagram-agent` GitHub repository.
4. Settings:
   * **Name:** `instagram-agent`
   * **Language / Environment:** `Docker` *(Recommended - handles FFmpeg & video codecs automatically)*
   * **Instance Type:** `Free`
5. Click **Advanced** → **Add Environment Variable**:
   * **Key:** `IG_SESSION_B64`
   * **Value:** *(Copy the text inside `D:\instagram agent\RENDER_SESSION_ENV.txt` and paste it here)*
6. Click **Create Web Service**.

Render will build and deploy the container in ~2-3 minutes. Once live, Render will give you a public URL (e.g. `https://instagram-agent.onrender.com`).

---

## 🤖 Step 3: Keep-Alive with UptimeRobot (No Sleep Workaround)

1. Sign up on [UptimeRobot.com](https://uptimerobot.com) (100% Free, No Card Needed).
2. Click **+ Add New Monitor**:
   * **Monitor Type:** `HTTP(s)`
   * **Friendly Name:** `Instagram Agent`
   * **URL (or IP):** `https://YOUR-APP-NAME.onrender.com/`
   * **Monitoring Interval:** `5 minutes`
3. Click **Create Monitor**.

---

### 🎉 That's It!
* UptimeRobot will ping your Render server every 5 minutes.
* Render will think your app has active traffic and will **NEVER go to sleep**!
* Your agent's Auto-Pilot will run in the cloud 24/7, auto-creating and uploading fresh Reels and Posts daily even when your laptop is completely turned off!
