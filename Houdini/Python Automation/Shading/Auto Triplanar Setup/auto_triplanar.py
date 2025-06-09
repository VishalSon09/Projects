import hou
import os
import voptoolutils


textureChannels = {
    "Albedo": ["base", "diffuse", "albedo", "basecolor"],
    "Roughness": ["roughness", "gloss"],
    "Metalness": ["metalness","metal"],
    "Normal": ["normal"],
    "Displacement": ["disp","displacement","height"],
    "Translucency": ["translucency","sss","subsurface"],
    "Opacity": ["opacity"]
}


currentproject = os.path.dirname(hou.hipFile.path())
pathToTextures = hou.ui.selectFile( file_type=hou.fileType.Directory, start_directory = currentproject, title = "Select the texture folder")
baseName = os.path.basename(os.path.dirname(pathToTextures))



# Create the karmamaterialbuilder

mask = voptoolutils.KARMAMTLX_TAB_MASK
viewer = hou.ui.paneTabOfType(hou.paneTabType.NetworkEditor)

kwargs = {
  "pane":viewer,
  "autoplace":True
}

kmb = voptoolutils.createMaskedMtlXSubnet(kwargs, baseName, mask, 'Karma Material Builder', 'kma')

materialX = kmb.node(kmb.path()+'/mtlxstandard_surface')
disp = kmb.node(kmb.path()+'/mtlxdisplacement')

#print(mtlx)


#######################################################

for texture in os.listdir(pathToTextures):

    path = pathToTextures + texture
    #filename, file_extension = os.path.splitext(path)
    checkFileExtension = path.lower().endswith(('.rat', '.tx'))
    
    if any( val in texture.lower() for val in textureChannels['Albedo'] ) and not checkFileExtension:
    
        textureNode = kmb.createNode("kma_hextiled_triplanar", list(textureChannels.keys())[0])
        textureNode.parm("file").set(path) 
        
        materialX.setInput(1, textureNode)
        
    elif any( val in texture.lower() for val in textureChannels['Roughness'] ) and not checkFileExtension:
        textureNode = kmb.createNode("kma_hextiled_triplanar", list(textureChannels.keys())[1])
        textureNode.parm("file").set(path)
        textureNode.parm("sourceColorSpace").set('raw') 
        
        materialX.setInput(6, textureNode)  
        
    elif any( val in texture.lower() for val in textureChannels['Metalness'] ) and not checkFileExtension:
        textureNode = kmb.createNode("kma_hextiled_triplanar", list(textureChannels.keys())[2])
        textureNode.parm("file").set(path)
        textureNode.parm("sourceColorSpace").set('raw') 
        
        materialX.setInput(3, textureNode)
        
        
    elif any( val in texture.lower() for val in textureChannels['Normal'] ) and not checkFileExtension:
        textureNode = kmb.createNode("kma_hextiled_triplanar", list(textureChannels.keys())[3])
        textureNode.parm("file").set(path)
        textureNode.parm("signature").set('normals')
        
        normalMapNode = kmb.createNode("mtlxnormalmap")
        normalMapNode.setInput(0, textureNode)
        
        materialX.setInput(40, normalMapNode)
        
    elif any( val in texture.lower() for val in textureChannels['Displacement'] )  and not checkFileExtension and texture.lower().endswith(".exr"):
        textureNode = kmb.createNode("kma_hextiled_triplanar", list(textureChannels.keys())[4])
        textureNode.parm("file").set(path)
        textureNode.parm("sourceColorSpace").set('raw')
        
        disp.setInput(0, textureNode)

        
AlbedoRef = kmb.node(kmb.path()+'/Albedo')      

allParms = AlbedoRef.parms()

excludeParms = ["file","signature","sourceColorSpace","height","invert"]

for par in allParms:
    name = par.name()
    
    if name not in excludeParms: 
    
        for node in kmb.children():            
        
            if node.type().name() == "kma_hextiled_triplanar" and node.name() != "Albedo":
            
                node.parm(name).setExpression('ch("../'+str(AlbedoRef)+'/'+name+'")')



kmb.layoutChildren() 