"""
"""

import numpy as np

import rasterio
from rio_tiler.utils import array_to_img

from lambda_proxy.proxy import API


APP = API(app_name="terrain-tiler")
TERRAIN_BUCKET = 's3://elevation-tiles-prod'


def mapbox_encoded_rgb(value):
    value = np.clip(value + 10000, 0.0, 65535.0)
    r = (value / 256)
    g = (value % 256)
    b = ((value * 256) % 256)
    return np.stack([r, g, b]).astype(np.uint8)


@APP.route('tiles/<int:z>/<int:x>/<int:y>.png', methods=['GET'], cors=True)
def mapbox_tile(tile_z, tile_x, tile_y):
    """
    Handle tile requests
    """
    query_args = APP.current_request.query_params
    query_args = query_args if isinstance(query_args, dict) else {}

    tilesize = query_args.get('tile', 256)
    tilesize = int(tilesize) if isinstance(tilesize, str) else tilesize

    address = f'{TERRAIN_BUCKET}/geotiff/{tile_z}/{tile_x}/{tile_y}.tif'
    with rasterio.open(address) as src:
        arr = src.read(indexes=1,
                       out_shape=(tilesize, tilesize)).astype(src.profile['dtype'])
        rgb = mapbox_encoded_rgb(arr)

    tile = array_to_img(rgb, 'png', nodata=None)

    return ('OK', 'image/png', tile)


@APP.route('wmts.xml', methods=['GET'], cors=True)
def wmts():
    """
    Handle tile requests
    """

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
    """
    favicon
    """
    return('NOK', 'text/plain', '')
