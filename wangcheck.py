from jsonschema import validate, Draft4Validator, ValidationError
from json import load, JSONDecodeError
from os import path
import sys

class Wangcheck(object):
  def __init__(self, config_dir, options_fn, schema_dir):
    self.config_dir = config_dir
    self.options_fn = options_fn
    self.schema_dir = schema_dir
  def config_file_path(self, filename):
    return path.join(self.config_dir, filename)
  def schema_file_path(self, filename):
    return path.join(self.schema_dir, filename)
  def loadf(self, fn):
    with open(fn) as f:
      return load(f)
  def load_schemas(self):
    self.schema_options = self.loadf(self.schema_file_path('options_schema.json'))
    self.schema_module_group = self.loadf(self.schema_file_path('module_group_schema.json'))
  def load_options(self):
    self.options = self.loadf(self.config_file_path(self.options_fn))
  def load_module_groups(self):
    self.combiner_module_group = self.loadf(self.config_file_path(self.options['CombinerModuleGroup']))
    self.source_modules = {}
    if 'DefaultModuleGroup' in self.options:
      mg_default = self.options['DefaultModuleGroup']
      self.source_modules[mg_default] = self.loadf(self.config_file_path(mg_default))
    for mg_type in [
      'TopBorderModuleGroups',
      'LeftBorderModuleGroups',
      'CentralBorderModuleGroups']:
      if mg_type not in self.options:
        continue
      for mg in self.options[mg_type]:
        mg_fn = mg['Filename']
        if mg_fn not in self.source_modules:
          try:
            self.source_modules[mg_fn] = self.loadf(self.config_file_path(mg_fn))
          except JSONDecodeError:
            print("Error in {0}:\n".format(mg_fn))
            raise
  def check_schemas(self):
    Draft4Validator.check_schema(self.schema_options)
    Draft4Validator.check_schema(self.schema_module_group)
  def check_options(self):
    validate(self.options, self.schema_options)
  def check_module_groups(self):
    validate(self.combiner_module_group, self.schema_module_group)
    if 'inputmodules' not in self.combiner_module_group:
      print("Warning: combiner module group requires three input modules")
    for fn, mg in self.source_modules.items():
      try:
        validate(mg, self.schema_module_group)
      except ValidationError:
        print('Error in {0}:\n'.format(fn))
        raise
  def check_images(self):
    for terrain in self.options['Terrains'].values():
      filename = terrain['FileName']
      assert path.exists(self.config_file_path(filename)),"Image not found: {0}\n".format(filename)
  def check_all(self):
    self.load_schemas()
    self.check_schemas()
    self.load_options()
    self.check_options()
    self.load_module_groups()
    self.check_module_groups()
    self.check_images()

if __name__ == '__main__':
  try:
    _, options_path, schema_dir = sys.argv
  except ValueError:
    print("Usage: python wangcheck.py path/to/options.json path/to/Wangscape/doc/schemas")
  config_dir, options_fn = path.split(options_path)
  wc = Wangcheck(config_dir, options_fn, schema_dir)
  wc.check_all()