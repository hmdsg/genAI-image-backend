from flask import Flask
from flask import render_template, request, jsonify
from flask_cors import CORS
import os
import time
import json
import ast

from vertexai.preview.vision_models import ImageCaptioningModel
from vertexai.preview.vision_models import Image
from vertexai.preview.language_models import TextGenerationModel

image_captioning_model = ImageCaptioningModel.from_pretrained('imagetext@001')
generation_model = TextGenerationModel.from_pretrained('text-bison@001')


app = Flask(__name__)
CORS(app)


def get_image_caption(filename):
    path = f"static/image/{filename}"
    image = Image.load_from_file(path)
    results = image_captioning_model.get_captions(
        image=image,
        number_of_results=3)
    results.sort(key=len)
    return results[-1]

def get_description_message(caption,lang):
    prompt = f"""
        広告アドバイザーの立場で、購入者に向けた以下の商品の表題に対する魅力的な商品の紹介文を作成してください。
        回答は回答の言語に従ってください。


        商品の表題：{caption}
        回答の言語：{lang}
        """
    answer = generation_model.predict(prompt,temperature=0.2, max_output_tokens=1024,top_k=40, top_p=0.8).text
    return answer 

def get_filename():
    name = int(time.time())
    return str(name) + ".png"

def get_option_for_caption(caption,lang):
    prompt = f"""
        As an advertising advisor, you will create attractive product introductions for the following product titles aimed at buyers.
        For the product title below, please suggest two types of parameters and three types of parameter options for classifying customers when creating a product introduction.
        Please include "Not set" in the parameter options. Answers should be in json format.
        Please follow the language of the answer when answering.

        example：
        Product title: ：Cutting-edge laptop
        Example answer:{{'Usage scene':['Work','Private','Not set'], 'Price':['Cheap','Expensive','Not set']}}

        example:
        Product title: White T-shirt with brand logo
        Example answers:{{'Target age':['For children','For adults','Not set'], 'Material':['Luxurious','Highly functional','Not set' ]}}

        Product title：{caption}
        Answer language:{lang}
        """

    answer = generation_model.predict(prompt,temperature=0.2, max_output_tokens=1024,top_k=40, top_p=0.8).text

    return ast.literal_eval(answer)

def get_adv_description_message(caption,lang,option1_title, option1_value, option2_title, option2_value):

    option1_key = option.keys()[0]
    option2_key = option.keys()[1]


    prompt = f"""
　　　　　As an advertising advisor, please create an attractive product introduction for the following product titles for buyers.
        Be sure to include the title of the element that describes the product in more detail and the value of the element that describes the product in more detail.
        Please follow the language of the answer when answering.

        Product title: {caption}
        Title of element 1 to describe the product in more detail: {option1_title}
        Value of element 1 to describe the product in more detail: {option1_value}
        Element 2 title to describe the product in more detail: {option2_title}
        Value of element 2 to describe the product in more detail: {option2_value}
        Answer language: {lang}
        """
    answer = generation_model.predict(prompt,temperature=0.2, max_output_tokens=1024,top_k=40, top_p=0.8).text
    return answer 

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':

    # upfileはcurlの場合
    # flutteもupfileにした
    # curl -X POST -F upfile=@/Users/shogohamada/github/genAI-image-backend/testenv/snowboard.png http://127.0.0.1:5000/upload

    # if 'upfile' not in request.files:
    #         return 'NO FILE'

        file = request.files['upfile']
        filename = get_filename()
        file.save(os.path.join('./static/image', filename))

        caption = get_image_caption(filename)

        #delete
        os.remove(f'./static/image/{filename}')

        return caption
    else:
        return 'NG'


@app.route('/option', methods=['GET', 'POST'])
def get_option():
    if request.method == 'POST':

        #caption取得
        caption = request.json["imageCaption"]
        lang = request.json["lang"]


        #optionを返す
        option = get_option_for_caption(caption,lang)
    
        return option
    else:
        return 'NG'


@app.route('/description', methods=['GET', 'POST'])
def get_description():
    # print (request.headers)
    # print (request.headers['Content-Type'])
    # application/json; charset=utf-8　が返ってくるらしい
    # if request.headers['Content-Type'] != 'application/json':
    #     print(request.headers['Content-Type'])
    #     return "NG"

    caption = request.json["imageCaption"]
    lang = request.json["lang"]


    description = get_description_message(caption,lang)

    return description

@app.route('/advdescription', methods=['GET', 'POST'])
def get_advdescription():
    # print (request.headers)
    # print (request.headers['Content-Type'])
    # application/json; charset=utf-8　が返ってくるらしい
    # if request.headers['Content-Type'] != 'application/json':
    #     print(request.headers['Content-Type'])
    #     return "NG"

    caption = request.json["imageCaption"]
    lang = request.json["lang"]
    
    option1_title = request.json["option1_title"]
    option1_value = request.json["option1_value"]
    option2_title = request.json["option2_title"]
    option2_value = request.json["option2_value"]

    description = get_adv_description_message(caption,lang, option1_title, option1_value, option2_title, option2_value)

    return description


@app.route('/health', methods=['GET', 'POST'])
def health_check():
    return jsonify({'message': 'ok'}), 200

@app.route('/captiontest', methods=['GET', 'POST'])
def caption_test():
    filename = "snowboard.png"
    return get_image_caption(filename)
 


if __name__ == '__main__':
  app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))