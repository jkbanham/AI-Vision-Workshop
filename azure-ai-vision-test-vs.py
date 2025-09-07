import os
import cv2
from PIL import Image
import webcolors
from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.ai.vision.imageanalysis.models import VisualFeatures
from azure.core.credentials import AzureKeyCredential
from azure.storage.blob import BlobServiceClient

# Static global variables here...

img_file = '.\\venv\\WEBCAM-IMAGES\\sort-object.jpg'  # The name (and file path) of the image file which will be capture and analyzed


# Reusable functions here:
def open_image_in_new_window(image_path):
    """Opens an image file in a new window using Pillow."""
    try:
        img = Image.open(image_path)
        img.show()
    except FileNotFoundError:
        print(f"Error: Image file not found at '{image_path}'")
    except Exception as e:
        print(f"An error occurred: {e}")


#######################

# Initialize the webcam
cap = cv2.VideoCapture(0)

#Check if the camera opened successfully
if not cap.isOpened():
    raise IOError("Cannot open webcam")

#Create a window named "Webcam Feed"
cv2.namedWindow("Webcam Feed")

print("Press c to capture the frame...")

#Loop to continuously get frames from the webcam until user types a 'c'
while(True):
    #Read a frame from the webcam
    ret, frame = cap.read()

    #If frame was read correctly, show it
    if ret:
        cv2.imshow("Webcam Feed", frame)

    #Break the loop when 'c' key is pressed
    if cv2.waitKey(1) & 0xFF == ord('c'):
        break

# Capture a frame
ret, frame = cap.read()

# Save the captured image
if ret:
    cv2.imwrite(img_file, frame)
    print("Webcam image captured...")
else:
    print("Error capturing image")

#Release the capture object and destroy all windows
cap.release()
cv2.destroyAllWindows()

# Open the webcam image in a new window and show it on the user's screen
open_image_in_new_window(img_file)

# Now need to write the image into the azure blob storage container...


container_name = "ai-vision-test"
blob_name = "sort-object"  # The name you want to assign to the uploaded file


def upload_blob(img_file, container_name, blob_name):
    # Create a BlobServiceClient
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)

    # Get a client to interact with the specified container
    container_client = blob_service_client.get_container_client(container_name)

    # Create the container if it does not exist
    try:
        container_client.create_container()
    except Exception as e:
        print(f"Container already exists or could not be created: {e}")

    # Upload the file
    with open(img_file, "rb") as data:
        container_client.upload_blob(name=blob_name, data=data, overwrite=True)

    # Construct and return the URL of the uploaded file
    blob_url = f"https://{blob_service_client.account_name}.blob.core.windows.net/{container_name}/{blob_name}"
    return blob_url

# Upload the file and print the URL
uploaded_file_url = upload_blob(img_file, container_name, blob_name)
print("Uploaded file URL:", uploaded_file_url)

# Create an Image Analysis client
client = ImageAnalysisClient(
    endpoint=endpoint,
    credential=AzureKeyCredential(key)
)

# Get a caption for the image. This will be a synchronously (blocking) call.
result = client.analyze_from_url(
    image_url=uploaded_file_url,
    visual_features=[VisualFeatures.CAPTION, VisualFeatures.READ],
    gender_neutral_caption=True,  # Optional (default is False)
)

print("Image analysis results:")
# Print caption results to the console
print(" Caption:")
if result.caption is not None:
    print(f"   '{result.caption.text}', Confidence {result.caption.confidence:.4f}")

# Print text (OCR) analysis results to the console
print(" Text in image (if any):")
if result.read.blocks:
    for line in result.read.blocks[0].lines:
        print(f"   Line: '{line.text}', Bounding box {line.bounding_polygon}")
        for word in line.words:
            print(f"     Word: '{word.text}', Bounding polygon {word.bounding_polygon}, Confidence {word.confidence:.4f}")

