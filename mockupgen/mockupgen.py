import os
import json
import urllib.request

from colorama import init as colorama_init
from colorama import Fore, Style

try:
    from helpers import _r, _b, _g, _c, _m, ColoredArgParser
    from image_processing import generate_mockup, save_image
except ImportError:
    from .helpers import _r, _b, _g, _c, _m, ColoredArgParser
    from .image_processing import generate_mockup, save_image


colorama_init()

DEFAULT_TEMPLATE_DIR = "https://raw.githubusercontent.com/rmenon1008/mockupgen-templates/main"

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
            if m['name'].lower() == mockup.lower() or m['slug'].lower() == mockup.lower():
                return m
    print(_r('Invalid template selection'))
    print()
    return None

def get_template_index(templates_path_or_url):
    if templates_path_or_url.startswith('http'):
        index_url = templates_path_or_url.rstrip('/') + '/index.json'
        try:
            with urllib.request.urlopen(index_url) as f:
                try:
                    template_index = json.load(f)
                except json.JSONDecodeError:
                    print(_r(f'Error parsing template index: {index_url}'))
                    exit(1)
        except urllib.error.HTTPError:
            print(_r(f'Error fetching template index: {index_url}'))
            exit(1)
    else:
        index_path = os.path.join(templates_path_or_url, 'index.json')
        try:
            with open(index_path, 'r') as f:
                try:
                    template_index = json.load(f)
                except json.JSONDecodeError:
                    print(_r(f'Error parsing template index: {index_path}'))
                    exit(1)
        except (NotADirectoryError, FileNotFoundError):
            print(_r(f'Error loading template index: {index_path}'))
            exit(1)
    version = template_index.get('index_version', "unspecified")
    return template_index["templates"], version, templates_path_or_url

def print_template_list(template_list):
    # Group templates by category
    categories = {}
    for template in template_list:
        category = template.get('category', 'Uncategorized')
        if category not in categories:
            categories[category] = []
        categories[category].append(template)
    
    # Print the templates
    i = 1
    for category in categories:
        print(_b(category+":"))
        for template in categories[category]:
            print(f"  {i}. {template['name']}")
            i += 1

def main():
    # Parse the arguments
    parser = ColoredArgParser(description='Mock up a screenshot in a device frame', prog='mockupgen')
    parser.add_argument('screenshot', metavar="SCREENSHOT", nargs='?', type=str, help='screenshot file path')
    parser.add_argument('-t', metavar="TEMPLATE", help='template number, name or slug')
    parser.add_argument('-o', metavar="OUTFILE", type=str, default=None, help='output file name (use extension to specify format)')
    parser.add_argument('-w', metavar="WIDTH", type=int, default=None, help='output width (will attempt to upscale)')
    parser.add_argument('--crop', action='store_true', help='crop instead of stretching the screenshot to fit the template', default=False)
    parser.add_argument('--rotate', metavar="R", type=int, default=0, help='number of times to rotate the screenshot 90 degrees ccw')
    parser.add_argument('--brightness', metavar="B", type=float, default=1.0, help='screen brightness adjustment (default: 1.0)')
    parser.add_argument('--contrast', metavar="C", type=float, default=1.0, help='screen contrast adjustment (default: 1.0)')
    parser.add_argument('--list', action='store_true', help='list available templates', default=False)
    parser.add_argument('--custom-templates', metavar="PATH/URL", type=str, default=None, help='specify a custom directory of templates (see README.md)')
    args = parser.parse_args()

    # Accept a template URL or path
    if args.custom_templates:
        template_list, template_version, template_dir = get_template_index(args.custom_templates)
        print(f'Using custom template directory: {_b(args.custom_templates)} (version {_b(template_version)})')
    else:
        template_list, template_version, template_dir = get_template_index(DEFAULT_TEMPLATE_DIR)
        print(f'Using {_b("mockupgen-templates")} (version {_b(template_version)})')

    # List the templates if requested
    if args.list:
        print_template_list(template_list)
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
    template = get_valid_template(template_list, args.t)
    while not template:
        print_template_list(template_list)
        template = get_valid_template(template_list, input(f'{_m("Select one: ")}'))

    print()
    print(f'Generating mockup for {_b(template["name"])} - {_b(template["slug"])}')

    if 'author' in template:
        print(f'Template created by {_g(template["author"])}')
    if 'backlink' in template:
        print(f'Original template: {_g(template["backlink"])}')
    print()

    # Generate the mockup
    generated_mockup = generate_mockup(template_dir, args.screenshot, template, args.w, args.crop, args.rotate, args.brightness, args.contrast)

    if generated_mockup is None:
        print(_r('Error generating mockup'))
        exit(1)

    save_image(generated_mockup, args.o)


if __name__ == '__main__':
    main()
