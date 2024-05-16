import random
import praw
from praw.models import MoreComments
import pyttsx3
from moviepy.editor import VideoFileClip, concatenate_videoclips, vfx, AudioFileClip, ImageClip, CompositeVideoClip
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
import requests



def genData():
    data = {
        "title": "",
        "comment": [],
        "postid": "",
        "posturl": "",
        "titleImg": ""
    }
    js_code = "arguments[0].scrollIntoView();"
    print("------------------------------------------------")
    print("\tGenAudio Status : Process 🔃")
    print("------------------------------------------------\n")
    reddit = praw.Reddit(
        client_id="o5ES7gv0t6ENbo0Xr8vlXQ",
        client_secret="ZgzXtBrRjTLeLo-FtuoJm9WP_cp9bg",
        user_agent="Bot by u/ujjwalti",
        username="ujjwalti",
        password="ujjwal70815",
    )

    subreddit = reddit.subreddit("AskReddit").top(limit=1, time_filter="day")
    post = 0
    for s in subreddit:
        post = s
        data["title"] = s.title
        data["postid"] = s.id
        data["posturl"] = s.url

    print("Title => ", post.title)
    print("Id => ", post.id)
    print("Url => ", post.url)
    print("\n")

    driver = webdriver.Chrome()
    driver.maximize_window()
    driver.get(post.url + "/?sort=confidence")
    # driver.get(post.url + "/?sort=top")
    actions =  ActionChains(driver);

    driver.execute_script("""
       var l = document.getElementsByTagName("header")[0];
       l.parentNode.removeChild(l);
    """)

    titleImgSS = driver.find_element(By.TAG_NAME, "shreddit-post")
    # driver.execute_script(js_code, titleImgSS)
    titleImgSS.screenshot("./asset/ss/title.png")


    data["titleImg"] = "./asset/ss/title.png"

    c = reddit.submission(url=post.url)
    c.comment_sort = "confidence"
    # c.comment_sort = "top"
    c.comment_limit = 3

    i = 0
    for cc in c.comments:
        id = f"t1_{cc.id}"
        tempcomment = driver.find_element(By.CSS_SELECTOR, f'[thingid="{id}"]')
        driver.execute_script(js_code, tempcomment)

        actions.move_to_element(tempcomment).pause(10)
        tempcomment.screenshot(f"asset/ss/comment{i}.png")
        if isinstance(cc, MoreComments):
            continue
        if len(cc.body) > 120:
            data["comment"] = [{"body": cc.body, "cid": id, "imgLocation": f"asset/ss/comment{i}.png"}]
            break
        else:
            data["comment"] = data["comment"] + [
                {"body": cc.body, "cid": id, "imgLocation": f"asset/ss/comment{i}.png"}]
        i += 1

    return data


engine = pyttsx3.init(driverName='sapi5')
rate = engine.getProperty('rate')
engine.setProperty('rate', (rate - 15))


def genVideo():
    print("------------------------------------------------")
    print("\tGen Video Status : Processing 🔃")
    print("------------------------------------------------\n")

    data = genData()

    titleClip = createClip(data["titleImg"], "\t\nSomeone one reddit asked \n" + data["title"], "title")
    clips = []
    clips.append(titleClip)

    i = 0
    for i,c in enumerate(data["comment"]):
        # print(c)
        res = ""
        if i != len(data["comment"]) - 1:
            res = "\nRepiled : \n\n " + c["body"] + "\n\n\n\t\t Nigga if u liked this do follow and we good niigga"
        else:
            res = "\nRepiled : \n\n " + c["body"]
        vClipc = createClip(img=c["imgLocation"], text=res, fileName=f"comment{i}")
        clips.append(vClipc)
        i += 1
    i = 0
    # print(clips)

    titleandCommentClip = concatenate_videoclips(clips).set_position("center")

    # To clip from raw video of gameplay
    rawT = int(random.random() * 700)
    starttime = convertSec(rawT)
    endtime = (starttime + round(titleandCommentClip.duration))

    bgClip = VideoFileClip("./asset/vid/rawm.mp4").subclip(starttime, endtime).fx(vfx.fadein, 1).fx(vfx.fadeout, 1)

    finalVideo = CompositeVideoClip(clips=[bgClip, titleandCommentClip])
    outputFile = './asset/outputClip.mp4'
    finalVideo.write_videofile(outputFile)
    # finalVideo.write_videofile(outputFile, codec="mpeg4", threads=12, bitrate="8000k")

    # print(data)

    print("------------------------------------------------")
    print("\tGenAudio Status : Sucessful ✅")
    print("------------------------------------------------\n")

    print("-----------------------------------")
    print("Uploading to telegram ")
    print("-----------------------------------")

    TOKEN = "6795099200:AAHKXtAb2ZE5VwCBwC38GPa8KjIwM1f2sh8"
    chatid = "-4226147032"
    f = open('./asset/outputClip.mp4', 'rb')

    APP_Url = f"https://api.telegram.org/bot{TOKEN}/sendVideo?chat_id={chatid}"
    file_byte = f.read()
    f.close()
    response = {
        'document': (f.name, file_byte)
    }

    res = requests.post(url=APP_Url, files={"video": response['document']})
    print(res.status_code)

    print("----------------------------------------------------------")
    print("\t Upload Complete ✅")
    print("----------------------------------------------------------")


def progress(percent):
  print(percent)

def genAudio(a, fileName):
    engine.save_to_file(a, f'./asset/audio/{fileName}.wav')
    engine.runAndWait()
    return AudioFileClip(f"./asset/audio/{fileName}.wav")


def createClip(img, text, fileName):
    audioclip = genAudio(text, fileName)
    imgclip = ImageClip(img).set_duration(audioclip.duration)
    imgclip = imgclip.set_position("center").resize(width=(1080 - 200))
    videoclip = imgclip.set_audio(audioclip)
    videoclip.fps = 1
    return videoclip


def convertSec(n):
    return int((n * 60) / 100)



if __name__ == '__main__':
    genVideo()


