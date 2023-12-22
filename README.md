# COG tools
Provide a docker image to execute operations on TIFF files to create COG


## Features
- Transform a grayscale single band tiff into a COG
- Apply a colormap
- Normalization of the values

## Instructions
First build the image
```
docker compose --profile prod build
```
Move files you want to work with to `data` folder
```
docker compose --profile prod run cli grayscale data/raster.tiff --colormap Greens
```


## Why a docker image?
Installing and building GDAL is complex, so let's use a reproducible and isolated environment 
