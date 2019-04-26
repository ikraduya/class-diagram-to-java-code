import re
import os
import shutil

CLASS_TEMPLATE = """class {0} {1}{{
{2}
{3}
}}
"""

# fontStyle=4 maka italic = static
# - private
# + public
# # protected
VARIABLE_TEMPLATE = '\t{0}{1}{2} {3};'
def fitMemberVar(member):
  access_spec = ''
  if member.access_spec == '-':
    access_spec = 'private '
  elif member.access_spec == '+':
    access_spec = 'public '
  elif member.access_spec == '#':
    access_spec = 'protected '

  static = ''
  if ('fontStyle' in member.xml.styleSet) and member.xml.styleSet['fontStyle'] == "4":
    static = 'static '
  
  var_re = re.findall(r'([\w\d]+)\s*:\s*((?:[\w\d,\s]|(?:&lt;|&gt;))+)', member.xml.attrSet['value'])[0]
  var_type = var_re[1].replace('&lt;', '<').replace('&gt;', '>')
  var_name = var_re[0]
  return VARIABLE_TEMPLATE.format(access_spec, static, var_type, var_name)

def parseParamsText(params_raw):
  params_raw = params_raw.replace(',', ', ')
  re_params = re.findall(r'(?:([\w\d]+)\s*:\s*((?!,)(?:(?:[\w\d]|(?:&lt;|&gt;))+))),?\s*', params_raw)
  
  params_text = ''
  for i in range(len(re_params)):
    params_text += re_params[i][1].replace('&lt;', '<').replace('&gt;', '>') + ' ' + re_params[i][0]
    if i != len(re_params)-1:
      params_text += ', '
  return params_text

# Access_spec, [static], return type, method name, param list
METHOD_TEMPLATE = """\t{0} {1}{2} {3}({4}) {{
\t\t// Implementasi {3}
\t\t{5}
\t}}
"""
def fitMethod(method):
  access_spec = ''
  if method.access_spec == '-':
    access_spec = 'private'
  elif method.access_spec == '+':
    access_spec = 'public'
  elif method.access_spec == '#':
    access_spec = 'protected'

  static = ''
  if ('fontStyle' in method.xml.styleSet) and method.xml.styleSet['fontStyle'] == "4":
    static = 'static '
  
  method_re = re.findall(r'([\w\d]+)\s*\((.*?)\)\s*:\s*((?:[\w\d]|(?:&lt;|&gt;))+)', method.xml.attrSet['value'])[0]
  method_name = method_re[0]
  method_params = parseParamsText(method_re[1])
  method_ret_type = method_re[2].replace('&lt;', '<').replace('&gt;', '>')
  return METHOD_TEMPLATE.format(access_spec, static, method_ret_type, method_name, method_params, "return Null" if (method_ret_type != 'void') else "")

def getIsARelations(arrow_group):
  isARelations = {}
  for i in range(len(arrow_group)):
    isARelations[arrow_group[i].attrSet['source']] = arrow_group[i].attrSet['target']
  return isARelations

def writeAClass(a_class, parent=''):
  # class name
  class_name = a_class.class_name

  # parent
  if (parent != ''):
    parent = 'extends ' + parent + ' '

  # member variable
  member_text = []
  members = a_class.members
  for i in range(len(members)):
    member_text.append(fitMemberVar(members[i]))
  member_text = '\n'.join(member_text)
  if (len(member_text) > 0):
    member_text += '\n'

  # methods
  method_text = []
  methods = a_class.methods
  for i in range(len(methods)):
    method_text.append(fitMethod(methods[i]))
  method_text = '\n'.join(method_text)

  filename = class_name + ".java"
  
  f = open('output/' + filename, "w+")
  f.write(CLASS_TEMPLATE.format(class_name, parent, member_text, method_text))
  f.close()

def getParentClass(a_class, class_group, isARelations):
  if (a_class.id not in isARelations):
    return ''
  for i in range(len(class_group)):
    if (class_group[i].id == isARelations[a_class.id]):
      return class_group[i].class_name
  return ''

def writeToJavaCode(class_group, arrow_group):
  isARelations = getIsARelations(arrow_group)
  
  if os.path.exists('output'):
    shutil.rmtree('output', ignore_errors=False, onerror=None)
  os.makedirs('output')

  for i in range(len(class_group)):
    parent = getParentClass(class_group[i], class_group, isARelations)
    writeAClass(class_group[i], parent)
