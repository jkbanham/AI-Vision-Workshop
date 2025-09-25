# Import Python modules that we will utilize

import os
import cv2
from PIL import Image
import webcolors
from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.ai.vision.imageanalysis.models import VisualFeatures
from azure.core.credentials import AzureKeyCredential
from azure.storage.blob import BlobServiceClient
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials
import serial
import time

# Import the credentials that we will use to connect to the various Azure services (stored in a separate local file outside of git)
import config

# Static global variables are defined here...
img_file = '.\\venv\\WEBCAM-IMAGES\\sort-object.jpg'  # The name (and file path) of the image file which will be capture and analyzed
com_port = 'COM4'  # COM port for Arduino board connection (USB)


# Reusable functions here:

def get_image_frame_from_webcam():
    """Returns a single frame (image) from the webcam"""
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
        cv2.imwrite(img_file, frame) # This overwrites the existing jpeg file defined in the static global variable defined above
        print("\nWebcam image captured...\n")
    else:
        print("\nError capturing image\n")

    #Release the capture object and destroy all windows
    cap.release()
    cv2.destroyAllWindows()



def open_image_in_new_window(image_path):
    """Opens an image file in a new window using Pillow."""
    try:
        img = Image.open(image_path)
        img.show()
    except FileNotFoundError:
        print(f"Error: Image file not found at '{image_path}'")
    except Exception as e:
        print(f"An error occurred: {e}")



def upload_blob(img_file, container_name, blob_name):
    """Uploads a file to an Azure blob storage container."""
    # Create a BlobServiceClient
    blob_service_client = BlobServiceClient.from_connection_string(config.storage_connection_string)

    # Get a client to interact with the specified container
    container_client = blob_service_client.get_container_client(container_name)

    # Create the container if it does not exist
    try:
        container_client.create_container()
    except Exception as e:
        #print(f"Error detail: {e}")  # Uncomment this if more detail on the error message is needed
        print("Azure blob container already exists or could not be created")

    # Upload the file
    with open(img_file, "rb") as data:
        container_client.upload_blob(name=blob_name, data=data, overwrite=True)

    # Construct and return the URL of the uploaded file
    blob_url = f"https://{blob_service_client.account_name}.blob.core.windows.net/{container_name}/{blob_name}"
    return blob_url


def move_servo(angle):
  """Sends a command to the Arduino to move a servo."""
  ser.write(bytes([angle]))
  time.sleep(2)  # Give time for the servo to move


#######################

# Initialize the webcam
cap = cv2.VideoCapture(0)  # 0 is the index of the usb attached camera (1 is the built-in camera)

# Check if the camera opened successfully
if not cap.isOpened():
    raise IOError("Cannot open webcam - make sure it is attached")

# Create a window named "Webcam Feed" to display what the webcam is seeing on to the console
cv2.namedWindow("Webcam Feed")

# Call the capture frame function here
get_image_frame_from_webcam()

# Call the function to open the webcam image in a new window and show it on the console
open_image_in_new_window(img_file)

# Now write the image into the azure blob storage container so that we can run various Azure AI tools against it...
container_name = "ai-vision-test"  # This is the storage container created in the Azure environment
blob_name = "sort-object"  # The name to assign to the uploaded file

# Upload the file and print the URL to the screen
uploaded_file_url = upload_blob(img_file, container_name, blob_name)
print("\nUploaded file URL in Azure is: ", uploaded_file_url)

# Analyze the image...

# Create an Image Analysis client to talk to the Azure Vision API service
ia_client = ImageAnalysisClient(
    endpoint=config.az_endpoint,
    credential=AzureKeyCredential(config.key)
)

# Analyze the image.
result = ia_client.analyze_from_url(
    image_url=uploaded_file_url,
    visual_features=[VisualFeatures.CAPTION, VisualFeatures.READ],
    gender_neutral_caption=True,  # Optional (default is False)
)

# Print caption results to the console
print("\nImage Analysis result returned this caption: ")
if result.caption is not None:
    print(f"   '{result.caption.text}'")

# Print text (OCR) analysis results to the console
print("\nText found in the image (if any): ")
if result.read.blocks:
    for line in result.read.blocks[0].lines:
        print(f"   '{line.text}'")


# Open the serial port for the Arduino attached servo motors...
try:
    ser = serial.Serial( com_port, 9600, timeout=1)

    # Calls to move the servo examples - use these based on logic of the responses back from the Azure AI calls...
    print("\nMoving servo back to start position")
    move_servo(90)  # Move servo 0 to zero degree position
    print("\nMoving servo to sort object to the right")
    move_servo(0)  # Move servo 0 to zero degree position
    print("\nMoving servo back to start position")
    move_servo(90)  # Move servo 0 to zero degree position
    print("\nMoving servo to sort object to the left")
    move_servo(180)  # Move servo 0 to 180 degree position
    print("\nMoving servo back to start position")
    move_servo(90)  # Move servo 0 to zero degree position

    ser.close()  # Close the serial port connection

except Exception as e:
    print(f"\nArduino servos not available.  Error detail is: {e}")
