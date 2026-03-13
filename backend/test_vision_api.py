"""
Test script for Google Cloud Vision API setup
Run this after setting up your service account credentials
"""
import os
from dotenv import load_dotenv
from google.cloud import vision

# Load environment variables
load_dotenv()

def test_vision_api():
    """Test if Vision API is configured correctly"""

    print("Testing Google Cloud Vision API setup...")
    print("-" * 50)

    # Check authentication method
    credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

    print("1. Authentication Method")
    if credentials_path:
        print(f"   Using service account key: {credentials_path}")
        if not os.path.exists(credentials_path):
            print(f"   ❌ ERROR: Credentials file not found at {credentials_path}")
            return False
        print("   ✓ Credentials file exists")
    else:
        print("   Using Application Default Credentials (ADC)")
        print("   ✓ This is the recommended method")

        # Check if ADC is set up
        adc_path_linux = os.path.expanduser("~/.config/gcloud/application_default_credentials.json")
        adc_path_windows = os.path.expanduser("~/AppData/Roaming/gcloud/application_default_credentials.json")

        if os.path.exists(adc_path_linux):
            print(f"   ✓ Found ADC credentials at {adc_path_linux}")
        elif os.path.exists(adc_path_windows):
            print(f"   ✓ Found ADC credentials at {adc_path_windows}")
        else:
            print("   ⚠ Warning: ADC credentials not found")
            print("   Run: gcloud auth application-default login")

    # Try to initialize client
    try:
        client = vision.ImageAnnotatorClient()
        print("2. Vision API Client")
        print("   ✓ Successfully initialized Vision API client")
    except Exception as e:
        print(f"   ❌ ERROR: Failed to initialize client: {e}")
        return False

    # Try a simple test (text detection on a small test image)
    print("\n3. Testing API Connection")
    print("   Creating a test image with text...")

    try:
        # Create a simple test image with text
        from PIL import Image, ImageDraw, ImageFont
        import io

        # Create a white image with black text
        img = Image.new('RGB', (300, 100), color='white')
        draw = ImageDraw.Draw(img)
        draw.text((10, 30), "Test OCR", fill='black')

        # Convert to bytes
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()

        # Test Vision API
        image = vision.Image(content=img_byte_arr)
        response = client.text_detection(image=image)

        if response.error.message:
            print(f"   ❌ ERROR: Vision API returned an error: {response.error.message}")
            return False

        # Check if text was detected
        texts = response.text_annotations
        if texts:
            detected_text = texts[0].description.strip()
            print(f"   ✓ Successfully detected text: '{detected_text}'")
        else:
            print("   ⚠ Warning: No text detected (API is working but might need better test)")

        print("\n" + "=" * 50)
        print("✅ SUCCESS! Vision API is configured correctly!")
        print("=" * 50)
        return True

    except Exception as e:
        print(f"   ❌ ERROR: API test failed: {e}")
        print("\n" + "=" * 50)
        print("TROUBLESHOOTING:")
        print("=" * 50)
        print("1. Make sure gcloud is installed:")
        print("   Run: gcloud --version")
        print()
        print("2. Authenticate with Application Default Credentials:")
        print("   Run: gcloud auth application-default login")
        print()
        print("3. Set your project:")
        print("   Run: gcloud config set project YOUR_PROJECT_ID")
        print()
        print("4. Enable the Vision API:")
        print("   Run: gcloud services enable vision.googleapis.com")
        print()
        print("See GCLOUD_AUTH_SETUP.md for detailed instructions")
        print("=" * 50)
        return False

if __name__ == '__main__':
    success = test_vision_api()
    exit(0 if success else 1)
