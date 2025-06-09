if hou.ui.updateMode() == hou.updateMode.AutoUpdate:
    hou.ui.setUpdateMode(hou.updateMode.Manual)
else:
    hou.ui.setUpdateMode(hou.updateMode.AutoUpdate)