import hou
import os
from PySide2 import QtCore, QtUiTools, QtWidgets



class AssetLoader(QtWidgets.QWidget):

    def __init__(self):
    
        super(AssetLoader, self).__init__()
        
        #layout
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setContentsMargins(10,10,10,10)
        

        
        
        self.combo_box = QtWidgets.QComboBox(self)
        self.combo_box.addItems(['Select Folders','Multi Files'])
        self.combo_box.currentIndexChanged.connect(self.on_combo_box_changed)
        
        
        checkbox_layout = QtWidgets.QHBoxLayout()
        
        checkbox_layout.addWidget(QtWidgets.QLabel("LOD"))
        self.checkbox = QtWidgets.QCheckBox()
        
        checkbox_layout.addWidget(self.checkbox)
        
        checkbox_layout.addWidget(QtWidgets.QLabel("Prefix"))
        self.lineedit = QtWidgets.QLineEdit()
        self.lineedit.setText("Var")
        checkbox_layout.addWidget(self.lineedit)
        
        self.btn = QtWidgets.QPushButton("Load Assets")
        
        self.info_label = QtWidgets.QLabel("Select folder with subfolders")
        
        main_layout.addWidget(self.combo_box)
        main_layout.addLayout(checkbox_layout)
        main_layout.addWidget(self.btn)
        main_layout.addWidget(self.info_label)
        self.setLayout(main_layout)
        self.setParent(hou.ui.mainQtWindow(), QtCore.Qt.Window)
        self.setWindowTitle("Asset Loader")
        
        self.btn.clicked.connect(self.importFiles)
        
    def on_combo_box_changed(self, index):
        if index == 1:  # if "Multi Files" is selected
            self.checkbox.setDisabled(True)  # disable checkbox
            self.lineedit.setDisabled(True)  # disable lineedit
            self.info_label.setText("Select folder with multiple files")
        else:
            self.checkbox.setDisabled(False)  # enable checkbox
            self.lineedit.setDisabled(False)  # enable lineedit
            self.info_label.setText("Select folder with subfolders")
        
    def importFiles(self):
    
        start_dir = "C:/CG_CONTENT/Models"
        pathToFiles = hou.ui.selectFile(  start_directory = start_dir, file_type=hou.fileType.Directory, title = "Select the files folder")        
    
        
          
            
        if pathToFiles:
        
            obj = hou.node("/obj")
            assets_geo = obj.createNode("geo", "Assets")        
        
            if self.combo_box.currentIndex() == 0:
            

                
                
                for name in os.listdir(pathToFiles):
                
                    if self.lineedit.text() in name:
                    
                        if self.checkbox.isChecked():
                    
                            for file in os.listdir(os.path.join(pathToFiles, name)):
                            
                                if "LOD0" in file:      
                                
                                    base_name = os.path.splitext(file)[0]
                                    
                                    # Get full path of file
                                    file_path = os.path.join(pathToFiles, name, file)   
                    
                                    file_node = assets_geo.createNode("file")
                                    
                                    
                                    
                                    file_node.parm("file").set(file_path) 
                                    
                                    file_node.parent().collapseIntoSubnet((file_node,), base_name.split("_")[0])
                                
                        else:
                            
                            for file in os.listdir(os.path.join(pathToFiles, name)):   
                                
                                # Get full path of file
                                file_path = os.path.join(pathToFiles, name, file)   
                
                                file_node = assets_geo.createNode("file")
                                
                                
                                
                                file_node.parm("file").set(file_path) 
                                
                                file_node.parent().collapseIntoSubnet( (file_node,), name.replace(" ", "_") ) 
                                
                                #print(name)
                
                 
            else:
                
                for name in os.listdir(pathToFiles):
                
                    base_name = os.path.splitext(name)[0]
                
                    # Get full path of file
                    file_path = os.path.join(pathToFiles, name)   
                    
    
                    file_node = assets_geo.createNode("file")
                    
                    
                    
                    file_node.parm("file").set(file_path) 
                    
                    file_node.parent().collapseIntoSubnet( (file_node,), base_name.replace(" ", "_") )
                        
            assets_geo.layoutChildren()                    


global win
try:
    win.close()
except:
    pass
win = AssetLoader()
win.show()