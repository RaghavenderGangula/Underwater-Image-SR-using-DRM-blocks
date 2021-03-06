#!/usr/bin/env python

import os
import time
import ntpath
import numpy as np
from scipy import misc
from keras.models import model_from_json
## local libs
from utils.data_utils import getPaths, preprocess, deprocess

## for testing arbitrary local data
data_dir = "/content/drive/MyDrive/Review-2/SRDRM/data/test/lr_4x"
test_paths = getPaths(data_dir)
print ("{0} test images are loaded".format(len(test_paths)))

## load specific model
model_name = "srdrm"
#model_name = "srdrm-gan"
#ckpt_name =  "model_20_"
#checkpoint_dir  = os.path.join("checkpoints/saved/4x/", model_name) 
model_h5 = '/content/checkpoints/USR_4x/srdrm/model_25_.h5' 
model_json = '/content/checkpoints/USR_4x/srdrm/model_25_.json'
# sanity
assert (os.path.exists(model_h5) and os.path.exists(model_json))
# load json and create model
with open(model_json, "r") as json_file:
    loaded_model_json = json_file.read()
generator = model_from_json(loaded_model_json)
# load weights into new model
generator.load_weights(model_h5)
print("\nLoaded data and model")

## create dir for output test data
samples_dir = os.path.join("/content/drive/MyDrive/Review-2/SRDRM/data/output/4x/", model_name)
if not os.path.exists(samples_dir): os.makedirs(samples_dir)

# testing loop
times = []; s = time.time()
for img_path in test_paths:
    # prepare data
    img_name = ntpath.basename(img_path).split('.')[0]
    img_lr = misc.imread(img_path, mode='RGB').astype(np.float)  
    img_lr = misc.imresize(img_lr, (120,160))
    im = preprocess(img_lr)
    im = np.expand_dims(im, axis=0)
    # generate enhanced image
    s = time.time()
    gen = generator.predict(im)
    gen = deprocess(gen) # Rescale to 0-1
    tot = time.time()-s
    times.append(tot)
    # save sample images
    misc.imsave(os.path.join(samples_dir, img_name+'_gen.jpg'), gen[0])
    print ("tested: {0}".format(img_path))

# some statistics    
num_test = len(test_paths)
if (num_test==0):
    print ("\nFound no images for test")
else:
    print ("\nTotal images: {0}".format(num_test)) 
    # accumulate frame processing times (without bootstrap)
    Ttime, Mtime = np.sum(times[1:]), np.mean(times[1:]) 
    print ("Time taken: {0} sec at {1} fps".format(Ttime, 1./Mtime))
    print("\nSaved generated images in in {0}\n".format(samples_dir))

