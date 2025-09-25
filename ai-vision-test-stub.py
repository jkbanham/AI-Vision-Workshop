
from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.ai.vision.imageanalysis.models import VisualFeatures
from azure.core.credentials import AzureKeyCredential

import config

img_file = '.\\venv\\WEBCAM-IMAGES\\sort-object.jpg' 

# Now create an Image Analysis client to talk to a different Azure service
ia_client = ImageAnalysisClient(
    endpoint=config.az_endpoint,
    credential=AzureKeyCredential(config.key)
)

# Get a caption for the image.
result = ia_client.analyze_from_url(
    image_url="https://aistoragewkshp.blob.core.windows.net/ai-vision-test/sort-object",
    visual_features=[VisualFeatures.CAPTION, VisualFeatures.READ, VisualFeatures.OBJECTS,VisualFeatures.DENSE_CAPTIONS,VisualFeatures.PEOPLE,VisualFeatures.TAGS,VisualFeatures.SMART_CROPS],
    gender_neutral_caption=True,  # Optional (default is False)
)


print("\nCAPTIONS = ",result.caption)
print("\nDENSE CAPTIONS = ",result.dense_captions)
print("\nOBJECTS = ",result.objects)
print("\nPEOPLE = ",result.people)
print("\nREAD = ",result.read)
print("\nTAGS = ",result.tags)
print("\nSMART CROPS = ",result.smart_crops)
