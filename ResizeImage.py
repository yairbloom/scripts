from PIL import Image

img = Image.open('/mnt/sw-win10/XJet_3.5.0/BuildEngine/Export/PrintJob_2018-09-25_09-02-25_CustomerParts (009)/Model/SliceModel-00000.png') # image extension *.png,*.jpg
new_width  = 400
new_height = 600
img = img.resize((new_width, new_height), Image.ANTIALIAS)
img.save('/tmp/output image name.png') 
