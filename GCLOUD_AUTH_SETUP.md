# Google Cloud Vision API Setup - Using Application Default Credentials

This guide explains how to set up Google Cloud Vision API using **Application Default Credentials (ADC)**, which is more secure than service account keys and is the recommended approach when your organization has disabled service account key creation.

## Why Application Default Credentials?

- **More Secure**: No JSON key files to manage or accidentally commit
- **Easier Rotation**: Credentials automatically refresh
- **Organization Compliant**: Works with policies that disable service account key creation
- **Google Recommended**: This is the official best practice

## Prerequisites

- Google account with access to your organization's Google Cloud project
- Terminal/Command line access
- Python virtual environment already set up

## Step-by-Step Setup

### 1. Install Google Cloud SDK (gcloud CLI)

First, check if you already have gcloud installed:

```bash
gcloud --version
```

If not installed, follow the instructions for your operating system:

#### On Ubuntu/Debian:
```bash
# Add Cloud SDK repo
echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | sudo tee -a /etc/apt/sources.list.d/google-cloud-sdk.list

# Import the Google Cloud public key
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key --keyring /usr/share/keyrings/cloud.google.gpg add -

# Update and install
sudo apt-get update && sudo apt-get install google-cloud-cli
```

#### On macOS:
```bash
# Using Homebrew
brew install google-cloud-sdk
```

#### On Windows:
Download the installer from: https://cloud.google.com/sdk/docs/install

### 2. Initialize gcloud

```bash
gcloud init
```

This will:
1. Open a browser window for you to sign in with your Google account
2. Ask you to select your Google Cloud project
3. Configure your default settings

**Important**: Make sure you select the correct project where Cloud Vision API is enabled.

### 3. Enable Cloud Vision API (if not already enabled)

You can enable it via gcloud:

```bash
# Replace PROJECT_ID with your actual project ID
gcloud services enable vision.googleapis.com --project=PROJECT_ID
```

Or enable it in the Google Cloud Console:
1. Go to https://console.cloud.google.com/apis/library
2. Search for "Cloud Vision API"
3. Click "Enable"

### 4. Set Up Application Default Credentials

This is the key step - it creates credentials that your Python application can use:

```bash
gcloud auth application-default login
```

This command will:
1. Open a browser window
2. Ask you to sign in (if not already signed in)
3. Request permission to access Google Cloud APIs
4. Save credentials to your local machine at:
   - Linux/macOS: `~/.config/gcloud/application_default_credentials.json`
   - Windows: `%APPDATA%\gcloud\application_default_credentials.json`

**Important**: These credentials are stored locally and are automatically used by the Google Cloud Python libraries.

### 5. Verify Your Setup

Set your project ID (replace with your actual project):

```bash
export GOOGLE_CLOUD_PROJECT=your-project-id
# Or add to your .env file:
# GOOGLE_CLOUD_PROJECT=your-project-id
```

Now test the setup:

```bash
cd /home/sanjotbains/Documents/sikh_temple_membership/backend
source venv/bin/activate
python test_vision_api.py
```

You should see:
```
✅ SUCCESS! Vision API is configured correctly!
```

## Using in Your Application

Your Python code will automatically use Application Default Credentials when you initialize the Vision API client:

```python
from google.cloud import vision

# No explicit credentials needed!
# It automatically uses ADC
client = vision.ImageAnnotatorClient()
```

The library checks for credentials in this order:
1. `GOOGLE_APPLICATION_CREDENTIALS` environment variable (if set)
2. Application Default Credentials (what we just set up)
3. Compute Engine/App Engine/Cloud Run service account

## Common Issues and Solutions

### Issue: "Could not automatically determine credentials"

**Solution**: Make sure you ran `gcloud auth application-default login` and completed the browser authentication.

### Issue: "Permission denied" or "API not enabled"

**Solution**:
- Verify the Cloud Vision API is enabled in your project
- Check that your Google account has the necessary permissions
- You may need to ask your organization admin for the "Cloud Vision AI User" role

### Issue: "Wrong project selected"

**Solution**: Set the correct project:
```bash
gcloud config set project YOUR_PROJECT_ID
gcloud auth application-default login
```

### Issue: Credentials expired

**Solution**: Re-authenticate:
```bash
gcloud auth application-default login
```

## For Production Deployment

When deploying to production, you have several options:

### Option 1: Cloud Run / App Engine / Compute Engine
These services automatically provide credentials through their service accounts. No additional setup needed!

### Option 2: Workload Identity Federation
For deployments outside Google Cloud (AWS, Azure, on-premise), use Workload Identity Federation:
```bash
# Your organization admin would set this up
gcloud iam workload-identity-pools create-cred-config \
  projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/POOL_ID/providers/PROVIDER_ID \
  --service-account=SERVICE_ACCOUNT_EMAIL \
  --output-file=credentials.json
```

Then set: `GOOGLE_APPLICATION_CREDENTIALS=credentials.json`

### Option 3: Service Account with Different Authentication
If your organization allows other authentication methods, consult with your cloud admin about approved options.

## Security Best Practices

1. **Never commit ADC credentials**
   - The credentials file is in your home directory, not in your project
   - Still, never copy it into your project repo

2. **Refresh regularly**
   - Re-run `gcloud auth application-default login` periodically
   - Credentials have a limited lifetime and will auto-refresh

3. **Use service accounts in production**
   - ADC with your personal account is for development only
   - Production should use service accounts or workload identity

4. **Minimal permissions**
   - Request only "Cloud Vision AI User" role from your admin
   - Avoid using admin-level accounts for development

## Quick Reference

```bash
# Install gcloud SDK
sudo apt-get install google-cloud-cli  # Linux
brew install google-cloud-sdk          # macOS

# Initialize
gcloud init

# Set up Application Default Credentials
gcloud auth application-default login

# Set project
gcloud config set project PROJECT_ID

# Enable Vision API
gcloud services enable vision.googleapis.com

# Test your setup
cd backend && source venv/bin/activate
python test_vision_api.py

# View current configuration
gcloud config list

# Revoke credentials (if needed)
gcloud auth application-default revoke
```

## Getting Help

- **gcloud command help**: `gcloud auth --help`
- **Check your project**: `gcloud config get-value project`
- **List enabled APIs**: `gcloud services list --enabled`
- **Vision API docs**: https://cloud.google.com/vision/docs
- **ADC documentation**: https://cloud.google.com/docs/authentication/application-default-credentials

## Cost Information

Same as with service account keys:

**Free Tier** (first 1,000 units/month):
- Text Detection: FREE
- Document Text Detection: FREE

**Paid Tier** (after 1,000 units/month):
- Text Detection: $1.50 per 1,000 images
- Document Text Detection: $1.50 per 1,000 images

Monitor your usage:
```bash
# View billing in browser
gcloud alpha billing accounts list
```

Or check in Cloud Console: https://console.cloud.google.com/billing
