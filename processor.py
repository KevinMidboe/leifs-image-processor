import glob
import os
from PIL import Image, ExifTags
import concurrent.futures
import argparse
import fileinput
import uuid
import os.path

IMAGE_TYPES = ['.png', '.jpg', '.jpeg', '.JPG', '.PNG']
OUTPUT_EXTENSION = 'jpg'
OUTPUT_FALLBACK = os.path.dirname(__file__)
OUTPUT_SIZES = [
    { 'dimensions': (400, 400), 'name': 'thumb', 'crop': True },
    { 'dimensions': (650, 650), 'name': 'sm', 'crop': False },
    { 'dimensions': (1200, 1200), 'name': 'md', 'crop': False },
    { 'dimensions': (2500, 2500), 'name': 'lg', 'crop': False }]



def processImage(file, outputPath=None):
    if outputPath == None:
      outputPath = args.output if 'args.output' in globals() else os.path.join(OUTPUT_FALLBACK, 'output')
    else:
      outputPath = os.path.join(OUTPUT_FALLBACK, outputPath)

    print('outputpath', outputPath)
    image = Image.open(file)
    image = rotateFromExifMetadata(image)
    fileID = uuid.uuid4().hex

    for size in OUTPUT_SIZES:
        temp = image.copy()
        
        if size['crop']:
            temp = temp.crop(squareDimensions(temp.size))

        temp.thumbnail(size['dimensions'], Image.LANCZOS)
        
        filename = generateFilename(fileID, size['name'], outputPath)
        temp.save(filename)
    
    return {
      'filename': '.'.join([fileID, OUTPUT_EXTENSION]),
      'folder': outputPath,
      'variations': list(map(lambda vairation: vairation['name'], OUTPUT_SIZES))
    }

def rotateFromExifMetadata(image):
  """ This function autorotates a picture """
  try:
    exif = image._getexif()
  except AttributeError as e:
    print("Could not get exif - Bad image!")
    return image

  (width, height) = image.size
  if not exif:
    if width > height:
      return image.rotate(90)
  else:
    orientation_key = 274 # cf ExifTags
    if orientation_key in exif:
      orientation = exif[orientation_key]
      rotate_values = {
        3: 180,
        6: 270,
        8: 90
      }
      
      if orientation in rotate_values:
        # Rotate and return the picture
        return image.rotate(rotate_values[orientation])

  return image

def generateFilename(fileID, modifier, outputPath):
    filename = "{}_{}.{}".format(fileID, modifier, OUTPUT_EXTENSION)
    return os.path.join(outputPath, filename)

def squareDimensions(dimensions):
    (width, height) = dimensions

    if width > height:
       delta = width - height
       left = int(delta/2)
       upper = 0
       right = height + left
       lower = height
    else:
       delta = height - width
       left = 0
       upper = int(delta/2)
       right = width
       lower = width + upper

    return (left, upper, right, lower)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process some images')
    parser.add_argument('files', metavar="files", type=str, help='Directory of images to process')
    parser.add_argument('--output', metavar="DIR", help="Output directory")

    class Args:
        pass

    args = Args()
    args = parser.parse_args()

    # Create a pool of processes. By default, one is created for each CPU in your machine.
    with concurrent.futures.ProcessPoolExecutor() as executor:
        # Get a list of files to process
        image_files = glob.glob('{}/*'.format(args.files))

        print('Processing and generating images in following sizes: {}'.format(OUTPUT_SIZES))
        # Process the list of files, but split the work across the process pool to use all CPUs!
        for image_file, output_file in zip(image_files, executor.map(processImage, image_files)):
            print(f"Processed image {image_file} and save as {output_file}")
