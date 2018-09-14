# -*- coding:utf-8 -*-
 
import smtplib
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.base import MIMEBase
 
smtp = smtplib.SMTP('smtp.naver.com', 587)
smtp.ehlo()      # say Hello
smtp.starttls()  # TLS 사용시 필요
smtp.login('qkek984@naver.com', '*****')

files = 'data/capture.jpg'


msg = MIMEBase("multipart","mixed")
msg['Subject'] = '낙산공원에서의 소중한 추억사진입니다.' 
msg['To'] = 'qkek984@naver.com'
msg['From'] = '낙산공원 포토존'

imageFD=open(files,'rb')
imagePart=MIMEImage(imageFD.read())
imageFD.close()

msg.attach(imagePart)

msg.add_header('Content-Disposition','attachment',filename=files)

smtp.sendmail('qkek984@naver.com', 'qkek984@naver.com', msg.as_string())
 
smtp.quit()
