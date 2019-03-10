from flask import Flask, request
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw 

app = Flask(__name__)

@app.route("/info", methods=['POST'])
def info():
    req = request.get_json()
    img = Image.open("res/info.jpg")
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("res/msjh.ttc", 120)
    draw.text((0, 100),req["text"],(247,186,205),font=font)
    img.save('res/info_process.jpg')
    return "ok"

if __name__ == "__main__":
    app.run()