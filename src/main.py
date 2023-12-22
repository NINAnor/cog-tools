import rasterio
import numpy as np
from osgeo import gdal
from matplotlib import pyplot as plt
import pathlib
import click


@click.group()
def cli():
    pass

@cli.command()
@click.option('--colormap', default='viridis', help="Matplotlib colormap to apply")
@click.argument('source')
def grayscale(source, colormap='viridis'):
    source_path = pathlib.Path(source)
    rgba_path = source_path.parent / (source_path.stem + '.tiff.rgba')
    cog_path = source_path.parent / (source_path.stem + '.tiff.cog')

    src = rasterio.open(source)

    if src.profile.get('count') > 1:
        raise Exception('Only grayscale single band raster are supported')

    # extract only the first band, mask nodata values
    band = src.read(1, masked=True)
    cmap = plt.get_cmap(colormap)

    # Normalize grayscale values between 0 and 1
    normalized_data = (band - band.min()) / (band.max() - band.min())

    # Apply the colormap to get RGBA values
    rgba_data = (cmap(normalized_data) * 255).astype(np.uint8)

    # Create a new profile
    profile = src.profile.copy()
    profile.update(dtype=rasterio.uint8, count=4, nodata=None, photometric='RGBA')

    with rasterio.open(str(rgba_path), 'w+', **profile) as dst:
        # the shape of the raster cannot be saved (x, y, bands)
        # so it's necessary to "roll" the axis (bands, x, y)
        dst.write(np.rollaxis(rgba_data, 2))

    src_ds = gdal.Open(str(rgba_path))

    # Create GDAL options for the COG transformation
    options = [
        'COMPRESS=DEFLATE',
        'TILING_SCHEME=GoogleMapsCompatible',
        'ADD_ALPHA=NO',
    ]

    # Translate and create the COG
    gdal.Translate(str(cog_path), src_ds, format='COG', creationOptions=options)


if __name__ == '__main__':
    cli()
