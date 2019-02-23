import glob
import os
from PIL import Image
import concurrent.futures
import argparse
import fileinput
import uuid
import os.path

IMAGE_TYPES = ['.png', '.jpg', '.jpeg', '.JPG', '.PNG']
OUTPUT_EXTENSION = 'jpg'
OUTPUT_FALLBACK = os.path.dirname(__file__)
OUTPUT_SIZES = [
    { 'dimensions': (250, 250), 'name': 'thumb', 'crop': True },
    { 'dimensions': (650, 650), 'name': 'sm', 'crop': False },
    { 'dimensions': (1200, 1200), 'name': 'md', 'crop': False },
    { 'dimensions': (1800, 1800), 'name': 'lg', 'crop': False }]



def processImage(file, outputPath=None):
    outputPath = args.output if 'args.output' in globals() else os.path.join(OUTPUT_FALLBACK, 'output')
    print('outputpath', outputPath)
    image = Image.open(file)
    fileID = uuid.uuid4().hex

    for size in OUTPUT_SIZES:
        temp = image.copy()
        
        if size['crop']:
            temp = temp.crop(squareDimensions(temp.size))

        temp.thumbnail(size['dimensions'], Image.LANCZOS)
        
        filename = generateFilename(fileID, size['name'], outputPath)
        temp.save(filename)
    
    return '.'.join([fileID, OUTPUT_EXTENSION])

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
