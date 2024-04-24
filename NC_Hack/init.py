from concurrent.futures import ThreadPoolExecutor

from calendar import c
import os
os.environ["OPENCV_IO_ENABLE_OPENEXR"] = "1"

try:
    import cv2
except:
    import os
    print('opencv not installed, installing it')
    os.system('python -m pip install opencv-python')
    import cv2
    
print('NC_Hack loaded')

def convert_NC(path):

    exr_name = os.path.basename(os.path.dirname(os.path.dirname(path)))
    frames = {}
    max_x = 0
    max_y = 0

    if "split_0_0" in os.listdir(path):
        split_folders = os.listdir(path)

        for f in split_folders:
            if "split_" in f:
                split_path = os.path.join(path, f)
                
                x = int(f.split("split_")[1].split('_')[0])
                y = int(f.split("split_")[1].split('_')[1])
                max_x = max(max_x, x+1)
                max_y = max(max_y, y+1)  
                coords = (x, y) 

                exrs = os.listdir(split_path)
                for i, exr in enumerate(exrs):
                    exr_obj = {}
                    
                    if ".exr" in exr:
                        timing = exr.split('.exr')[0].split(".")[-1]
                        frame = {"path": os.path.join(path, f, exr),
                                 "coords": coords}
                        if timing not in frames:
                            frames[timing] = []
                        frames[timing].append(frame)

      
    def concat_tile(im_list_2d):
        return cv2.vconcat([cv2.hconcat(im_list_h) for im_list_h in im_list_2d])  
      
      
    def tile(data):
        timing, chunks = data
        if len(chunks) == max_x*max_y:
            chunks_sorted = []
            for x in range(max_x):
                y_chunks = []
                for y in range(max_y):
                    y_chunks.append(cv2.imread(chunks[(x*max_y)+y]["path"], cv2.IMREAD_UNCHANGED | cv2.IMREAD_ANYDEPTH))
                chunks_sorted.insert(0,y_chunks)
                
            im_tile = concat_tile(chunks_sorted)
            os.makedirs(os.path.join(path, "../merged"), exist_ok=True)
            cv2.imwrite(os.path.join(path, f"../merged/{exr_name}.{timing}.exr"), im_tile)

    with ThreadPoolExecutor(max_workers=32) as executor:
        results = list(executor.map(tile, frames.items()))
        print('done')
