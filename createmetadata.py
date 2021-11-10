from ome_types.model import OME, Image, Pixels

ome = OME()
img = Image(
    pixels=Pixels(
        size_c=2, size_t=1, size_x=512, size_y=512, size_z=15,
        type='uint16', dimension_order='XYZCT',
        metadata_only=True
    )
)
ome.images.append(img)

print(ome.to_xml())




import datetime
def xsd_now():
    '''Return the current time in xsd:dateTime format'''
    return datetime.datetime.now().isoformat()

DEFAULT_NOW = xsd_now()
NS_BINARY_FILE = "http://www.openmicroscopy.org/Schemas/BinaryFile/2013-06"
NS_ORIGINAL_METADATA = "openmicroscopy.org/OriginalMetadata"
NS_DEFAULT = "http://www.openmicroscopy.org/Schemas/{ns_key}/2013-06"
NS_RE = r"http://www.openmicroscopy.org/Schemas/(?P<ns_key>.*)/[0-9/-]"

default_xml = """<?xml version="1.0" encoding="UTF-8"?>
<!-- Warning: this comment is an OME-XML metadata block, which contains
crucial dimensional parameters and other important metadata. Please edit
cautiously (if at all), and back up the original data before doing so.
For more information, see the OME-TIFF documentation:
https://docs.openmicroscopy.org/latest/ome-model/ome-tiff/ -->
<OME xmlns="http://www.openmicroscopy.org/Schemas/OME/2016-06"
     xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
     xsi:schemaLocation="http://www.openmicroscopy.org/Schemas/OME/2016-06 http://www.openmicroscopy.org/Schemas/OME/2016-06/ome.xsd">
    <Image ID="Image:0" Name="default.png">
        <AcquisitionDate>{timestamp}</AcquisitionDate>
        <Pixels
                DimensionOrder="XYCZT"
                ID="Pixels:0"
                Interleaved="false"
                SizeC="1"
                SizeT="1"
                SizeX="512"
                SizeY="512"
                SizeZ="1"
                Type="uint8">
            <Channel ID="Channel:0:0" SamplesPerPixel="1">
            </Channel>
            <BinData
         BigEndian="false"
         Compression="zlib"
         Length="12"
         >ZGVmYXVsdA==</BinData>
        </Pixels>
    </Image>
</OME>""".format(ns_ome_default=NS_DEFAULT.format(ns_key='ome'), timestamp=xsd_now())

ome_types.from_xml(default_xml)
