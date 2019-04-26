import sys
import re
from enum import Enum
from java_writer import writeToJavaCode

class TipeXML(Enum):
  UNKNOWN = 0
  KELAS = 1
  PANAH_TURUNAN = 2
  METHOD = 3
  ATTRIBUTE = 4

class XMLBlock:
  # attributes: 
  # id = string
  # attrSet = dict
  # styleName = string
  # styleSet = dict
  # type = TipeXML (KELAS, ATTRIBUTE, METHOD, PANAH_TURUNAN, UNKNOWN)
  # isSelfClosing = boolean
  # parentId = string
  # child = string (nullable)
  def __init__(self, block='', self_closing=False):
    self.isSelfClosing = self_closing
    if (not self.isSelfClosing):
      self.child = self.extractChild(block)
      if (self.child != ''):
        block = self.removeChild(block)
    self.findAttrsSet(block)
    self.id = self.attrSet['id']
    self.parentId = ''
    if 'parent' in self.attrSet:
      self.parentId = self.attrSet['parent']
    self.styleName = ''
    self.styleSet = {}
    self.determineType()

  # private method
  @staticmethod
  def extractChild(string=''):
    pattern = r'>\s*(<[\s\S]*?>)\s*<\/mxCell>'
    child = re.findall(pattern, string)
    return '' if len(child) == 0 else child[0]
  
  @staticmethod
  def getStyleSet(string=''):
    pattern = r'^([\s\S]+?);|([\s\S]+?)=([\s\S]+?);'
    matches = re.findall(pattern, string)
    style_name = ''; style_set = {}
    for i in range(len(matches)):
      if matches[i][0] != '':
        style_name = matches[i][0]
      else:
        style_set[matches[i][1]] = matches[i][2]
    return style_name, style_set

  def determineType(self):
    if 'style' in self.attrSet:
      self.styleName, self.styleSet = self.getStyleSet(self.attrSet['style'])
      if 'swimlane' == self.styleName:
        self.type = TipeXML.KELAS
      elif 'edgeStyle' == self.styleName[:9]:
        self.type = TipeXML.PANAH_TURUNAN
      elif 'text' == self.styleName:
        if '(' in self.attrSet['value']:  # method
          self.type = TipeXML.METHOD
        else: # attribute member
          self.type = TipeXML.ATTRIBUTE
      else:
        self.type = TipeXML.UNKNOWN
    else:
      self.type = TipeXML.UNKNOWN

  def removeChild(self, string=''):
    return string.replace(self.child, '')

  def findAttrsSet(self, string=''):
    pattern = r'([\w]+)="([\s\S]*?)"'
    matches = re.findall(pattern, string)
    self.attrSet = {}
    for i in range(len(matches)):
      self.attrSet[matches[i][0]] = matches[i][1]

  # public class
  def __str__(self):
    # id = string
    # attrSet = dict
    # type = TipeXML (KELAS, PANAH_TURUNAN)
    # isSelfClosing = boolean
    # parentId = string
    # child = string (nullable)
    return """id = {0}
    parentId = {1}
    type = {2}
    """.format(self.id, self.parentId, self.type)

class Attr:
  def __init__(self, xml, access_spec):
    self.xml = xml
    self.access_spec = access_spec

  def __str__(self):
    ret = "Access specifier = " + self.access_spec + "\n"
    ret += str(self.xml)
    return ret

class ClassGroup:
  # attributes:
  # id = string
  # class_name = string
  # xml_main = XMLBlock
  # members = list of Attr
  # methods = list of Attr
  def __init__(self, xml_main, xmlList, id):
    self.id = id
    self.xml_main = xml_main
    self.class_name = xml_main.attrSet['value']
    self.members = []
    self.methods = []
    for i in range(len(xmlList)):
      xml = xmlList[i]
      if (xml.parentId == self.id):
        if xml.type == TipeXML.ATTRIBUTE:
          self.members.append(Attr(xml, xml.attrSet['value'][:1]))
        elif xml.type == TipeXML.METHOD:
          self.methods.append(Attr(xml, xml.attrSet['value'][:1]))
  
  def __str__(self):
    ret = "id = {}\n".format(self.id)
    ret += "nama = " + self.xml_main.attrSet['value'] + "\n"
    ret += "members:\n"
    for i in range(len(self.members)):
      ret += str(self.members[i]) + "\n"

    ret += "methods:\n"
    for i in range(len(self.methods)):
      ret += str(self.methods[i]) + "\n"
    return ret


def readExternalFile(filename):
  fin = open(filename, "r")
  f_text = fin.read()
  fin.close()
  return f_text

def groupXMLS(xmlList):
  class_group = []
  panah_group = []
  for i in range(len(xmlList)):
    if (xmlList[i].type == TipeXML.KELAS):
      class_group.append(ClassGroup(xmlList[i], xmlList, xmlList[i].id))
    elif (xmlList[i].type == TipeXML.PANAH_TURUNAN):
      panah_group.append(xmlList[i])

  return (class_group, panah_group)

def main(filename):
  text = readExternalFile(filename)
  # there are two type of mxCell: self closing and not self closing
  pattern = r'(<mxCell[\s\S]*?>[\s\S]*?<\/mxCell>)|(<mxCell[\s\S]*?\/>(?!<\/mxCell>))'
    
  data = re.findall(pattern, text)
  
  xmlList = []
  for i in range(len(data)):
    if (data[i][1] == ''):  # self closing
      xmlList.append(XMLBlock(data[i][0], self_closing=True))
    else: # not self closing
      xmlList.append(XMLBlock(data[i][1], self_closing=False))
  
  class_group, arrow_group = groupXMLS(xmlList)

  writeToJavaCode(class_group, arrow_group)


if __name__ == "__main__":
  if (len(sys.argv) < 2):
    print("Argument is invalid")
    exit(1)
  main(sys.argv[1])
