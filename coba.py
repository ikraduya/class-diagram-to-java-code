import re

def extractChild(string=''):
  pattern = r'>\s*(<[\s\S]*?>)\s*<\/mxCell>'
  child = re.findall(pattern, string)
  return '' if len(child) == 0 else child[0]

def findAttrsSet(string=''):
  pattern = r'(([\w]+)="([\s\S]*?)")'
  matches = re.findall(pattern, string)

  return matches[2][0]

block = '<mxCell id="2" value="KelasBuatan" style="swimlane;fontStyle=1;align=center;verticalAlign=top;childLayout=stackLayout;horizontal=1;startSize=26;horizontalStack=0;resizeParent=1;resizeParentMax=0;resizeLast=0;collapsible=1;marginBottom=0;swimlaneFillColor=#ffffff;" vertex="1" parent="1"><mxGeometry x="240" y="140" width="160" height="138" as="geometry"/></mxCell>'
child = extractChild(block)
block = block.replace(child, '')

tampung = findAttrsSet(block)
pat = r'^([\s\S]+?);|([\s\S]+?)=([\s\S]+?);'
mat = re.findall(pat, tampung)
print(mat)
