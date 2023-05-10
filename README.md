# mockupgen
A tool for generating 3D device mockups from a screenshot.

<br>

![](https://www.rohanmenon.com/media/example.png)

# Installation
```
pip install mockupgen
```

Alternatively, from source:
```
git clone https://github.com/rmenon1008/mockupgen.git
cd mockupgen
pip install .
```

# Usage
```
mockupgen [OPTION...] screenshot_file

OPTION:
  -t TEMPLATE                  template name or number
  -o OUTFILE                   output file name (use extension to specify format)
  -w WIDTH                     output width (will upscale if requested)
  --crop                       crop instead of stretching the screenshot to fit the mockup
  --brightness B               screen brightness adjustment (default: 1.0)
  --contrast C                 screen contrast adjustment (default: 1.0)
  --list                       list available templates
  --custom-template-dir DIR    use a custom directory of templates (see README.md)
```

# Templates
A number of templates come preinstalled with the tool. They are all based on mockups created by [Anthony Boyd](https://www.anthonyboyd.graphics/). You can see the available templates with `mockupgen --list`.

## Custom templates
Instead of using the preinstalled templates, you can supply your own by specifying `--custom-template-dir`. The directory should contain an `info.json` file and all the required images. It should look something like this:
```jsonc
// info.json
// Note: All paths are relative to this file

[
    {
        // Required fields
        "name": "Example Template",
        "base_file": "base.png",   // The device template image
        "screen_points": [         // The pixel locations of the 4 corners of the screen
            [896, 224],            // Starts in the top left and goes counter clockwise
            [896, 654],
            [1471, 985],
            [1471, 555]
        ],

        // Only one of the two options below must be specified
        "mask_file": "mask.png",   // An image used to mask the screenshot (alpha channel used)
        // OR
        "mask_aspect_ratio": 1.0,  // Aspect ratio to mask the screenshot (assumes rectangular)

        // Optional fields
        "brightness": 1.0,         // Brightness adjustment of the screenshot
        "contrast": 1.0            // Contrast adjustment of the screenshot
    },
    ...
]
```

# About
Mockups typically require expensive and slow image processing tools to create. While these can create very realistic mockups, they're very manual and usually overkill for the blog post thumbnail I'm trying to create.

The tool uses opencv to mask, warp and composite screenshots onto a template. Right now, it doesn't do any lighting or shadow effects.
