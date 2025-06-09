import os
import hou
import shutil
import re
import glob

hipdir = os.environ["HIP"]
homedir = os.environ["HOME"]

image_extensions = ('.jpg', '.jpeg', '.png', '.exr', '.hdr', '.tif', '.targa')
model_extensions = ('.obj', '.fbx', '.abc')

fileRefs = hou.fileReferences()
udim_placeholder = "<udim>"

def expand_udim_path(path):
    """ Expand UDIM paths into actual file paths. """
    udim_pattern = re.sub(udim_placeholder, '[0-9][0-9][0-9][0-9]', path, flags=re.IGNORECASE)
    expanded_files = glob.glob(udim_pattern)
    return expanded_files

for parm, path in fileRefs:
    # Normalize the path for comparison
    path_lower = path.lower()

    if path_lower.endswith(image_extensions) or path_lower.endswith(model_extensions) or udim_placeholder in path_lower:
        parmName = parm.name()
        parmPath = parm.path()
        selNode = parm.node()

        paths_to_copy = [path]
        is_udim_path = udim_placeholder in path_lower
        if is_udim_path:
            paths_to_copy = expand_udim_path(path)

        for filePath in paths_to_copy:
            if not (filePath.startswith("$JOB") or filePath.startswith("$HIP")):
                # Get the file name with extension
                file_name_with_extension = os.path.basename(filePath)

                if filePath.lower().endswith(image_extensions):
                    base_folder = 'tex'
                elif filePath.lower().endswith(model_extensions):
                    subfolder = parmPath.split('/')[3]
                    subfolder = re.sub(r'_\d+', '', subfolder)
                    base_folder = os.path.join('geo', subfolder)
                else:
                    base_folder = ''

                if filePath.startswith("$HOME"):
                    filePath = filePath.replace("$HOME", homedir)
                    filePath = os.path.abspath(filePath)

                path_folder = os.path.join(hipdir, base_folder)
                if not os.path.exists(path_folder):
                    os.makedirs(path_folder)

                fileAppend = os.path.join(path_folder, file_name_with_extension)
                if not os.path.abspath(filePath) == os.path.abspath(fileAppend):
                    shutil.copyfile(filePath, fileAppend)

                relativePath = os.path.join("$HIP", base_folder, file_name_with_extension)
                if is_udim_path:
                    # Replace the actual file name with <UDIM>
                    relativePath = re.sub(r'\d{4}', '<UDIM>', relativePath)

        if is_udim_path:
            # Ensure the parm is set only once with the UDIM placeholder path
            relativePath = re.sub(r'\d{4}', '<UDIM>', relativePath)
        selNode.parm(parmName).set(relativePath)
