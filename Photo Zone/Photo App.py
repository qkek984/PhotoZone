# -*- coding:utf-8 -*-
from flask import Flask, render_template, Response, request,send_file
from picamera import PiCamera
from picamera.array import PiRGBArray
import io
import threading
from threading import Lock
import cv2
import numpy as np
import os,pickle, signal,time

##E-mail##
import smtplib
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.base import MIMEBase
##
global frame, count_text
frame=""
count_text=""
WIDTH=800
HEIGHT=600
camera = PiCamera()
camera.resolution = (WIDTH, HEIGHT)
stream = PiRGBArray(camera, size=(WIDTH, HEIGHT))
camera.framerate = 40
camera.brightness = 53
app = Flask(__name__)
##

def e_mail(to_email):
    smtp = smtplib.SMTP('smtp.naver.com', 587)
    smtp.ehlo()      # say Hello
    smtp.starttls()  # TLS 사용시 필요
    smtp.login('qkek984@naver.com', 'dkagh752')

    msg = MIMEBase("multipart","mixed")
    msg['Subject'] = '낙산공원에서의 소중한 추억사진입니다.' 
    msg['To'] = to_email
    msg['From'] = '낙산공원 포토존'
    
    files = 'data/capture.jpg'
    imageFD=open(files,'rb')
    imagePart=MIMEImage(imageFD.read())
    imageFD.close()
    
    files2 = 'data/coupon.jpg'
    imageFD2=open(files2,'rb')
    imagePart2=MIMEImage(imageFD2.read())
    imageFD2.close()

    msg.attach(imagePart)
    msg.add_header('Content-Disposition','attachment',filename=files)
    msg.attach(imagePart2)
    msg.add_header('Content-Disposition','attachment',filename=files2)
    smtp.sendmail('qkek984@naver.com', to_email, msg.as_string())
    smtp.quit()

global pp
pp = os.getpid()
lck=Lock()
class count(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.num = 5
    def run(self):
        global count_text
        for i in range(0,5):
            count_text = self.num
            self.num=self.num-1
            time.sleep(1)
        count_text=""
        while self.num<3:
            time.sleep(0.05)
            camera.brightness = 80+(self.num*5)
            self.num=self.num+1
        camera.brightness = 53
    
def signal_handler(signum,frame):
    global s1
    t=count()
    t.start()
    print "global:",s1
signal.signal(signal.SIGUSR1,signal_handler)

@app.route('/capture')
def capture():
    #camera.capture('data/capture.jpg')
    cv2.imwrite('data/capture.jpg', frame)
    return send_file('data/capture.jpg')

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/config')
def config():
    global pp,s1
    s1 = request.args.get('capture','')
    os.kill(pp,signal.SIGUSR1)

@app.route('/emailserver')
def emailserver():
    global pp,s1
    s2 = request.args.get('email','')
    print s2
    e_mail(s2)
    #os.kill(pp,signal.SIGUSR1)
    
def gen():
    global frame,count_text
    x=int(WIDTH*0.48)
    y=int(HEIGHT*0.6)
    while True:
        camera.capture(stream,'bgr',use_video_port=True)
        stream.seek(0)
        frame=stream.array
        
        cv2.putText(frame, str(count_text),(x-5,y-5),cv2.FONT_HERSHEY_SIMPLEX,4,(0,0,0),10)
        cv2.putText(frame, str(count_text),(x,y),cv2.FONT_HERSHEY_SIMPLEX,4,(255,255,255),10)
        cv2.putText(frame, str(count_text),(x,y),cv2.FONT_HERSHEY_SIMPLEX,4,(250,150,50),5)
        cv2.putText(frame, str(count_text),(x,y),cv2.FONT_HERSHEY_SIMPLEX,4,(250,200,50),2)
        cv2.imwrite('data/f.jpg', frame)
        yield (b'--frame\r\n'
                   b'Content-Type: frame/jpeg\r\n\r\n' + open('data/f.jpg', 'rb').read() + b'\r\n')

        stream.truncate(0)
        
    '''
    global frame
    for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        frame= frame.array
        frame = cv2.resize(frame,None,fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
        
        cv2.imwrite('data/f.jpg', frame)
        yield (b'--frame\r\n'
                   b'Content-Type: frame/jpeg\r\n\r\n' + open('data/f.jpg', 'rb').read() + b'\r\n')
        rawCapture.truncate(0)
    '''
        
@app.route('/video_feed')
def video_feed():
    return Response(gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, threaded=True)
