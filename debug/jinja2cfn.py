from jinja2 import Template, Environment, FileSystemLoader
import envdata
import sys

args = sys.argv

env = Environment(loader=FileSystemLoader('.'))
template = env.get_template(args[1])

rendered = template.render(envdata.data)

print(str(rendered))
