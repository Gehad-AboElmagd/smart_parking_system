"""
								  Coder : Eng.Omar
								  Version : v1.0B
								  version Date :  19 / 4 / 2023
								  Code Type :  CV | OCR => smart_parking_project
								  Title : Smart Parking System
								  Interpreter : cPython  v3.11.0 [Compiler : MSC v.1933 AMD64]
"""

import os 
import sys
import cv2
import time 
import psutil

import pyautogui
import numpy as np
import pytesseract as tsr

import Garage_DB as db

 #_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#
# TODO : finish CUDA accel function and use it in ocr_main()
# TODO : show a  timer in  video ( 5 ~ 10 sec )  use cv2.puttext()
# TODO : add audio feedback 
# TODO : car plate / license id simple  template detection
# TODO : tracking 
# TODO : make it work with real id cards ( mostly will change tesseract psm mode to parse )
 #_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#


 #_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#
def render_timer ( frame : cv2.UMat | np.ndarray , timer : int , **extraArgs ) -> cv2.UMat | np.ndarray : ... 
 #_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#

 #_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#
def make_rectangle_obj( frame : cv2.UMat | np.ndarray , id_dimension : tuple  , color : str , **extraArgs ) -> tuple: 
	"""
		1. specs of rectangle to be rendered in live video for guiding end user
  
		2. get points to position helper rectangle in center
  
		3. define rectangle object to be rendered on video frame
  
  ---

		* Returns:
			 rectangle_obj , [(x1,y1) , (x2 , y2)]
	"""
	#specs of rectangle to be rendered in live video for guiding end user
	blue  = (255 , 0 , 0)
	green = ( 0  , 255 , 0)
	red   = ( 0  , 0 , 255)
	frame_shape = extraArgs['_frame_shape']
	x1 , x2 , y1 , y2 = [-1 for i in range(4)]
 
	rec_spec = {
    'top_left_coordinate'  : tuple , 
    'bot_right_coordinate' : tuple  ,
    'color' : (red if color == 'red' else green ), 
    'thickness' : 1 ,
    }
 
	#keep separate copy of original video frame with out the rectangle and timer objects for better proccess 
	frame_to_show = cv2.UMat(np.array(frame.get())) #deep copy ->  not share any data with frame (may take more mem. but efficent than COW copy + solved '=' problem)
	
	if testing_mode == True : #TESTING
		print (f"frame_to_show var type: {type(frame_to_show)}")
 
	#get points to position helper rectangle in center
	y_center , x_center = [ int(x) // 2 for x in frame_shape ] #frame_to_show  has no shape attribute (UMat obj)
		#top left 
	x1 , y1 = x_center - id_dimension[0] // 2 , y_center - id_dimension[1] // 2
		#bot_right
	x2 , y2 = x_center + id_dimension[0] // 2 , y_center + id_dimension[1] // 2	
		#make rec_in_center
	rec_spec['top_left_coordinate'] , rec_spec['bot_right_coordinate'] = (x1 , y1) , (x2 , y2)
	
	
	frame_rect_obj = cv2.rectangle ( frame_to_show , *rec_spec.values() )
    
    
	pos = [(x1 , y1 ) , (x2 , y2)]
	return frame_rect_obj , pos
 #_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#
	
 

 #_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#
def check_gpu_accl (_default_gpu : int = 1) -> tuple : #default gpu set to nvidia cuda == 1
	"""
	* use only  inside video_settings()

	* NOTE 1: 
 				this fuctntion gets exactly whose api  enabled  cuda or opencl
				and prefers opencl if both are enbaled 
				due to it being opensource and was writtern in an PC using AMD GPU
    

	* NOTE 2:
 				depending on used GPU acceleration main function will call
				the appropriate ocr reader function
    

	* NOTE 3: 
 				if OpenCL enabled use cv2.UMat to save frames in and then process them
				after that convert them back to cv2.Mat
				if cuda is enabled use cv2.cudaGpuMat instead of cv2.UMat 
				and cv2.cuda.foo() instead of cv2.foo() in some opencv-python functions
    
    ---
  
	* Returns:
 		tuple (is_enabled? , gpu_type 1== cuda 2==opencl)
  
	"""

	#check if cuda / opencl is enabled  
	cuda_available : bool = cv2.cuda.getCudaEnabledDeviceCount() > 0
	cuda_enabled   : bool = 'CUDA'	in cv2.getBuildInformation()
	
	opencl_enabled : bool = cv2.ocl.haveOpenCL()
	cv2.ocl.setUseOpenCL(True) if opencl_enabled else False

	#alternative check for opencl (but i'll do it also XD)
	opencl_enabled : bool = 'OpenCL' in cv2.getBuildInformation()
	if opencl_enabled : cv2.ocl.setUseOpenCL(True)
 
 	#even if no gpu accel available  default function is Nvidia cuda function => 2
	gpu_accel_enabled : list[bool , int]= [False  , 2]
 
  
	if cuda_enabled and cuda_available : 
		gpu_accel_enabled [:2] = True , 1
		if _default_gpu == 1 : return tuple ( gpu_accel_enabled )  #even if opencl is avilable gpu def is nvidia if == 1 
  
	if opencl_enabled :
	#no need to check if its default ( it will auto override if nvidia is not default )
		gpu_accel_enabled [:2] = True , 2 

	return tuple ( gpu_accel_enabled )
 #_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#

 #_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#
def enable_multithreading (thread_no : int = 4) :  #in case gpu acceleration is not enough to maintain stable 30fps
	cv2.setNumThreads(thread_no)#enable cv2 multithread
	ret = f"number of cv2 used threads: {cv2.getThreadNum()} "
	return ret

 #_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#

 #_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#
def video_settings_setup (cam_indx : int  = 0, fps : int = 30 , vid_length_sec : int = 10, res : tuple = (1366 , 768)) -> tuple :
	"""
	* This function does set up the video objects
	* res is set by default to 720p
 
	* NOTE 1:
 
		* gpu_accel == 0  no GPU acceleration found 
		* gpu_accel == 1  Cuda GPU acceleration found
		* gpu_accel == 2  OpenCl GPU acceleration found
 
	* NOTE 2:
 
		* active_gpu_api == 0 (no active accel api)
		* active_gpu_api == 1 (Cuda)
		* active_gpu_api == 2 (OpenCL)
  
  ---
  
	* Returns :
 
		vid , fps , frametime , vid_length_sec , active_gpu_api
  

	"""
	#set the path to the tesseract dir ( not needed if you added it to win. env. variables)
	tsr.pytesseract.tesseract_cmd =  r'C:\Program Files\Tesseract-OCR\tesseract.exe'
 
	# Get the process object for the current process
	process = psutil.Process(os.getpid())
	# Set the process priority to "high"
	process.nice(psutil.HIGH_PRIORITY_CLASS)
	
	enable_multithreading(12)
 
	is_gpu_accel_enabled  , gpu_api = check_gpu_accl () 
	
 
	if testing_mode == True :
		print ( f"gpu api is : {gpu_api}") #TESTING
 
	if is_gpu_accel_enabled :
		if gpu_api == 1 : #use cuda vid obj 
			
			#you can change video I/O backends used by adding  the argument :
			#cv2.CAP_DSHOW  (Dshow is the default in my omar-pc)
			vid = cv2.VideoCapture(cam_indx , cv2.CAP_CUDA)
		else : #OpencL
			vid = cv2.VideoCapture(cam_indx , cv2.CAP_DSHOW)
	else : #DEFAULT 
		vid = cv2.VideoCapture(cam_indx , cv2.CAP_DSHOW)
  
	if testing_mode == True :
		# TO GET YOUR DEFAULT CV2 RES :
		# default res on omarpc obs vritual cam plugin -> (height_Y : 480 , width_X : 640)
		hCV2 = vid.get(cv2.CAP_PROP_FRAME_HEIGHT)#TESTING
		wCV2 = vid.get(cv2.CAP_PROP_FRAME_WIDTH)#TESTING
		print (f"cv2 res is : {wCV2, hCV2}") #TESTING
		# TO GET YOUR DEFAULT SCREEN RES :
		wSCREEN , hSCREEN = pyautogui.size()#TESTING
		print ( f"screen res is : {wSCREEN , hSCREEN}")#TESTING
		  
	
	#set custom res
	vid.set(cv2.CAP_PROP_FRAME_WIDTH , res[0] ) 
	vid.set(cv2.CAP_PROP_FRAME_HEIGHT, res[1] )
	
 
	#frametime is needed to put as cv2.waitkey() argument 
	frametime = 1000 // fps 

	return vid , fps , frametime , vid_length_sec , gpu_api 
 #_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#
 
 #_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#

def compare_img ( img_to_comp : np.ndarray  , ref_img : np.ndarray) -> list :
	''' Returns : good_matches , (ref_kp , img_kp) '''
 
 
 

#NOTE: DETECT keypoints and create the decriptors for ref.img and img_to_cmp

	detect_obj = cv2.ORB_create() #two algorithms in ORB : corner detection and binary descriptor extraction 
	#instead of ORB you could use SIFT. it's better and more accurate but slower.
	#since our objects are relativily simple and we need high process rate (30FPS+) will use ORB for now.

	#brute force matching + norm_hamming (is better for cv and images than L1 , L2)
	match_obj = cv2.BFMatcher(cv2.NORM_HAMMING) 

	ref_kp , ref_desc = detect_obj.detectAndCompute(ref_img , mask= None)
	img_kp , img_desc = detect_obj.detectAndCompute(img_to_comp , mask= None)

	if img_desc is  None or ref_img is None:
		return -1 , -1
 
#NOTE: MATCH and save best matches

	if testing_mode == True : #TESTING
		print (f"ref_desc type : {type(ref_desc)}  img_desc  type {type(img_desc)}")
  
	matched_descs = match_obj.match(ref_desc , img_desc) 
	#match() returns DMatch_Obj = [img_desc_indx , ref_img_desc_indx , distance]
	
	matched_descs = sorted(matched_descs , key= lambda x : x.distance) # each x is a matched_descs obj
	
	tolerance = 16
	good_matches = matched_descs[:tolerance] #get only best n matches (smallest distance)
 
	if testing_mode == True :
		print (f"tot number of matched descs: {len(matched_descs)}") #TESTING
	
	return ( good_matches , (ref_kp , img_kp) )
 
 #_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#
def get_trans_mat( good_matches : cv2.DMatch  , key_points : tuple ) -> np.ndarray :
	''' Returns : homography transformation matrix '''
 
	#NOTE:  homography transformation matrix : 
	# [ cos(theta)  -sin(theta)  0 ]
	# [ sin(theta)   cos(theta)  0 ]
	# [     0            0       1 ]
	#trans. mat will be pure rotation mat (like above) 
	# if and ONLY if the image is only rotated  with no any other transformation
	ref_kp , img_kp = key_points

	ref_good_pts = np.float32( [ref_kp[m.queryIdx].pt for m in good_matches] ) # 'pt' is the pixel coordinate of a keypoint
	ref_good_pts = ref_good_pts.reshape(-1,1,2) #make 3D mat of coordintes [ [x1,y1] , [x2,y2] ..]
 
	img_good_pts = np.float32( [img_kp[m.trainIdx].pt for m in good_matches] )
	img_good_pts = img_good_pts.reshape(-1,1,2)
 
 	#NOTE: in finHomography() function: cv2.RANSAC is a (match outlier excluder Algorithm) and 5.0 is the thresholder
	trans_mat , choosed_matches_mask = cv2.findHomography(  ref_good_pts , img_good_pts , cv2.RANSAC , 5.0 ) 
	
	return trans_mat 

 #_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#
def get_skew_angle( homograph_rot_mat : np.ndarray , img_to_skew_shape : tuple ) -> tuple:
	"""
#### Pure rotation mat should look like :
  
|  [ cos(theta) | -sin(theta)| 0 ]  	|
| ------- 		 | --- 		  | ---     |
|  [ sin(theta) | cos(theta) | 0 ] 		|
|  [     0 		 | 0 			  | 1 ]		|

---
---
	Returns:
 
		( skew_angle , (center , h , w) )
  
  if fail return -1 , -1
	"""
	if type (homograph_rot_mat) != type(None) :
		sine = homograph_rot_mat [1 , 0]
		cos  = homograph_rot_mat [0 , 0]
		skew_angle = np.arctan2(sine , cos) * (180 / np.pi)
  
		if testing_mode == True :
			print ( f"IMAGE ROTATION ANGLE IS : {skew_angle} DEGREES")#TESTING
  
  
	else :
		return -1 , -1 #skip this frame
	
	h , w = img_to_skew_shape
	center = ( w // 2 , h // 2)
	
	return ( skew_angle , (center , w , h) )
 #_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#
def affine_trans ( _skew_angle : int , img_coord : tuple , _image_to_skew : np.ndarray) -> np.ndarray :
	"""
	Returns:
		 deskewed_image : np.ndarray
	"""
	center , w , h = 	img_coord
 
	affine_rot_mat = cv2.getRotationMatrix2D(center , _skew_angle , scale= 1.0) #1.0 is image scale factor
	rotated_img = cv2.warpAffine(_image_to_skew , affine_rot_mat , (w,h) , flags= cv2.INTER_CUBIC, borderMode= cv2.BORDER_REPLICATE )
	deskewed_img = rotated_img
 
	return deskewed_img
 #_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#
def rotate_180 (img_to_rotate_180 : np.ndarray) -> np.ndarray :
	rot_angle = 180
	rotated_180_img = affine_trans (rot_angle , img_to_rotate_180)

	return  rotated_180_img
 #_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#
def deskew_img(  img_to_skew : np.ndarray , ref_img : np.ndarray , **extraArgs ) -> np.ndarray : #lets call it de-rotate for now
	"""
---
	Returns:
		 np.ndarray: image after deskew
   if error return -1
	"""
	img_shape = extraArgs['img_shape']
	match_err = False
 
 
	good_matches , key_points = compare_img( img_to_skew , ref_img)
 
	if good_matches == -1 or key_points == -1 :
		return -1 

	trans_mat = get_trans_mat( good_matches , key_points)

	skewed_angle , coordinates = get_skew_angle ( trans_mat , img_shape)
 
	if skewed_angle == -1 or coordinates == -1: 
		return -1
	else : 
		deskewed_img = affine_trans( skewed_angle , coordinates , img_to_skew)
		return deskewed_img 

 #_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#
 
 #_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#
def proccess_vid_frame( _frame : cv2.UMat | np.ndarray , _id_dimension : tuple , _is_valid ,  _is_valid2 , _ref_img : cv2.UMat | np.ndarray , **extraArgs) -> cv2.UMat | np.ndarray :
	"""
	0. cvt to gray-scale
	1. inv frame
	2. threshold fram
	3. deskew frame
	4. sharpen the frame
	5. dilate frame by one itteration 

#### NOTE: image background black and foreground is white and foreground is what we need this makes ocr better 
#### to use opposite  use erode() instead of dilate()


---
	Returns:
		final_img_deskew , final_img_no_deskew

	if error return -1
"""

	skip = False
 
	# TODO : benchmark passing to proccess_vid_frame() as mat then copy() then cvt both copy and frame to UMat and this method
	# NOTE : if prev. todo is better in benchmark then be aware that this function is used from both cuda and opencl functions
	# and you will need to make another for cude

	#make the rectangle object to help position ID card when scanning (initially RED)
	frame  , pos  = make_rectangle_obj( _frame , _id_dimension , ('red' if _is_valid  == 0 else 'green') , _frame_shape = extraArgs['frame_shape'] )
	frame2 , pos2 = make_rectangle_obj( _frame , _id_dimension , ('red' if _is_valid2 == 0 else 'green') , _frame_shape = extraArgs['frame_shape'] )

	# TODO : frame = make_timer_obj (frame , _id_dimension , time_left_sec : int )

	#show green  if any edited  frames suceeded (at fps to visual aid enduser)
	if _is_valid == 1 :
		cv2.imshow("Camera", frame)
	elif _is_valid2 == 1 :
		cv2.imshow("Camera", frame2)
	else : #show any red
		cv2.imshow("Camera", frame)
  
	frames_to_skip_procs = 10

	if extraArgs['count'] % frames_to_skip_procs != 0 :
		skip = True
		if testing_mode == True : #TESTING
			print( f"skip frame? {skip}")
   
		return skip , skip , skip

	if extraArgs['count'] % frames_to_skip_procs == 0 :
		skip = False
  
	if testing_mode == True : #TESTING
				print( f"skip frame? {skip}")
	
	x1 , y1 = pos[0][0] , pos[0][1]
	x2 , y2 = pos[1][0] , pos[1][1]

	#crop image to get the id card only (with + 5px than actuall id size)
	# _frame = _frame[ y1 : y2 , x1 : x2  ] #dont work for Umat
	_frame = cv2.UMat( _frame , [y1 , y2] , [x1 , x2]) 
 
	#change image to gray scale cuz THRESH OTSU Needs that
	_frame = cv2.cvtColor(_frame , cv2.COLOR_BGR2GRAY)

	# if testing_mode == True :
	# 	cv2.imshow("TESTING : show image before edit *grayed*" , _frame) #TESTING

	_frame = cv2.bitwise_not(_frame)

	# if testing_mode == True :
	# 	cv2.imshow("TESTING : show image bitwise not" , _frame)#TESTING


	_frame = cv2.threshold(_frame , 0 , 255 , cv2.THRESH_BINARY_INV+ cv2.THRESH_OTSU)[1]

	# if testing_mode == True :
	# 	cv2.imshow("TESTING : show image threshed" , _frame)#TESTING

	no_deskew = cv2.UMat(np.array(_frame.get()))  #deep copy _frame ( efficient but takes more mem.)
	#COW copy method of _frame (saves mem but puts overhead + some issues)
 
	# no_deskew = cv2.UMat(no_deskew , [y1 , y2] , [x1, x2]) #.get() for some reason resets shape to screen res

	_frame = deskew_img( _frame , _ref_img , img_shape= extraArgs['frame_shape'] )

	if type(_frame) == type(-1) : #skip this frame
		return skip , skip , skip

	#continue process
	_frame = cv2.Laplacian(_frame, cv2.CV_8U, ksize=3)
	no_deskew = cv2.Laplacian(no_deskew, cv2.CV_8U, ksize=3)



	kernel    = np.ones((1,3) , dtype= np.uint8)#little bit  better for text(more horizentally focused)
	kernel2   = np.ones((3,3) , dtype= np.uint8)
	_frame 	 = cv2.dilate(_frame , kernel= kernel)
	no_deskew = cv2.dilate(no_deskew , kernel= kernel)


	img_final_deskew = _frame
	img_final_no_deskew = no_deskew
 


	if testing_mode == True : #TESTING
		print (f" UMat final imgs sizes are (not the window the img itself in gpu) ")
		temp_deskew_shape = _frame.get().shape[0] , _frame.get().shape[1]
		temp_no_deskew_shape = no_deskew.get().shape[0] , no_deskew.get().shape[1]
		print (f" not_deskewed shape : {temp_no_deskew_shape}")
		print (f" deskewed shape : {temp_deskew_shape}")
		cv2.imshow("TESTING : show image final_deskewed" , img_final_deskew)#TESTING
		cv2.imshow("TESTING : show image final_not_deskewed" , img_final_no_deskew)#TESTING


	return img_final_deskew , img_final_no_deskew , skip
 #_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#
 
 #_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#
def search_id( id_char_type : str , scanned_image : str , valid_ids_freq : dict ) -> bool :
	"""
 ---
	Returns:
		 is_valid , (some times extracted_id_val)
	"""

	id_values_type : str = id_char_type #always 'numeric' for type 0 id (default)
	scanned_image = scanned_image.split()

	if testing_mode == True :
		print ( f" {scanned_image}  {type(scanned_image)} ") #TESTING

	is_valid , extracted_id_val = False , None
	prev_obj = None
	for id_obj in scanned_image	:
    
		if testing_mode == True :
			print ( f'obj before strip and replace : {id_obj} ' )#TESTING

		#deal with small misses in ocr
		id_obj = id_obj.strip().replace(" " , "")
		id_obj = id_obj.strip().replace("," , "")
		id_obj = id_obj.strip().replace("." , "")
  
		sz = len(id_obj)
		ok_type : bool = id_obj.isnumeric()

		if testing_mode == True :
			print (f'scanned_image ibj no. : {len(scanned_image)} ')#TESTING
			print (f' id_obj: {id_obj}  is numeric? {ok_type} ') #TESTING
   
		
		if id_char_type == 'numeric' and ok_type ==  True and sz == 14 : 
			extracted_id_val = id_obj

			#NOTE: its more safer to return id found in db then make freq array 
   		# to record most accured id then thats the one
			# this makes sure  that for one second OCR will read the same right id 
			#(cuz ocr may not be accurate and generate fault id which is also present in DB not the right one)

			db_ok : bool =  db.db_check_ai_id(id_obj)
			if db_ok == True :
				is_valid = True
				if extracted_id_val in valid_ids_freq:
					valid_ids_freq[extracted_id_val] += 1
				else:
					valid_ids_freq[extracted_id_val] = 1
			else :
				continue
	
		elif id_char_type == 'numeric' and ok_type : 
     	# in some cases specially with higher good_matches tolerance and --psm 11
      # the ocr separates the id to 2 obj at most (as far as i've detected)
      # this elif is to handle this case cuz it may be a valid id after joining the 2 objects
      
			prev_obj = id_obj
			joined_numeric_conseq_obj = prev_obj + id_obj
   
			if len(joined_numeric_conseq_obj) == 14 :
				extracted_id_val = joined_numeric_conseq_obj
				is_valid = True
				if extracted_id_val in valid_ids_freq:
					valid_ids_freq[extracted_id_val] += 1
				else:
					valid_ids_freq[extracted_id_val] = 1
		else : 
			pass



	return is_valid 	, extracted_id_val
 #_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#
 
 #_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#
def read_simple_card_cuda (vid : cv2.VideoCapture , vid_specs : list , id_card_specs : dict , is_valid : bool = False) -> str :
	#gpu index to use in acceleration
	cv2.cuda.setDevice(0) 

	#vid = cv2.VideoCapture(0, cv2.CAP_CUDA)

	# Check if the camera is successfully opened
	return False if not vid.isOpened() else True
	

#use cuda functions and cuda matrices

#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#

#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#
def read_simple_card_opencl( vid : cv2.VideoCapture , vid_specs : list , id_card_specs : dict , is_valid = False  , is_valid2 = False) -> str : #NOTE: also use it when no GPU
	"""
	* Args:

		vid

		vid_specs : fps , frametime(1000 ms / fps) , vid_length_sec , active_gpu_api

		id_dimension

		is_valid
  
  ---

	* Returns:

		final_status 

		scanned_id_string

	status is 'False' when error reading frame or scan id
	"""
  
	valid_cnt , valid_cnt2 = 0 , 0
	valid_ids_freq = {}  #updated at search_id()
	valid_ids_freq2 = {} #updated at search_id()
	vid_length_sec = vid_specs[2]
	fps = vid_specs[0]
	vid_time_cnt = fps * vid_length_sec #fps * length_of_video = total number of frames
	id_dimension = id_card_specs['dimension']
	
	if testing_mode == True : #TESTING
		print(enable_multithreading(12))
	
	#needed in deskew()  (pre-allocate it 'one-time' saves huge overhead)
	ref_img = get_ref_img_db()
	ref_img = cv2.UMat(ref_img)
 
	# #4 copies moved outside loop will be used as buffer to stor org image copy UMat (may not need)
	# full_shape = (*id_dimension , 3)
	# umat_container = [np.zeros(full_shape, dtype=np.uint8)]*4
	#BTW this is only way i know to copy UMat to UMat 
	

	no_error , frame =  vid.read() #pre-allocate frame to save some overhead
	frame_shape = frame.shape[:2]
	while vid_time_cnt > 0: #start capture camera for vid_length_sec 

		if testing_mode == True :#TESTING
			start_time = time.time()
   
		no_error , frame =  vid.read()
		frame = cv2.UMat(frame)
		
		

		if  not no_error :
			print(f"""
			warninig!: could not read this frame : {vid_time_cnt} 
			skipping to next frame>> """)
			vid_time_cnt -= 1
			continue
			# return False , "Fail error reading frame" #Fetal Fail error reading frame


		img_final_deskew , img_final_no_deskew , skip = proccess_vid_frame(frame , _id_dimension= id_dimension , _is_valid = is_valid ,  _is_valid2 = is_valid2 , _ref_img = ref_img , frame_shape = frame_shape , count= vid_time_cnt )


		if type(img_final_deskew) == type( False ) or type(img_final_no_deskew) == type( False ) : #skip this frame for speed or err handle
     
			print
			(
      	f"""
			warninig!: this frame : {vid_time_cnt} will be skipped from ocr and id db check  
			due to cv2 unable to generate  homopraghy transformation mat
			"""
			)
   
			vid_time_cnt -= 1
			continue

		#custom tesser configuration if needed
		cfg  = "--psm 11 --oem 3" # Sparse text. Find as much text as possible in no particular order.
		cfg2 = "--psm 12 --oem 3" # Sparse text with osd. Find as much text as possible in no particular order.
  
		#prepare imgs for tesseract and pass them
		if testing_mode == True :
			print( f"type img_final_deskew before cvt to mat: {type(img_final_deskew)}")
			print( f"type img_final_no_deskew before cvt to mat: {type(img_final_no_deskew)}")

		img_final_deskew = img_final_deskew.get()
		img_final_no_deskew = img_final_no_deskew.get()
		imgstr  = tsr.image_to_string(img_final_deskew , lang='eng' , config= cfg)
		imgstr2 = tsr.image_to_string(img_final_no_deskew , lang='eng')
	
		#search id in rotated and non rotated images
		is_valid  , *_ = search_id ( id_card_specs['id_char'] , scanned_image= imgstr  , valid_ids_freq= valid_ids_freq) #edits valid_ids_freq inside
		is_valid2 , *_ = search_id ( id_card_specs['id_char'] , scanned_image= imgstr2 , valid_ids_freq= valid_ids_freq2) #edits valid_ids_freq inside
  
		if is_valid : valid_cnt += 1
			#render a green rectangle + must stay green for one second
		elif not is_valid: valid_cnt = 0
			#render a red rectangle
			
		if is_valid2 : valid_cnt2 += 1
			#render a green rectangle + must stay green for one second
		elif not is_valid2 : valid_cnt2 = 0
			#render a red rectangle
   
		if testing_mode == True :
			print ( 'valid counter  : ' , valid_cnt)#TESTING 
			print ( 'valid counter2 :' , valid_cnt2)#TESTING 

		vid_time_cnt -= 1
		n = 1
		validate_after = n * fps  #after n sec
  
		if valid_cnt >= validate_after :  #perfect match  if still valid for a whole n (sec)
			all_success = True
			#get only one id -> the higest freq ( if two has same freq choose the first to be inputed in freq_arr)
			final_value = max ( valid_ids_freq ,  key= valid_ids_freq.get ) 
			return all_success , final_value 

		elif valid_cnt > validate_after // 2  :
			return True , max ( valid_ids_freq ,  key= valid_ids_freq.get ) #Sucess but not perfect match

		if valid_cnt2 >= validate_after:  #perfect match  if still valid for a whole n (sec)
			all_success = True
			#get only one id -> the higest freq ( if two has same freq choose the first to be inputed in freq_arr)
			final_value = max ( valid_ids_freq2 ,  key= valid_ids_freq2.get ) 
			return all_success , final_value 

		elif valid_cnt2 > validate_after // 2  :
			return True , max ( valid_ids_freq2 ,  key= valid_ids_freq2.get ) #Sucess but not perfect match
	
		if testing_mode == True :
			print ( 'valid counter not_deskewed ' , valid_cnt)#TESTING 

		frametime = vid_specs[1]
  
		if testing_mode == True :#TESTING
			end_time = time.time()
			actual_frametime = end_time - start_time
			actual_fps = 1 / actual_frametime
			max_rec_frametime_min_fps[0] =  max (max_rec_frametime_min_fps[0] , actual_frametime)
			max_rec_frametime_min_fps[1] =  min (max_rec_frametime_min_fps[1] , actual_fps)
			min_rec_frametime_max_fps[0] =  min (max_rec_frametime_min_fps[0] , actual_frametime)
			min_rec_frametime_max_fps[1] =  max (max_rec_frametime_min_fps[1] , actual_fps)
			print(f"#### actual Frametime(sec) and FPS: {actual_frametime} , {actual_fps} ####")
			print(f"#### TARGET frametime and fps (sec) {frametime / 1000} , {fps} ####")
   
		cv2.waitKey( frametime )  
	
	max_skewed , max_un_skewed = -1 , -1
	if len(valid_ids_freq) != 0 :
		max_skewed = max ( valid_ids_freq ,  key= valid_ids_freq.get )
 
	if len(valid_ids_freq2) != 0 :
		max_un_skewed = max ( valid_ids_freq2 ,  key= valid_ids_freq2.get )
 
	return False , max(max_skewed , max_un_skewed)  #fail but return best guess
 #_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#

 #_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#

def save_ref_img_db ( name : str = "ref_rot_img"): #only use manually

	#Apply same operations that made to image before calling deskew()
	img_path = r"clear.jpg"
	path_no_ext , img_format = os.path.splitext(img_path)
	ref_img = cv2.imread(f"./{img_path}", cv2.IMREAD_GRAYSCALE)
	ref_img = cv2.bitwise_not(ref_img)
	ref_img = cv2.threshold(ref_img , 0 , 255 , cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

	#encode in bytes to compress 
	success , ref_img_encoded = cv2.imencode( ext= img_format , img= ref_img )
 
	if not success :
		print("Error : Encoding image failed in save_ref_img_db()  exiting(1)>>")
		sys.exit( 1 ) #fail and raise sys excpetion
  
	else:
		#send to db
		db.access_img_table( 1 , img_to_write= ref_img_encoded , img_name= name )
 #_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#
def get_ref_img_db(img_name : str = "ref_rot_img") -> np.ndarray :

	original = "original" #the original id card made in paint3d
	ref_img_encoded =  db.access_img_table( 0 ,img_name= img_name )
	ref_img = cv2.imdecode( np.frombuffer(ref_img_encoded , dtype= np.uint8 , ) , cv2.IMREAD_GRAYSCALE)
 
	return ref_img
 #_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#
 
 #_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#
def ocr_main (id_dimension : tuple = (450 , 316) , id_type_indx : int = 0 ) -> str : 
	"""
	* this function does following (until now):

		0. enables gpu acceleration if available (cuda or opencl)

		1. starts video capture

		2. provide rectangle at video center to help user scan id 
  			+ timer 
	
		4. proccess taken frame for better ocr ( Inverte , Threshhold , deskew , sharpen
  			dialate/erode) 

		5. ocr ( 2 frames : rotated and not rotated one)

		6. parse the text to take only id for now ( 14 numeric digits as default )

		3. apply tolerance layers  to determine either to accept read id or not 
  		(perfect match / not perfect match  / failed but send best guess)
	

		7. return the ocr(ed) ID card number

	* Default id shape is : ( 450 x 316 ) (x,y) (later this will ocr car plates and license)
		actual size of our test id card image is 400 x 266
		 id_type_inx -> default id == 0 , lisence id  == 1  , car plate id == 2

---

	 returns id_string  , True  -> if succeeded 

	 returns best_guess_ID , False   -> if Failed
	"""
	#simple ids templates
	# this is good for future if wanted to extend code to scan car plates ofقdiffز id types
	default_id_specs = {
    
    'id_type' : (0 , "default")  ,
    'id_char' : "numeric"      ,
    'id_length' : 14 ,
    'id_objects_ordered' : ["name" , "gender" , "birthDate" , "id_num" ] ,
    'dimension' : id_dimension  
    
    }
 
	lisence_specs    = {
    'id_type' : (1 , "lisence")  ,
    'id_char' : "numeric"      ,
    'id_length' : 14 ,
    'id_objects_ordered' : ["name" , "vehicle_type" ,  "id_num" ] ,
    'dimension' : id_dimension
    }
 
	car_plate_specs  = {
    'id_type' : (2 , "carPlate") ,
    'id_char' : "Alphanumeric" ,
    'id_length' : 7  ,
    'id_objects_ordered' : ["egyEng" , "egyArb"  , "nums" , "alpha"] ,
    'dimension' : id_dimension
    }
	# NOTE : car_plate length may not be always 7 , 7 is tha mx_len so find solution to that
	ids_specs = [default_id_specs , lisence_specs , car_plate_specs ]  #0 is the default id


	final_value = None 
	vid, *vid_specs = video_settings_setup(vid_length_sec= 100)
	active_gpu_api = vid_specs[3]

	if active_gpu_api == 1 : #Cuda
		if id_type_indx == 0 : #default id card
			final_status , scanned_id = read_simple_card_opencl(vid , vid_specs , ids_specs[0])
		elif id_type_indx == 1 : #TODO: lisence card
			pass
		elif id_type_indx == 2 : #TODO: car plate id
			pass
	else : #OpenCL or no Gpu
		if id_type_indx == 0 : #default id card
			final_status , scanned_id = read_simple_card_opencl(vid , vid_specs , ids_specs[0])
		elif id_type_indx == 1 : #TODO: lisence card
			pass
		elif  id_type_indx == 2 : #TODO: car plate id
			pass

	vid.release()
	cv2.destroyAllWindows()
 

	if testing_mode == True :
		print(f" highest recorded frametime  (sec) , lowest  fps  : {max_rec_frametime_min_fps}")
		print(f" lowest  recorded frametime  (sec) , highest fps  : {min_rec_frametime_max_fps}")
		print ("did we found correct id ? " , final_status)#TESTING
 
	if final_status : 
		id = scanned_id
		return id , True
	else : 
		return  scanned_id , False #FAIL but thus is best guess
#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#_#

if __name__ == "__main__": 
	#test your code 
	
	#test ocr 
	testing_mode = True
	max_rec_frametime_min_fps =  [-1 , 1000]
	min_rec_frametime_max_fps =  [10000 , -1]
	print(f" YOUR OCR FINAL OUTPUT (ID , op_status) : {ocr_main()}")
	
	#save imgs to db for first time after rebuilding db
	# save_ref_img_db (name= "ref_rot_img")
	# save_ref_img_db (name= "original")