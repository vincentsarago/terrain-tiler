"""Terrain App"""

from io import BytesIO

import numpy
from rio_tiler import main
from rio_rgbify import encoders
from rio_tiler.utils import (
    array_to_img,
    linear_rescale,
    get_colormap,
    mapzen_elevation_rgb
)
from rio_tiler import profiles as TileProfiles

from lambda_proxy.proxy import API


APP = API(app_name="terrain-tiler")
TERRAIN_BUCKET = 's3://elevation-tiles-prod'


def img_to_buffer(img, tileformat):
    """Convert a Pillow image to an base64 encoded string.

    Attributes
    ----------
    img : object
        Pillow image
    tileformat : str
        Image format to return (Accepted: "jpg" or "png")

    Returns
    -------
    buffer

    """
    params = TileProfiles.get(tileformat)

    if tileformat == 'jpeg':
        img = img.convert('RGB')

    sio = BytesIO()
    img.save(sio, tileformat.upper(), **params)
    sio.seek(0)
    return sio.getvalue()


@APP.route(
    "/tiles/<int:z>/<int:x>/<int:y>.<ext>",
    methods=["GET"],
    cors=True,
    payload_compression_method="gzip",
    binary_b64encode=True,
)
def tile(
    tile_z,
    tile_x,
    tile_y,
    tileformat,
    indexes=1,
    shadder=None,
    colormap=None,
    range=None,
):
    """Handle tile requests"""
    if tileformat == "jpg":
        tileformat = "jpeg"

    if colormap and shadder:
        return ("NOK", "text/plain", "Cannot pass shadder and colormap options")

    address = f"s3://elevation-tiles-prod/geotiff/{tile_z}/{tile_x}/{tile_y}.tif"
    data, mask = main.tile(
        address, tile_x, tile_y, tile_z, indexes=indexes, tilesize=512
    )
    if shadder:
        tileformat = "png"
        if shadder == "mapbox":
            tile = encoders.data_to_rgb(data[0], -10000, 1)
        elif shadder == "mapzen":
            tile = mapzen_elevation_rgb.data_to_rgb(data)
        else:
            return ("NOK", "text/plain", f"Invalid shadder mode: {shadder}")
    else:
        if not range:
            range = "0,10000"
        histoCut = list(map(int, range.split(',')))

        tile = numpy.where(
            mask, linear_rescale(data, in_range=histoCut, out_range=[0, 255]), 0
        )

    options = dict(mask=mask)
    if colormap:
        options.update(color_map=get_colormap(name=colormap))
    img = array_to_img(tile, **options)

    return (
        "OK",
        f"image/{tileformat}",
        img_to_buffer(img, tileformat)
    )


@APP.route('wmts.xml', methods=['GET'], cors=True)
def wmts():
    """WMTS Service"""
    xml = """<GDAL_WMS>
        <Service name="TMS">
            <ServerUrl>http://elevation-tiles-prod.s3.amazonaws.com/geotiff/${z}/${x}/${y}.tif</ServerUrl>
        </Service>
        <DataWindow>
            <UpperLeftX>-20037508.34</UpperLeftX>
            <UpperLeftY>20037508.34</UpperLeftY>
            <LowerRightX>20037508.34</LowerRightX>
            <LowerRightY>-20037508.34</LowerRightY>
            <TileLevel>14</TileLevel>
            <TileCountX>1</TileCountX>
            <TileCountY>1</TileCountY>
            <YOrigin>top</YOrigin>
        </DataWindow>
        <ImageFormat>image/tif</ImageFormat>
        <DataType>UInt32</DataType>
        <Projection>EPSG:3857</Projection>
        <BlockSizeX>512</BlockSizeX>
        <BlockSizeY>512</BlockSizeY>
        <BandsCount>1</BandsCount>
        <MaxConnections>100</MaxConnections>
        <ZeroBlockOnServerException>true</ZeroBlockOnServerException>
    </GDAL_WMS>"""

    return ('OK', 'plain/text', xml)


@APP.route('/favicon.ico', methods=['GET'], cors=True)
def favicon():
    """favicon."""
    return('NOK', 'text/plain', '')
