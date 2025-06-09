import replicate
import urllib.request
from PIL import Image
import hou

def test():
  model_url = 'get it from replicate.com'

  pre_prompt = 'You are a houdini AI assistant, please respond everything in SideFx Houdini context'
  usr_prompt = hou.ui.readInput('Enter a prompt:')

  response = replicate.run(model_url,
                           input={'prompt': f'{pre_prompt} {usr_prompt} AI: ', 'temperature':0.1, 'max_length':500, 'repetition_penalty':1}
                           )
  res = ''

  for r in response:
    res += r

  print(res)


def textureGenerator():

  usr_input = hou.ui.readInput('Enter a prompt:')
  model_url = 'stability ai url from replicate.com'
  output = replicate.run(model_url,
                           input={'prompt': f'{usr_prompt}, high resolution, realistic, tileable'}
                           )
  res = output[0]
  print(res)
  texture_path = 'pathtoyourvenv/replicate_api/texture_01.png'
  urllib.request.urlretrieve(res, texture_path)

  texture_node = hou.selectedNodes()[0]
  texture_node.parm('map').set(' texture_path')