# xView3
XView3 Model Documentation 
All files can be found at the GitHub repository, https://github.com/boat-buster/xview3-reference.git 

# System Requirements 

## Compatibility: 
The model is designed for libraries that exist only in Linux. Recommend Ubuntu 20.04. 

## Required platforms: Prior to creating environment install 
Anaconda: package manager and python interpreter: https://www.anaconda.com/products/individual#linux. 
- Download and run the installer.sh file from the website 

Aria2: Download utility: https://github.com/aria2/aria2/releases/tag/release-1.36.0
- Download the source code, no installation needed 
## Storage Requirements: 
Raw Data and source code: 2tb 

Chipped Data: There are two options for chips, limited and full.  
- Limited: requires 500gb of storage but model efficacy is reduced. Download the `dataloader.py` from the “limited” folder 
- Full: requires 6tb of storage but model efficacy is maximized. Download the `dataloader.py` from the “full” folder 
## File paths: The following directory subsystem should be created to house files: 
`/xview3-reference-main`

&emsp;`/limitedDataloader`

&emsp;`/fullDataloader`

&emsp;`/reference`

&emsp;&emsp;`/weights`

`/data` *2tb required*

&emsp;`/shoreline`

&emsp;`/labels`

&emsp;`/results`

&emsp;`/big`

&emsp;&emsp;`/train` 

&emsp;&emsp;`/validation` 

&emsp;&emsp;`/visuals` 

`/raid/chips` *6tb required* 

&emsp;`/train`

&emsp;`/validation`

## Source Code: 
Download the `/reference` folder from GitHub 
## Creating adequate storage: 
use the following command line arguments to create a 6tb RAID 0, assumes 3 2tb member drives: sda, sdb, sdc and mount point: `/raid`.  
- Prepend `sudo` if you are not the root user. 

On each member drive do: 
- `fdisk /dev/sd[a, b, or c]` (enter the menu) 
- `N` (new partition) 
- `P` (standard partition) 
- `1` (partition 1) 
- `enter` twice to exit 

Once the drives have been formatted: 
- `lsblk -o NAME, SIZE, TYPE` (list available devices) 
- `apt-get install mdadm` (install mdadm utility) 
- `mdadm --create --verbose /dev/mch0 --level=0 --raid-devices=3 /dev/sda1 /dev/sdb1 /dev/sdc1` (create the raid) 
- `cat /proc/mdstat` (check for success)
- `mkfs.ext4 -F /dev/mch0` (make filesystem for the raid) 
- `mkdir -p /raid` (make a mount point)
- `mount /dev/mch0 /raid` (mount the drive)
- `chmod +rwx /raid` (allow read/write /execute from the directory)
- `chown [user] /raid` (change ownership to current user)

If the machine is restarted, Linux will not mount the RAID automatically. To mount the existing drive on restart do `mount /dev/mch0 /raid`
## Creating the Anaconda environment 
Navigate to `/reference` and run 
- `conda env create –f environment.yml`
- `conda install pytorch torchvision torchaudio cudatoolkit=11.3 -c pytorch`
- `conda activate xview3`
- `pip install ipykernel`
- `python -m ipykernel install --user --name xview3`  
- `conda install -c conda-forge ipywidgets`
- `jupyter nbextension enable --py widgetsnbextension`
- `python torch-checks.py`  

To activate the environment and load the jupyter labs run 
- `conda activate xview3`
- `jupyter lab`
## Downloading the data  
- Download the train.csv.tgz, validation.csv.tgz, and extract both to strip the .tgz 
- Download shoreline/train.tar.gz, and shoreline/validation.tar.gz 
- Download validation.txt and train.txt into `/reference` 

Navigate to /reference and run 
- `aria2c --input-file=validation.txt --auto-file-renaming=false --continue=true --dir=./data/big/validation/ --dry-run=false`
- `aria2c --input-file=train.txt --auto-file-renaming=false --continue=true --dir=./data/big/training/ --dry-run=false`

NOTE: The train download will take several hours as it is very large  

To unpack the files, navigate into the training and validation subdirectories and run  
- `for file in *.tar.gz; do tar xzvf "${file}" && rm "${file}"; done`
## Running the notebook 
All steps to load datasets and conduct training are housed in the jupyter notebook file. 

Open the notebook 
- `conda activate xview3`
- `jupyter lab`

## Preprocessing data 
The first time the model is run, the downloaded data must be preprocessed
- Ensure the argument `overwrite_preproc = True`

Once the data has been preprocessed one time, set `overwrite_preproc = False` 
- While overwriting the preprocessed data every time does not negatively affect the data, it is computationally expensive and unnecessary

If the dataloader file is changed and the chips need to be created differently, rerun with `overwrite_preproc = True`
- This also applies to the dataset creation for the inference model

## Training the model 
Configure the following parameters in the following order: 
- `bs`: adjust the batch size to the highest number the graphics cards can support. If Cuda raises memory allocation errors during training, lower the batch size. 
- `lr`: if the batch size is significantly adjusted, scale the learning rate inversely. For example, if the batch is decreased from 50 to 8, adjust the learning rate from 0.03 to 0.1. 
- `num_epochs`: once the batch size and learning rate are properly configured, run one epoch to decide the estimated time per epoch. Use the following formula to decide the maximum number of epochs: epochs = (time allotted – 3hrs)/time_per_epoch  

Click the run all button or `ctrl + shift + alt + enter` 

## Metrics 
The model is scored according to the provided metrics from DIU: 

Maritime Object Detection `F1D` 
- The maritime object detection score, F1D is the Dice coefficient on the core object detection challenge presented by xView3 -- identifying vessels and fixed infrastructure in each scene. Ground truth positives are man-made maritime objects that are validated by a human labeler and/or Automatic Identification System (AIS) correlation. 
- In order to perform highly on this component, a model must be able to map the shoreline to a high fidelity, handle SAR artifacts such as ambiguities and sea clutter, and generalize well across a variety of sea states, satellite sensor configurations, and geographic regions. 

Close-to-Shore Object Detection `F1S` 
- Detecting vessels close to the shore is of vital interest to the IUU enforcement community. Since vessels tend to be grouped close together near the shore, and land-based artifacts such as boulders and radar reflections are common, the detection task is harder. "Close to shore" vessels are defined as those vessels up to 2km away from the shoreline. 

Vessel Classification `F1V` 
- Classifying a maritime object as "vessel" or "non-vessel" is the lowest fidelity classification that is useful to the IUU enforcement community. Positive classes are defined as "vessel" upon which an F1 score is calculated with regards to the ground truth. 

Fishing Classification `F1F` 
- Once you have identified that a detected object is a "vessel", an F1 score is calculated over the model's ability to differentiate between "fishing" and "non-fishing" vessels, with the positive class being "fishing". There are many different types of fishing vessels, such as trawlers, trollers, dredge fishers, and long liners. A complete list is available in the '''dataloader.get_label_map()''' function. 

Vessel Length Estimation `PEL` 
- Knowing the size of the vessel is critical for IUU enforcement efforts. Since SAR is inherently noisy, this component is scored using an aggregate percent error defined as PEL above. 

## Scoring the model 
Once the model is finished training, it will automatically run an inference model on the validation set. 

The following code block scores the results in a variety of areas and supplies an aggregate score.  

## Interpreting results 
All scores are normalized to the range 0:1 
- If a score is `Nan`: The model is not producing any results with MEDIUM or HIGH confidence. Continue training/improving the model 
- If a score is `0`: The model is producing high confidence results, but these results are completely wrong. Reconsider how the model is running ex: how are bounding boxes being created? 

## Saving and reloading model states 
The model is configured to save a checkpoint every epoch. Checkpoints contain the learned weights, optimizer state, and learning rate scheduler. 

To begin training from a saved stated, modify the epoch number in `trained_model_1_epochs.pth` to the epoch you would like to load. 

It is recommended to save the current best weights in `/bestWeights` to avoid the model overwriting them. The `load_state_dict()` path parameter can easily be configured to `./bestWeights/best.pth`

## Visualizing results 

The visualizer automatically runs at the end of the notebook and copies results to `/results/DDM` where DDM is the current day and month. Ex: /03March 

To force a run of the visualizer `python visualizer.py`

If visualizations need to be preserved, copy the directory before running the script again `cp –avr /visuals /results/DDM` where DDM is current day and month as before 

## Saving records 
The final block in the notebook will automatically write out the learning rate, batch size, and number of epochs scheduled for the run, as well as a complete output of the scoring function. This text file can be found in the `/results/DDM` folder as well. 

## Runtime notifications 
The jupyter notebook includes functionality to ping a Telegram bot to send messages when the runtime finished successfully, or errors out. The chat group to receive notifications from the bot is linked here. https://t.me/+FMYhbH_VaFEwZjRh
