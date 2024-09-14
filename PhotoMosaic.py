"""Module to make photo mosaics - By: DaviAMSilva"""

import argparse
import PIL.Image
from glob import glob
from tqdm import tqdm
from math import floor, ceil, sqrt

# These are optional, but if they're not present you can't use CIELAB as the color mode
try:
    from colormath.color_objects import LabColor, sRGBColor
    from colormath.color_conversions import convert_color
    from colormath.color_diff import delta_e_cie2000
except ModuleNotFoundError:
    pass










def create_mosaic(
    main_image_path:str,
    size:int,
    resolution:int,
    samples_path:str = ".\\",
    name:str = "Mosaic.jpg",
    recursive:bool = False,
    color_mode:str = "SIMPLIFIED",
    resize_mode:str = "BICUBIC",
    formats:list = []
) -> bool:
    """
    ### Creates a images mosaic combining many sample images to \
    create a bigger image that resembles the original main image
    
    #### Arguments:
    - main_image_path {str} -- Path to the main image, source to the mosaic image
    - size {int} -- Size of each tile in the main image (different from tile resolution)
    - resolution {int} -- Resolution (size) of each tile in the final image
    
    #### Keyword Arguments:
    - samples_path {str} -- The path to the samples images (default: {".\"})
    - recursive {bool} -- Whether or not to recursively search all the files in the sample images folder (default: {False})
    - color_mode {str} -- Specifies how to calculate the distance between two colors (default: {"SIMPLIFIED"})
    - resize_mode {str} -- Specifies a resampling filter for resizing images (default: {"BICUBIC"})
    - formats {list} -- Aditional file formats to be accepted (dot required) (default: [])
    
    #### Returns:
    {bool} -- Whether or not the function exited successfully
    """

    # Loading main image
    try:
        main_image:PIL.Image.Image = PIL.Image.open(main_image_path)
    except FileNotFoundError:
        print(f"The main image could not be found. Please try again. (Input: {main_image_path})")
        return False

    main_image_info = ImageInfo(main_image_path, main_image, average_color(main_image, resize_mode))

    # Valid extensions
    valid_extensions = [".jpg", ".jpeg", ".png"]
    valid_extensions.extend(formats)
    valid_extensions = tuple(valid_extensions)

    # The list with all image names
    path_name_list = []

    # Adding the images
    for ext in valid_extensions:
        if recursive:
            path_name_list.extend(glob(f"{samples_path}/**/*{ext}", recursive=True))
        else:
            path_name_list.extend(glob(f"{samples_path}/*{ext}", recursive=False))

    # Removing all non valid image
    path_name_list = list(filter(
        lambda x: 
            x.endswith(valid_extensions),
    path_name_list))

    # Stores the information of all the sample images
    sample_image_info = []

    # Creating progress bar
    pbar = tqdm(path_name_list, "Loading sample images", unit=" images", leave=False)

    # Looping through all the images
    for path_name in pbar:

        # Updating current image
        pbar.set_postfix({"Current": path_name[-25:]}, True)

        # Opening the files
        with PIL.Image.open(path_name) as image:
            image = image.convert("RGBA")

            # Getting info
            sq_image = square_crop(image, resolution, resize_mode)
            av_color = average_color(image, resize_mode)

            # Saving info
            sample_image_info.append(ImageInfo(path_name,sq_image,av_color))

    # Creating the mosaic
    mosaic_image = create_mosaic_image(main_image, sample_image_info, size, resolution, color_mode, resize_mode)

    # Checking if the mosaic is valid
    if mosaic_image == None:
        return False

    # Creating progress bar
    pbar = tqdm(desc="Saving the mosaic... (This might take a while)", bar_format="{desc}", leave=False)

    # Saving the image
    mosaic_image.save(name)

    # Closing the progress bar
    pbar.close()

    # Success
    return True










def create_mosaic_image(
        main_image:PIL.Image.Image,
        sample_images_info,
        size:int,
        resolution:int,
        color_mode:str = "SIMPLIFIED",
        resize_mode:str = "BICUBIC"
) -> PIL.Image.Image:
    """
    ### Function to actually create the mosaic image
    
    #### Arguments:
    - main_image {PIL.Image.Image} -- Main image object
    - sample_images_info {list} -- Info of all the sample images
    - size {int} -- Size of each tile in the main image (different from tile resolution)
    - resolution {int} -- Resolution (size) of each tile in the final image
    - color_mode {str} -- Specifies how to calculate the distance between two colors (default: {"SIMPLIFIED"})
    - resize_mode {str} -- Specifies a resampling filter for resizing images (default: {"BICUBIC"})
    
    #### Returns:
    PIL.Image.Image -- Pillow image object
    """

    # Initializing some variables
    width, height = main_image.size
    xoff, yoff = width % size / 2, height % size / 2
    xnum, ynum = width // size, height // size

    pb = tqdm(desc="Creating a blank image... (This might take a while)", bar_format="{desc}", leave=False)
    
    # Creating a blank image
    mosaic_image = PIL.Image.new("RGB", (resolution*xnum, resolution*ynum), 255)

    pb.close()

    pbar = tqdm(desc="Drawing all the tiles", total=xnum*ynum, unit=" tiles", leave=False, smoothing=0.1)

    # Looping through all the tiles
    for i, x in enumerate(range(ceil(xoff), floor(width - xoff), size)):
        for j, y in enumerate(range(ceil(yoff), floor(height - yoff), size)):

            # Getting the average color of the current tile
            av_color = average_color(main_image.crop((x, y, x + size, y + size)), resize_mode)

            # Initializing some variables
            lowest_value = 1_000_000_000
            best_image:PIL.Image.Image = PIL.Image.new("RGB", (resolution, resolution), 255)

            # Going through all the info from the sample images
            for sample_img in sample_images_info:

                # Determining which color distance estimatorr to use
                if color_mode == "CIELAB":
                    try:

                        # * CIELAB: More realistic, but slower *
                        r,g,b,*_ = av_color
                        av_color_lab = convert_color(sRGBColor(r, g, b, True), LabColor)
                        sample_lab = convert_color(sRGBColor(*[*sample_img.color][0:3], True), LabColor)
                        result = delta_e_cie2000(sample_lab, av_color_lab)

                    except NameError:

                        pbar.leave = True
                        pbar.close()
                        print(f"\nNameError detected. Please verify that you have "+
                        "'colormath' installed to use the color mode 'CIELAB'.")
                        return

                else:

                    # Initializing some variables
                    r,g,b,_ = sample_img.color
                    ar,ag,ab,*_ = av_color

                    if color_mode == "RGB":

                        # * Cartesian RGB: Not realistic, but faster *
                        result = sqrt(pow(r-ar,2) + pow(g-ag,2) + pow(b-ab,2))

                    else:

                            # * Simplified formula: Intermidiare realism and speed. *
                            # * Source: https://www.compuphase.com/cmetric.htm *
                            rmean = (r + ar) // 2;
                            dr,dg,db = int(r - ar), int(g - ag), int(b - ab)
                            result = sqrt((((512+rmean)*dr*dr)>>8) + 4*dg*dg + (((767-rmean)*db*db)>>8))

                # Storing the image with the most similar colors to the current tile
                if result < lowest_value:
                    lowest_value = result
                    best_image = sample_img.image

            # Drawing the best image found in the current tile
            mosaic_image.paste(best_image, (
                i * resolution,
                j * resolution,
                (i + 1) * resolution,
                (j + 1) * resolution
            ))

            # Updating progress bar
            pbar.update(1)
            # TODO # Fix jittering by formating numbers
            pbar.set_postfix({"Current": (i + 1, j + 1), "Grid": (xnum, ynum)}, True)

    # Closing the progress bar
    pbar.close()

    # Returning the image
    return mosaic_image










class ImageInfo:
    """Stores the information of each image"""


    def __init__(self, path:str, image:PIL.Image.Image, color:tuple):

        self.image:PIL.Image.Image = image
        self.color:tuple = color
        self.path:str = path

    def __repr__(self) -> str:

        return f"Path: {self.path}\nImage: {self.image}\nColor: {self.color}"










def square_crop(img:PIL.Image.Image, resolution:int, resize_mode:str="BICUBIC") -> PIL.Image.Image:
    """
    ### Crops a image with the biggest square possible
    
    #### Arguments:
    - img {PIL.Image.Image} -- Pillow image object
    - resolution {int} -- The height/width of the return square image
    - resize_mode {str} -- Specifies a resampling filter for resizing images (default: {"BICUBIC"})
    
    #### Returns:
    {PIL.Image.Image} -- Pillow image object
    """

    # Dimensions
    w, h = img.size

    # Selecting the right crop box
    if w == h:
        box = (0, 0, w, h)
    elif w > h:
        box = ((w-h) // 2, 0, (w + h) // 2, h)
    else:
        box = (0, (h-w) // 2, w, (h + w) // 2)

    # Returning the cropped image
    return img.resize((resolution, resolution), getattr(PIL.Image, resize_mode), box)










def average_color(img:PIL.Image.Image, resize_mode:str="BICUBIC") -> tuple:
    """
    ### Gets the average color of a image
    
    #### Arguments:
    - img {Image.Image} -- Pillow image object
    - resize_mode {str} -- Specifies a resampling filter for resizing images (default: {"BICUBIC"})
    
    #### Returns:
    {tuple} -- 3-Tuple with the RGB color
    """

    # Returning the color
    return img.resize((1, 1), getattr(PIL.Image, resize_mode)).getpixel((0, 0))











# ---------- ========== Main Script ========== ---------- #

if __name__ == "__main__":

    # Starting
    print("Starting...\n")

    # Getting the parser
    parser = argparse.ArgumentParser("PhotoMosaic", description="Use to create beautiful mosaic with your images")

    # Adding the arguments
    parser.add_argument("main_path", metavar="Image Path", type=str,
        help="The path to the image that will be turned into a mosaic."
    )
    parser.add_argument("size", metavar="Tile Size", type=int,
        help="The size of the each tile in the main image (different from the tile resolution)."
    )
    parser.add_argument("resolution", metavar="Tile Resolution", type=int,
        help="The resolution (size) of each tile on the final mosaic."
    )
    parser.add_argument("-p", "--samplespath", metavar="PATH", type=str, default=".\\",
        help="The path to the sample images that will form the final mosaic."
    )
    parser.add_argument("-n", "--name", type=str, default="Mosaic.jpg",
        help="The name (with extension) of the final mosaic."
    )
    parser.add_argument("-r", "--recursive", action="store_true", default=False,
        help="Whether or not to recursively search images in the sample images folder"
    )
    parser.add_argument("-c", "--colormode", type=str, default="SIMPLIFIED",
        choices=["RGB", "SIMPLIFIED", "CIELAB"],
        help="Specifies one from the different ways to compare the distance between colors."
    )
    parser.add_argument("-s", "--resizemode", type=str, default="BICUBIC",
        choices=[ "BICUBIC", "NEAREST", "BOX", "BILINEAR", "HAMMING", "LANCZOS"], 
        help="Specifies the resampling filter for resizing images."
    )
    parser.add_argument("-f", "--formats", metavar="FORMAT", type=str, nargs="+", default=[],
        help="Aditional file formats to be accepted (dot required)."
    )

    # Getting the arguments
    args = parser.parse_args()

    # Executing the main function
    success = create_mosaic(args.main_path, args.size, args.resolution, args.samplespath,
    args.name, args.recursive, args.colormode, args.resizemode, args.formats)

    # Ending
    if success:
        input("\nThe program exited successfully. Press ENTER to close.\n")
    else:
        input("\nThe program didn't exit successfully. Press ENTER to close.\n")
