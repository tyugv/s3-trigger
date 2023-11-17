import boto3
from PIL import Image
import io
import urllib.parse


s3 = boto3.client('s3')


def preprocess(event, context):
   # parse event
   bucket = event['Records'][0]['s3']['bucket']['name']
   key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
   
   # download file
   try:
      response = s3.get_object(Bucket=bucket, Key=key)
   except Exception as e:
      raise Exception('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))

   # read as Image
   image = Image.open(response['Body'])

   # cut to square and resize to 512x512
   w, h = image.size
   size = min(w, h)
   dw, dh = (w - size) // 2, (h - size) // 2
   image = image.crop((dw, dh, size + dw, size + dh)).resize((512, 512))

   # to bytes stream
   bytes_stream = io.BytesIO()
   image.save(bytes_stream, format="PNG")
   bytes_stream.seek(0)

   # change folder to "preprocessed_data" and image extension if it is not "png"
   filename = key.replace('raw_data/', 'preprocessed_data/')
   filename = filename.replace(".jpg", ".png").replace(".jpeg", ".png")

   # save the result
   s3.put_object(Bucket=bucket, Key=filename, Body=bytes_stream)
