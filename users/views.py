from django.shortcuts import render, HttpResponse
from .forms import UserRegistrationForm
from .models import UserRegistrationModel,UserImagePredictinModel
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from .utility.GetImageStressDetection import ImageExpressionDetect
from .utility.MyClassifier import KNNclassifier
from subprocess import Popen, PIPE
import subprocess
# Create your views here.
import cv2
import os
import vlc
global emoname

# Create your views here.
def UserRegisterActions(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            print('Data is Valid')
            form.save()
            messages.success(request, 'You have been successfully registered')
            form = UserRegistrationForm()
            return render(request, 'UserRegistrations.html', {'form': form})
        else:
            messages.success(request, 'Email or Mobile Already Existed')
            print("Invalid form")
    else:
        form = UserRegistrationForm()
    return render(request, 'UserRegistrations.html', {'form': form})


def UserLoginCheck(request):
    if request.method == "POST":
        loginid = request.POST.get('loginname')
        pswd = request.POST.get('pswd')
        print("Login ID = ", loginid, ' Password = ', pswd)
        try:
            check = UserRegistrationModel.objects.get(loginid=loginid, password=pswd)
            status = check.status
            print('Status is = ', status)
            if status == "activated":
                request.session['id'] = check.id
                request.session['loggeduser'] = check.name
                request.session['loginid'] = loginid
                request.session['email'] = check.email
                print("User id At", check.id, status)
                return render(request, 'users/UserHome.html', {})
            else:
                messages.success(request, 'Your Account Not at activated')
                return render(request, 'UserLogin.html')
        except Exception as e:
            print('Exception is ', str(e))
            pass
        messages.success(request, 'Invalid Login id and password')
    return render(request, 'UserLogin.html', {})


def UserHome(request):
    return render(request, 'users/UserHome.html', {})

def UploadImageForm(request):
    loginid = request.session['loginid']
    data = UserImagePredictinModel.objects.filter(loginid=loginid)
    return render(request, 'users/UserImageUploadForm.html', {'data': data})

def UploadImageAction(request):
    image_file = request.FILES['file']

    # let's check if it is a csv file
    if not image_file.name.endswith('.jpg'):
        messages.error(request, 'THIS IS NOT A JPG  FILE')

    fs = FileSystemStorage()
    filename = fs.save(image_file.name, image_file)
    # detect_filename = fs.save(image_file.name, image_file)
    uploaded_file_url = fs.url(filename)
    obj = ImageExpressionDetect()
    emotion = obj.getExpression(filename)
    username = request.session['loggeduser']
    loginid = request.session['loginid']
    email = request.session['email']
    UserImagePredictinModel.objects.create(username=username,email=email,loginid=loginid,filename=filename,emotions=emotion,file=uploaded_file_url)
    data = UserImagePredictinModel.objects.filter(loginid=loginid)
    return render(request, 'users/UserImageUploadForm.html', {'data':data})

def UserEmotionsDetect(request):
    if request.method=='GET':
        imgname = request.GET.get('imgname')
        print(imgname)
        obj = ImageExpressionDetect()
        emotion = obj.getExpression(imgname)
        loginid = request.session['loginid']
        data = UserImagePredictinModel.objects.filter(loginid=loginid)
        return render(request, 'users/UserImageUploadForm.html', {'data': data})

def UserLiveCameDetect(request):
    obj = ImageExpressionDetect()
    obj.getLiveDetect()
    return render(request, 'users/UserLiveHome.html', {})

def UserKerasModel(request):
    if request.method=='GET':
        # p = Popen(["python", "kerasmodel.py --mode display"], cwd='StressDetection', stdout=PIPE, stderr=PIPE)
        # out, err = p.communicate()
        subprocess.call("python kerasmodel.py --mode display")
        loginid = request.session['loginid']
        data = UserImagePredictinModel.objects.filter(loginid=loginid)
        return render(request, 'users/UserImageUploadForm.html', {'data': data})
def stop(request):
    # p = Popen(["python", "kerasmodel.py --mode display"], cwd='StressDetection', stdout=PIPE, stderr=PIPE)
    # out, err = p.communicate()
    subprocess.call("python restart_django.py --mode display")
    return render(request, 'users/UserLiveHome.html', {})


def Capture(request):
    

    # Initialize the camera
    cap = cv2.VideoCapture(0)
    # Set the number of images to capture
    num_images = 15
    # Initialize a counter
    count = 0
    name="main"
    while count < num_images:
        # Read the frame from the camera
        ret, frame = cap.read()
        # Check if the frame was successfully read
        if not ret:
            break
        if count>10:
            path = 'C:/Users/user/Desktop/Emotion Recommendation/media'
            # cv2.imwrite(os.path.join(path , 'waka.jpg'), img)
            # Save the frame as an image file
            cv2.imwrite(os.path.join(path,f"{name}_{count}.jpg"), frame)
        # Increase the counter
        count += 1

        # Display the frame (optional)
        cv2.imshow("Frame", frame)

        # Break the loop if the 'q' key is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the camera and destroy all windows
    cap.release()
    cv2.destroyAllWindows()
    loginid = request.session['loginid']
    data = UserImagePredictinModel.objects.filter(loginid=loginid)
    return render(request, 'users/UserImageUploadForm.html', {'data': data})
def Reccommend_Movie(request):
    if request.method=='GET':
        global emoname
        emoname = request.GET.get('emoname')
        
        a=emoname.lower()   
        mainn = a + ".mp4"
        print(mainn)     
        # create a VLC instance
        player = vlc.Instance()

        # create a media object
        path='C:/Users/user/Desktop/Emotion Recommendation/movies/'
        # 
        main=os.path.join(path,f"{mainn}")
        print(main)
        print("****************")
        media = player.media_new(main)
        # create a media player object
        player = player.media_player_new()

        # set the media object for the media player
        player.set_media(media)

        # play the mediat
        player.play()
        loginid = request.session['loginid']
        data = UserImagePredictinModel.objects.filter(loginid=loginid)
        return render(request, 'users/UserImageUploadForm.html', {'data': data})
# def stop(request):
#     if request.method=='GET':
#         player = vlc.Instance()
#         global emoname
#         a=emoname.lower()   
#         mainn = a + ".mp4"
#         path='D:/AVRP/mallareddy/16 Stress Detection in IT Professionals/Code/Emotion Recommendation/'
#         # 
#         main=os.path.join(path,f"{mainn}")
#         media = player.media_new(main)
#         player = player.media_player_new()
#         player.set_media(media)
#         player.stop()
#         loginid = request.session['loginid']
#         data = UserImagePredictinModel.objects.filter(loginid=loginid)
#         return render(request, 'users/UserImageUploadForm.html', {'data': data})

def UserKnnResults(request):
    obj = KNNclassifier()
    df,accuracy,classificationerror,sensitivity,Specificity,fsp,precision = obj.getKnnResults()
    df.rename(columns={'Target': 'Target', 'ECG(mV)': 'Time pressure', 'EMG(mV)': 'Interruption', 'Foot GSR(mV)': 'Stress', 'Hand GSR(mV)': 'Physical Demand', 'HR(bpm)': 'Performance', 'RESP(mV)': 'Frustration', }, inplace=True)
    data = df.to_html()
    return render(request,'users/UserKnnResults.html',{'data':data,'accuracy':accuracy,'classificationerror':classificationerror,
                                                       'sensitivity':sensitivity,"Specificity":Specificity,'fsp':fsp,'precision':precision})
