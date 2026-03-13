# Google Cloud Vision API Setup Guide - Service Account Method

> **⚠️ IMPORTANT**: This guide is for organizations that allow service account key creation.
>
> **If you see an error about "Service account key creation is disabled"**, use the recommended method instead:
>
> **→ See [GCLOUD_AUTH_SETUP.md](./GCLOUD_AUTH_SETUP.md) for Application Default Credentials (Recommended)**

---

This guide explains the legacy service account key method for setting up Google Cloud Vision API for OCR functionality.

## Prerequisites

- Google account
- Credit card (for Google Cloud - free tier includes 1000 Vision API calls/month)

## Step-by-Step Setup

### 1. Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a Project" at the top
3. Click "New Project"
4. Enter project name: `sikh-temple-membership` (or your preferred name)
5. Click "Create"
6. Wait for the project to be created and make sure it's selected

### 2. Enable Cloud Vision API

1. In the Google Cloud Console, go to **APIs & Services > Library**
   - Or visit: https://console.cloud.google.com/apis/library
2. Search for "Cloud Vision API"
3. Click on "Cloud Vision API"
4. Click **"Enable"**
5. Wait for the API to be enabled

### 3. Create a Service Account

1. Go to **IAM & Admin > Service Accounts**
   - Or visit: https://console.cloud.google.com/iam-admin/serviceaccounts
2. Click **"Create Service Account"**
3. Fill in the details:
   - **Service account name**: `vision-api-service`
   - **Service account ID**: (auto-generated)
   - **Description**: `Service account for Vision API OCR`
4. Click **"Create and Continue"**

### 4. Grant Permissions

1. In the "Grant this service account access to project" section:
   - Select role: **"Cloud Vision AI Service Agent"**
   - Or select: **"Viewer"** (minimum required)
2. Click **"Continue"**
3. Click **"Done"** (skip the optional user access step)

### 5. Create and Download Service Account Key

1. In the Service Accounts list, find the account you just created
2. Click on the service account email
3. Go to the **"Keys"** tab
4. Click **"Add Key"** > **"Create new key"**
5. Select **"JSON"** as the key type
6. Click **"Create"**
7. The JSON key file will be automatically downloaded to your computer

### 6. Install the Key in Your Project

1. Rename the downloaded JSON file to `service-account-key.json`
2. Move it to the backend directory:
   ```bash
   mv ~/Downloads/*-key.json /home/sanjotbains/Documents/sikh_temple_membership/backend/service-account-key.json
   ```
3. Verify the path in your `.env` file matches:
   ```
   GOOGLE_APPLICATION_CREDENTIALS=/home/sanjotbains/Documents/sikh_temple_membership/backend/service-account-key.json
   ```

### 7. Test Your Setup

Run the test script to verify everything is working:

```bash
cd /home/sanjotbains/Documents/sikh_temple_membership/backend
source venv/bin/activate
python test_vision_api.py
```

You should see:
```
✅ SUCCESS! Vision API is configured correctly!
```

## Troubleshooting

### Error: "GOOGLE_APPLICATION_CREDENTIALS not set"
- Make sure you created the `.env` file in the backend directory
- Verify the path in `.env` is correct

### Error: "Credentials file not found"
- Check that `service-account-key.json` exists in the backend directory
- Verify the path in `.env` matches the actual file location

### Error: "Permission denied" or "API not enabled"
- Make sure you enabled the Cloud Vision API in Google Cloud Console
- Verify the service account has the correct permissions
- Wait a few minutes after enabling the API (it can take time to propagate)

### Error: "Quota exceeded"
- The free tier includes 1,000 Vision API calls per month
- Check your usage in Google Cloud Console under "APIs & Services > Dashboard"
- Consider upgrading your billing if you need more

## Cost Information

**Free Tier** (first 1,000 units/month):
- Text Detection: FREE
- Document Text Detection: FREE

**Paid Tier** (after 1,000 units/month):
- Text Detection: $1.50 per 1,000 images
- Document Text Detection: $1.50 per 1,000 images

**Best Practices to Control Costs:**
- Only process images when necessary
- Implement caching for already-processed images
- Monitor your usage regularly
- Set up billing alerts in Google Cloud Console

## Security Best Practices

1. **Never commit credentials to Git**
   - The `.gitignore` file already excludes `*-key.json` files
   - Double-check before committing

2. **Restrict service account permissions**
   - Only grant the minimum required permissions
   - Regularly review and audit service account access

3. **Rotate keys periodically**
   - Create new keys every 90 days
   - Delete old keys after rotation

4. **Monitor API usage**
   - Set up billing alerts
   - Review API logs regularly
   - Watch for suspicious activity

## Next Steps

Once your Vision API is set up and tested:

1. Run your Flask application:
   ```bash
   cd backend
   source venv/bin/activate
   python app.py
   ```

2. Upload a test form image through the frontend

3. Check the OCR results in the database or API response

## Support

If you continue to have issues:
- Check the [Cloud Vision API documentation](https://cloud.google.com/vision/docs)
- Review the [Python client library docs](https://cloud.google.com/python/docs/reference/vision/latest)
- Check your application logs for detailed error messages
