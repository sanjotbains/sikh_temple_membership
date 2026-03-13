# LAN Access Guide

## Your Network Configuration
- **Host Machine IP**: 192.168.1.17
- **Frontend Port**: 5173
- **Backend Port**: 5000

## How to Access from Other Devices on Your LAN

### For Users on the Same Network:
1. Open a web browser on any device connected to your LAN
2. Navigate to: **http://192.168.1.17:5173**
3. The app should load and work normally

### Starting the Servers

#### Backend (Terminal 1):
```bash
cd /home/sanjotbains/Documents/sikh_temple_membership/backend
source venv/bin/activate
python app.py
```

The backend will be accessible at:
- From host: http://localhost:5000
- From LAN: http://192.168.1.17:5000

#### Frontend (Terminal 2):
```bash
cd /home/sanjotbains/Documents/sikh_temple_membership/frontend
npm run dev
```

The frontend will be accessible at:
- From host: http://localhost:5173
- From LAN: http://192.168.1.17:5173

## Firewall Configuration

If other devices cannot connect, you may need to allow the ports through your firewall:

### Ubuntu/Debian:
```bash
sudo ufw allow 5173/tcp
sudo ufw allow 5000/tcp
```

### Check if firewall is active:
```bash
sudo ufw status
```

### Temporarily disable firewall for testing (not recommended for production):
```bash
sudo ufw disable
```

## Troubleshooting

### Can't connect from other devices?
1. **Check firewall**: Make sure ports 5173 and 5000 are open
2. **Verify IP address**: Run `hostname -I` to confirm your LAN IP
3. **Check both servers are running**: You should see both backend and frontend running in separate terminals
4. **Try pinging**: From another device, run `ping 192.168.1.17` to verify network connectivity

### IP Address Changed?
If your router assigns a new IP address (DHCP), you'll need to update:
1. `/home/sanjotbains/Documents/sikh_temple_membership/frontend/vite.config.js` - Line 18
2. Restart the frontend server

### For Static IP (Recommended):
Consider setting a static IP for your host machine in your router's settings to avoid IP changes.

## Security Notes

⚠️ **Important**:
- The current configuration allows **all origins** for CORS (for development convenience)
- Only use this configuration on trusted local networks
- For production deployment, configure specific allowed origins in `/backend/.env`
- Consider adding authentication for production use

## Network Access Summary

| Service | Localhost | LAN Access | Port |
|---------|-----------|------------|------|
| Frontend | http://localhost:5173 | http://192.168.1.17:5173 | 5173 |
| Backend | http://localhost:5000 | http://192.168.1.17:5000 | 5000 |
| Health Check | http://localhost:5000/health | http://192.168.1.17:5000/health | 5000 |

## Testing LAN Access

### From another device on your network:
1. Open a browser and go to: http://192.168.1.17:5000/health
   - You should see: `{"status":"healthy","message":"Sikh Temple Membership System API is running"}`
2. Then go to: http://192.168.1.17:5173
   - The full application should load

### From your host machine:
- You can still use http://localhost:5173 as before
- Or use http://192.168.1.17:5173 (same as LAN users)
