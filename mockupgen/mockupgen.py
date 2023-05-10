import os
import json

from colorama import init as colorama_init
from colorama import Fore, Style

try:
    from helpers import _r, _b, _g, _c, _m, ColoredArgParser
    from image_processing import generate_mockup, save_image
except ImportError:
    from .helpers import _r, _b, _g, _c, _m, ColoredArgParser
    from .image_processing import generate_mockup, save_image


colorama_init()

DEFAULT_TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'templates')

def get_valid_template(mockups, mockup):
    if not mockup:
        return None
    if mockup.isnumeric():
        mockup = int(mockup)
        if mockup > 0 and mockup <= len(mockups):
            selected = mockups[mockup - 1]
            return selected
    else:
        for m in mockups:
            if m['name'].lower() == mockup.lower():
                return m
    print(_r('Invalid template selection'))
    print()
    return None


def main():
    # Parse the arguments
    parser = ColoredArgParser(description='Mock up a screenshot in a device frame', prog='mockupgen')
    parser.add_argument('screenshot', metavar="SCREENSHOT", type=str, help='screenshot file path')
    parser.add_argument('-t', metavar="TEMPLATE", help='template name or number')
    parser.add_argument('-o', metavar="OUTFILE", type=str, default=None, help='output file name (use extension to specify format)')
    parser.add_argument('-w', metavar="WIDTH", type=int, default=None, help='output width (will attempt to upscale)')
    parser.add_argument('--crop', action='store_true', help='crop instead of stretching the screenshot to fit the template', default=False)
    parser.add_argument('--brightness', metavar="B", type=float, default=1.0, help='screen brightness adjustment (default: 1.0)')
    parser.add_argument('--contrast', metavar="C", type=float, default=1.0, help='screen contrast adjustment (default: 1.0)')
    parser.add_argument('--list', action='store_true', help='list available templates', default=False)
    parser.add_argument('--custom-template-dir', metavar="DIR", type=str, default=None, help='use a custom directory of templates (see README.md)')
    # parser.add_argument('--reset-templates', action='store_true', help='clear the templates directory to rerun setup', default=False)
    args = parser.parse_args()

    # Generate the mockup list from the mockups folder
    if args.custom_template_dir:
        norm_path = os.path.normpath(args.custom_template_dir)
        if not os.path.isdir(norm_path):
            print(_r('Custom template directory not found'))
            exit(1)
        print(_b(f'Using custom template directory: {norm_path}'))
        print()
        template_dir = norm_path
    else:
        template_dir = DEFAULT_TEMPLATE_DIR

    # Load the mockup info
    try:
        with open(os.path.join(template_dir, 'info.json')) as info_file:
            template_info = json.load(info_file)
    except FileNotFoundError:
        print(_r('Template directory missing "info.json"'))
        exit(1)

    # List the templates if requested
    if args.list:
        print('Available templates:')
        for i, m in enumerate(template_info):
            print(f' {_b(i+1)}. {m["name"]}')
        exit(0)

    # Ensure the screenshot exists
    if not args.screenshot:
        print(_r('Screenshot not specified'))
        print()
        parser.print_help()
        exit(1)
    if not os.path.isfile(args.screenshot):
        print(_r('Screenshot not found'))
        exit(1)
    
    # List the templates
    template = get_valid_template(template_info, args.t)
    while not template:
        print('Available templates:')
        for i, m in enumerate(template_info):
            print(f' {_b(i+1)}. {m["name"]}')
        template = get_valid_template(template_info, input(f'{_m("Select one: ")}'))

    print()
    print(f'Generating mockup for {_b(template["name"])}')

    if 'author' in template:
        print(f'Template created by {_g(template["author"])}')
    if 'backlink' in template:
        print(f'Original template: {_g(template["backlink"])}')
    print()

    # Generate the mockup
    generated_mockup = generate_mockup(template_dir, args.screenshot, template, args.w, args.crop, args.brightness, args.contrast)

    if generated_mockup is None:
        print(_r('Error generating mockup'))
        exit(1)

    save_image(generated_mockup, args.o)


if __name__ == '__main__':
    main()