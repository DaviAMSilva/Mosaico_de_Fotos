# Mosaico de Fotos
Programa para criar um mosaico de fotos a partir de várias imagens.

```console
usage: PhotoMosaic [-h] [-p PATH] [-n NAME] [-r]
                   [-c {RGB,SIMPLIFIED,CIELAB}]
                   [-s {BICUBIC,NEAREST,BOX,BILINEAR,HAMMING,LANCZOS}]
                   [-f FORMAT [FORMAT ...]]
                   Image Path Tile Size Tile Resolution

Use to create beautiful mosaic with your images

positional arguments:
  Image Path            The path to the image that will be       
                        turned into a mosaic.
  Tile Size             The size of the each tile in the main    
                        image (different from the tile
                        resolution).
  Tile Resolution       The resolution (size) of each tile on    
                        the final mosaic.

options:
  -h, --help            show this help message and exit
  -p PATH, --samplespath PATH
                        The path to the sample images that will  
                        form the final mosaic.
  -n NAME, --name NAME  The name (with extension) of the final   
                        mosaic.
  -r, --recursive       Whether or not to recursively search     
                        images in the sample images folder       
  -c {RGB,SIMPLIFIED,CIELAB}, --colormode {RGB,SIMPLIFIED,CIELAB}
                        Specifies one from the different ways    
                        to compare the distance between colors.  
  -s {BICUBIC,NEAREST,BOX,BILINEAR,HAMMING,LANCZOS}, --resizemode {BICUBIC,NEAREST,BOX,BILINEAR,HAMMING,LANCZOS}
                        Specifies the resampling filter for      
                        resizing images.
  -f FORMAT [FORMAT ...], --formats FORMAT [FORMAT ...]
                        Aditional file formats to be accepted    
                        (dot required).
```
