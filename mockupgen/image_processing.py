import os

import cv2
import numpy as np
from colorama import Fore, Style

try:
    from helpers import _r, _b, _g, _c, _m
except ImportError:
    from .helpers import _r, _b, _g, _c, _m

def _center_crop(image, aspect_ratio):
    image_aspect_ratio = image.shape[1] / image.shape[0]
    center = (image.shape[1] / 2, image.shape[0] / 2)

    if aspect_ratio > image_aspect_ratio:
        crop_width = image.shape[1]
        crop_height = crop_width / aspect_ratio
    else:
        crop_height = image.shape[0]
        crop_width = crop_height * aspect_ratio

    image = image[
        int(center[1] - crop_height / 2):int(center[1] + crop_height / 2),
        int(center[0] - crop_width / 2):int(center[0] + crop_width / 2)
    ]

    return image


def _brightness(image, amount):
    a = image[:,:,3]
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    v = np.clip(v * amount, 0, 255).astype(np.uint8)
    final_hsv = cv2.merge((h, s, v))
    image = cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)
    image[:,:,3] = a
    return image

def _contrast(image, amount):
    a = image[:,:,3]
    amount = amount * 127 - 127
    f = 131*(amount + 127)/(127*(131-amount))
    image = cv2.addWeighted(image, f, image, 0, 127*(1-f))
    image[:,:,3] = a
    return image



def _over_composite(background, foreground):
    # Split out the alpha channel
    alpha_foreground = foreground[:,:,3] / 255.0

    # Set adjusted colors
    for color in range(0, 3):
        background[:,:,color] = alpha_foreground * foreground[:,:,color] + background[:,:,color] * (1 - alpha_foreground)
    return background


def _warn_for_different_aspect_ratios(ar1, ar2):
    if ar1 / ar2 > 1.1 or ar2 / ar1 > 1.1:
        print(_r(f'Warning: The screenshot was stretched significantly to fit the template. Use --crop to crop the screenshot instead.'))


def _mask_image(image, mask):
    # Set the alpha channel of the image to the alpha channel of the mask
    image[:,:,3] = mask[:,:,3]
    return image


def save_image(image, output_file):
    # Get extension if specified
    extension = None
    if output_file:
        extension = os.path.splitext(output_file)[1]
        if extension:
            extension = extension[1:]

    # Save the mockup
    if output_file:
        if extension:
            try: 
                cv2.imwrite(output_file, image, [int(cv2.IMWRITE_JPEG_QUALITY), 100])
                print(f'Saved mockup as {Fore.GREEN}{output_file}{Style.RESET_ALL}')
            except:
                print(_r(f'Invalid output file extension "{extension}"'))
                exit(1)
        else:
            cv2.imwrite(output_file + '.png', image)
            print(f'Saved mockup as {Fore.GREEN}{output_file + ".png"}{Style.RESET_ALL}')
    else:
        cv2.imwrite('mockup.png', image)
        print(f'Saved mockup as {Fore.GREEN}mockup.png{Style.RESET_ALL}')

def generate_mockup(mockup_dir, screenshot_file, mockup, output_width, crop, brightness, contrast):
    ### STEP 1: Load the screenshot and the mockup

    # Load the screenshot and the mockup
    screenshot = cv2.imread(screenshot_file, cv2.IMREAD_UNCHANGED)
    mockup_img_file = os.path.join(mockup_dir, mockup['base_file'])
    mockup_img = cv2.imread(mockup_img_file, cv2.IMREAD_UNCHANGED)

    # Ensure the screenshot and mockup are valid
    if screenshot is None:
        print(_r(f'Screenshot "{screenshot_file}" not found or invalid.'))
        return None
    if mockup_img is None:
        print(_r(f'Mockup base image "{mockup_img_file}" specified, but invalid. This is an issue with the mockup configuration.'))
        return None
    
    if screenshot.dtype == np.uint16:
        screenshot = (screenshot / 256).astype(np.uint8)
    if mockup_img.dtype == np.uint16:
        mockup_img = (mockup_img / 256).astype(np.uint8)

    if screenshot.shape[2] == 3:
        screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2BGRA)
    if mockup_img.shape[2] == 3:
        mockup_img = cv2.cvtColor(mockup_img, cv2.COLOR_BGR2BGRA)

    if screenshot.dtype != np.uint8:
        print(_r(f"Couldn't convert screenshot to uint8"))
        return None
    if mockup_img.dtype != np.uint8:
        print(_r(f"Couldn't convert mockup base image to uint8"))
        return None



    ### STEP 2: Upscale and adjust the files as needed

    # Upscale the mockup image if it's under the desired output width
    mockup_upscale_factor = 1
    if output_width and mockup_img.shape[0] < output_width:
        mockup_upscale_factor = output_width / mockup_img.shape[0]
        mockup_img = cv2.resize(mockup_img, (0, 0), fx=mockup_upscale_factor, fy=mockup_upscale_factor, interpolation=cv2.INTER_CUBIC)

    # Always upscale by 4 to improve the quality after the perspective warp 
    mockup_img = cv2.resize(mockup_img, (0, 0), fx=4, fy=4, interpolation=cv2.INTER_CUBIC)
    mockup_upscale_factor *= 4

    # Adjust the screenshot based on the mockup options
    if "contrast" in mockup:
        screenshot = _contrast(screenshot, mockup['contrast'])
    if "brightness" in mockup:
        screenshot = _brightness(screenshot, mockup['brightness'])
    
    # Now adjust the screenshot based on the CLI options
    if contrast:
        screenshot = _contrast(screenshot, contrast)
    if brightness:
        screenshot = _brightness(screenshot, brightness)



    ### STEP 3: Mask the screenshot

    if "mask_file" in mockup:
        # Load the mask
        mockup_mask = cv2.imread(os.path.join(mockup_dir, mockup['mask_file']), cv2.IMREAD_UNCHANGED)

        # Ensure the mask is valid
        if mockup_mask is None:
            print(_r(f'Template mask image "{mockup_dir + mockup["mask_file"]}" specified, but invalid. This is an issue with the template configuration.'))
            return None

        # Center crop the image to match the aspect ratio of the mask
        if crop:
            screenshot = _center_crop(screenshot, (mockup_mask.shape[1] / mockup_mask.shape[0]))

        # Warn the user if the image is being stretched a lot
        _warn_for_different_aspect_ratios((screenshot.shape[1] / screenshot.shape[0]), (mockup_mask.shape[1] / mockup_mask.shape[0]))

        # Scale the mask to the size of the screenshot
        mockup_mask = cv2.resize(mockup_mask, (screenshot.shape[1], screenshot.shape[0]))

        # Apply the mask to the screenshot, but preserve transparency
        masked_screenshot = _mask_image(screenshot, mockup_mask)

    elif "mask_aspect_ratio" in mockup:
        # Center crop the image to match the aspect ratio of the mask
        if crop:
            screenshot = _center_crop(screenshot, mockup['mask_aspect_ratio'])

        # Warn the user if the image is being stretched a lot
        _warn_for_different_aspect_ratios((screenshot.shape[1] / screenshot.shape[0]), mockup['mask_aspect_ratio'])
        
        masked_screenshot = screenshot
    else:
        print(_r('No mask or mask aspect ratio specified in template. This is an issue with the template configuration.'))
        return None



    ### STEP 4: Warp the screenshot

    # Warp the screenshot to the mockup perspective
    mockup_points = np.array(mockup['screen_points'], dtype=np.float32) * mockup_upscale_factor

    screenshot_points = np.array([
        [0, 0],
        [0, masked_screenshot.shape[0]],
        [masked_screenshot.shape[1], masked_screenshot.shape[0]],
        [masked_screenshot.shape[1], 0]
    ], dtype=np.float32)

    matrix = cv2.getPerspectiveTransform(screenshot_points, mockup_points)

    warped_screenshot = cv2.warpPerspective(
        masked_screenshot,
        matrix,
        (mockup_img.shape[1], mockup_img.shape[0]),
        borderMode=cv2.BORDER_TRANSPARENT
    )
    
    # Blur the screenshot slightly
    warped_screenshot = cv2.blur(warped_screenshot, (2, 2))



    ### STEP 5: Composite the screenshot onto the mockup and resize
    
    # Composite
    mockup_img = _over_composite(mockup_img, warped_screenshot)

    # Scale back down by 4
    mockup_img = cv2.resize(mockup_img, (0, 0), fx=0.25, fy=0.25, interpolation=cv2.INTER_AREA)

    # Resize to the specified output width
    if output_width:
        mockup_img = cv2.resize(mockup_img, (output_width, int(mockup_img.shape[0] * (output_width / mockup_img.shape[1]))), interpolation=cv2.INTER_AREA)
    
    return mockup_img
