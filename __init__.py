
# coding: utf-8
import ssl
from flask import render_template, url_for
import time

#圖片辨識流程by face++
import requests
import pandas
import sqlite3 as lite
from json import JSONDecoder
#圖片辨識流程by face++

import os,shutil#資料移動相關
import random
import configparser as ConfigParser

from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError,LineBotApiError
)
from linebot.models import (
    MessageImagemapAction,ImagemapArea,URIImagemapAction,BaseSize,ImagemapSendMessage,LeaveEvent,SourceGroup,JoinEvent,SourceUser,FollowEvent,ImageCarouselColumn,ImageCarouselTemplate,CarouselColumn,CarouselTemplate,ImageMessage,MessageEvent, TextMessage, TextSendMessage,LocationMessage,FollowEvent,PostbackEvent,ImageSendMessage,FollowEvent,TemplateSendMessage,ButtonsTemplate,PostbackTemplateAction,MessageTemplateAction,URITemplateAction
)
import io
from imgurpython import ImgurClient
from PIL import Image
from setting import *

#line資訊
line_bot_api = LineBotApi(key)
handler = WebhookHandler(secret)
#imgur資訊
client = ImgurClient(client_id, client_secret, access_token, refresh_token)

app = Flask(__name__)

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    print(event.message.text)
        
    #使用者要求寫入資料庫
    av_data={'文字':[event.message.text],'時間':[time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())]}
    write=pandas.DataFrame(av_data)

    with lite.connect('av_data.sqlite') as db:
        write.to_sql('user_say',con=db,if_exists='append')
    #使用者要求寫入資料庫
        
    if event.message.text=='眾天使':
        
        with lite.connect('av_data.sqlite') as db:
            read=pandas.read_sql_query('select * from face_search',con = db)
            
        word='\n'.join(list(set(read['名子'].tolist())))
        av_amount=str(len(list(set(read['名子'].tolist()))))
        
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='目前天使庫：'+av_amount+'位\n'+word))
        
    elif event.message.text=='許願':
        
        #隨機選擇一位老婆

        three_boss=list(range(1,2+1))
        with lite.connect('av_data.sqlite') as db:
            read=pandas.read_sql_query('select * from face_search',con = db)
            select=list(set(read['名子'].tolist()))

            for item in three_boss:
                select+=['馬英九']
                select+=['蔡英文']
                select+=['柯p']

            rad=random.randint(0,len(select)-1)
            sent_name=read[read['名子']==select[rad]].iloc[0]['名子']
            sent_logo=read[read['名子']==select[rad]].iloc[0]['logo']
            if sent_logo=='':
                sent_logo='https://i.imgur.com/JrohLrx.jpg'
            
            if sent_name=='馬英九' or sent_name=='蔡英文' or sent_name=='柯p':
                set_label='你好 我是三幻神之一'
                set_title='墮天使'
                set_text='神抽'
            elif sent_name=='紗倉真菜' or sent_name=='三上悠亞' or sent_name=='高橋聖子':
                set_label='你好 我是三大神之一'
                set_title='主天使'
                set_text='神抽'
                
            elif sent_name=='光頭葛格':
                set_label='你好 我是最大雷'
                set_title='露西法'
                set_text='降臨'
            else:
                set_label='你好 我是'
                set_title='天使'
                set_text='降臨'
            
            sent_Column=CarouselColumn(
                thumbnail_image_url=sent_logo,
                title=set_title,
                text=set_text,
                actions=[
                    PostbackTemplateAction(
                        label=set_label,
                        text=' ',
                        data='action=buy&itemid=1'
                    ),
                    MessageTemplateAction(
                        label=sent_name,
                        text=' '
                    ),
                    URITemplateAction(
                        label='按這搜尋去～',
                        uri='https://www.google.com.tw/search?q='+sent_name
                    )
                ]
            )


        #隨機選擇一位老婆

        carousel_template_message = TemplateSendMessage(
            alt_text='Carousel template',
            template=CarouselTemplate(
                columns=[sent_Column
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token,carousel_template_message)
        


    elif event.message.text=='使用說明':
        print(event.message.text)
        
        #使用者要求寫入資料庫
        av_data={'文字':[event.message.text],'時間':[time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())]}
        write=pandas.DataFrame(av_data)
        
        with lite.connect('av_data.sqlite') as db:
            write.to_sql('user_say',con=db,if_exists='append')
        #使用者要求寫入資料庫
        sent_word='你好!請對我們傳送圖片~\n\n我們來幫你找你的天使w\n\n對了 你可以拍照截圖做到以下幾點 天使會更容易找到：\n１．正面臉\n２．清晰照\n３．不截到其他人頭\n\n另外 你可以\n輸入"許願"：來找尋天使'
        sent_word=TextSendMessage(text=sent_word)
        
        imagemap_message_bad = ImagemapSendMessage(
                base_url='https://i.imgur.com/AFbIhlz.jpg',
                alt_text='this is an imagemap',
                base_size=BaseSize(height=1040, width=1040),
                actions=[]
            )
        imagemap_message_good = ImagemapSendMessage(
                base_url='https://i.imgur.com/NQ869qM.jpg',
                alt_text='this is an imagemap',
                base_size=BaseSize(height=1040, width=1040),
                actions=[]
            )
        line_bot_api.reply_message(
            event.reply_token, [imagemap_message_bad,imagemap_message_good,sent_word])
        
        
    

    
    else:
        None

@handler.add(MessageEvent, message=ImageMessage)
def handle_message(event):
    
    def image_search(mode):
        #圖片儲存流程
        message_content = line_bot_api.get_message_content(event.message.id)

        with open('test.jpg', 'wb') as fd:
            for chunk in message_content.iter_content():
                fd.write(chunk)
        #圖片儲存流程


        decide=1#重複比對照片
        test=0#失敗5次以上說看不懂
        while decide:
            time.sleep(0.5)#讓程式停止一秒 避免face++伺服器當掉
            try:
                key = "B2LK45DwbvhBhz6NFcja5q4m3182NMmk"
                secret = "h3jMXHC-fc0aXdcuo_cQOQBERuICfZHA"

                #想要的face數量
                want_face=3

                #在faceset搜索
                http_url = "https://api-cn.faceplusplus.com/facepp/v3/search"

                filepath = "test.jpg"

                data = {"api_key": key, "api_secret": secret, "outer_id": mode,"return_result_count":want_face}
                files = {"image_file": open(filepath, "rb")}
                response = requests.post(http_url, data=data, files=files)

                req_con = response.content.decode('utf-8')
                req_dict = JSONDecoder().decode(req_con)
                print(req_dict)


                #與資料庫名子匹配
                with lite.connect('av_data.sqlite') as db:
                    read=pandas.read_sql_query('select * from face_search',con = db)
                ans_name=read[read["face_tokens"]==req_dict['results'][0]['face_token']].iloc[0,2]    
                ans_ps=read[read["face_tokens"]==req_dict['results'][0]['face_token']].iloc[0,5]
                ans_av_file_name=read[read["face_tokens"]==req_dict['results'][0]['face_token']].iloc[0,3]
                ans_logo=read[read["face_tokens"]==req_dict['results'][0]['face_token']].iloc[0,6]


                #與資料庫名子匹配
                with lite.connect('av_data.sqlite') as db:
                    read=pandas.read_sql_query('select * from face_search',con = db)
                ans_name2=read[read["face_tokens"]==req_dict['results'][1]['face_token']].iloc[0,2]    
                ans_ps2=read[read["face_tokens"]==req_dict['results'][1]['face_token']].iloc[0,5]
                ans_av_file_name2=read[read["face_tokens"]==req_dict['results'][1]['face_token']].iloc[0,3]
                ans_logo2=read[read["face_tokens"]==req_dict['results'][1]['face_token']].iloc[0,6]


                #與資料庫名子匹配
                with lite.connect('av_data.sqlite') as db:
                    read=pandas.read_sql_query('select * from face_search',con = db)
                ans_name3=read[read["face_tokens"]==req_dict['results'][2]['face_token']].iloc[0,2]    
                ans_ps3=read[read["face_tokens"]==req_dict['results'][2]['face_token']].iloc[0,5]
                ans_av_file_name3=read[read["face_tokens"]==req_dict['results'][2]['face_token']].iloc[0,3]
                ans_logo3=read[read["face_tokens"]==req_dict['results'][2]['face_token']].iloc[0,6]


                if ans_ps=='':
                    ans_ps='好好照顧她!知道嗎'
                if ans_ps2=='':
                    ans_ps2='好好照顧她!知道嗎'
                if ans_ps3=='':
                    ans_ps3='好好照顧她!知道嗎'
                
                #人正確或不確定都傳三人
                if 38.0<req_dict['results'][0]['confidence'] and req_dict['results'][0]['confidence']:

                    if ans_logo=='':#如果沒有logo統一用此網址
                        ans_logo='https://i.imgur.com/Vq9uNlE.jpg'
                    if ans_logo2=='':#如果沒有logo統一用此網址
                        ans_logo2='https://i.imgur.com/Vq9uNlE.jpg'
                    if ans_logo3=='':#如果沒有logo統一用此網址
                        ans_logo3='https://i.imgur.com/Vq9uNlE.jpg'

                    name_first=CarouselColumn(
                            thumbnail_image_url=ans_logo,
                            title='相似度：',
                            text=str(req_dict['results'][0]['confidence'])[0:str(req_dict['results'][0]['confidence']).find('.')]+'趴',
                            actions=[
                                PostbackTemplateAction(
                                    label='應該是',
                                    text=' ',
                                    data='action=buy&itemid=1'
                                ),
                                MessageTemplateAction(
                                    label=ans_name,
                                    text=' '
                                ),
                                URITemplateAction(
                                    label='按這搜尋去～',
                                    uri='https://www.google.com.tw/search?q='+ans_name
                                )
                            ]
                        )

                    name_second=CarouselColumn(
                            thumbnail_image_url=ans_logo2,
                            title='相似度：',
                            text=str(req_dict['results'][1]['confidence'])[0:str(req_dict['results'][1]['confidence']).find('.')]+'趴',
                            actions=[
                                PostbackTemplateAction(
                                    label='應該是',
                                    text=' ',
                                    data='action=buy&itemid=2'
                                ),
                                MessageTemplateAction(
                                    label=ans_name2,
                                    text=' '
                                ),
                                URITemplateAction(
                                    label='按這搜尋去～',
                                    uri='https://www.google.com.tw/search?q='+ans_name2
                                )
                            ]
                        )

                    name_third=CarouselColumn(
                            thumbnail_image_url=ans_logo3,
                            title='相似度：',
                            text=str(req_dict['results'][2]['confidence'])[0:str(req_dict['results'][2]['confidence']).find('.')]+'趴',
                            actions=[
                                PostbackTemplateAction(
                                    label='應該是',
                                    text=' ',
                                    data='action=buy&itemid=3'
                                ),
                                MessageTemplateAction(
                                    label=ans_name3,
                                    text=' '
                                ),
                                URITemplateAction(
                                    label='按這搜尋去～',
                                    uri='https://www.google.com.tw/search?q='+ans_name3
                                )
                            ]
                        )

                    columns=[name_first,name_second,name_third]

                    if ans_name==ans_name2:
                        columns.remove(name_second)

                    if ans_name==ans_name3:
                        columns.remove(name_third)

                    if ans_name2==ans_name3 and len(columns)==3:
                        columns.remove(name_third)

                    carousel_template_message = TemplateSendMessage(
                        alt_text='Carousel template',
                        template=CarouselTemplate(columns
                        )
                    )

                    line_bot_api.reply_message(event.reply_token,carousel_template_message)
                    #移動傳過來的檔案
                    shutil.copy2('test.jpg','av_girl_data/not_sure/'+ans_name+'_'+str(req_dict['results'][0]['confidence'])+'_'+str(time.time())+'.jpg')

                    #人臉辨識排行
                    '''
                    with lite.connect('av_data.sqlite') as db:
                        read=pandas.read_sql_query('select * from charts',con = db)

                    if sum((read['名子']==ans_name).tolist())==0:
                        av_data={'名子':[ans_name],'搜尋數':[0]}
                        write=pandas.DataFrame(av_data)
                        with lite.connect('av_data.sqlite') as db:
                            write.to_sql('charts',con=db,if_exists='append')

                    with lite.connect('av_data.sqlite') as db:
                        read=pandas.read_sql_query('select * from charts',con = db)

                    girl_number=read[read['名子']==ans_name]['搜尋數'].tolist()[0]
                    for item in sorted(read['搜尋數'].tolist()):
                        if girl_number==item:
                            girl_number=girl_number+1
                        #print(girl_number)
                    with lite.connect('av_data.sqlite') as db:
                        db.cursor().execute('UPDATE charts set 搜尋數 = "'+str(girl_number)+'" where 名子="'+ans_name+'"')
                    '''
                    #人臉辨識排行

                else:
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text='找不到像的人啊...'))

                decide=0
            except KeyError as e:
                print('filed')
                test=test+1
                if test==5:
                    print('無法解析')
                    if isinstance(event.source, SourceUser):
                        line_bot_api.reply_message(
                            event.reply_token,
                            TextSendMessage(text='找不到像的人啊...'))
                    decide=0
    
    
    if isinstance(event.source, SourceGroup):
        # print(event.source.group_id)
        # by_group_id=event.source.group_id
        # with lite.connect('av_data.sqlite') as db:
        #     read=pandas.read_sql_query('select * from select_group_id',con = db)

        # if sum(read['group_id']==by_group_id)!=0:
        #     with lite.connect('av_data.sqlite') as db:
        #         read=pandas.read_sql_query('select * from select_group_id',con = db)
        #         ps=read[read['group_id']==by_group_id].iloc[0,2].replace('\n',' ')
        #         ps=ps.replace('//','')
        #         ps=ps.replace(':','')
        #         mode=read[read['group_id']==by_group_id].iloc[0,4]
            
        #      #圖片儲存流程
        #     message_content = line_bot_api.get_message_content(event.message.id)

        #     with open('av_girl_data/Client/'+mode+'_'+ps+'_群組_'+by_group_id+'_'+time.strftime("%Y-%m-%d %H-%M-%S",time.localtime())+'.jpg', 'wb') as fd:
        #         for chunk in message_content.iter_content():
        #             fd.write(chunk)
        #     #圖片儲存流程

        #     with lite.connect('av_data.sqlite') as db:
        #         db.execute('DELETE FROM select_group_id WHERE group_id="'+by_group_id+'"')

        #     line_bot_api.reply_message(
        #         event.reply_token,
        #         TextSendMessage(text='已建立 我們將會審查您的圖片'))
        # else:
        #     if isinstance(event.source, SourceGroup):
        #         with lite.connect('av_data.sqlite') as db:
        #             read=pandas.read_sql_query('select * from KUSO_mode',con = db)
        #             if sum(read['id']==by_group_id)==0:
        #                 image_search("line_bot_av_girl")
        #             else:
        #                 image_search("line_bot_av_KUSO")
        #     elif isinstance(event.source, SourceUser):
        #         with lite.connect('av_data.sqlite') as db:
        #             read=pandas.read_sql_query('select * from KUSO_mode',con = db)
        #             if sum(read['id']==by_user_id)==0:
        #                 image_search("line_bot_av_girl")
        #             else:
        #                 image_search("line_bot_av_KUSO")
        pass

    elif isinstance(event.source, SourceUser):
        print(event.source.user_id)
        by_user_id=event.source.user_id
        
        with lite.connect('av_data.sqlite') as db:
            read=pandas.read_sql_query('select * from select_user_id',con = db)
        if sum(read['user_id']==by_user_id)!=0:
            with lite.connect('av_data.sqlite') as db:
                read=pandas.read_sql_query('select * from select_user_id',con = db)
                ps=read[read['user_id']==by_user_id].iloc[0,2].replace('\n',' ')
                ps=ps.replace('//','')
                ps=ps.replace(':','')
                mode=read[read['user_id']==by_user_id].iloc[0,4]
            
             #圖片儲存流程
            message_content = line_bot_api.get_message_content(event.message.id)

            with open('av_girl_data/Client/'+mode+'_'+ps+'_使用者_'+by_user_id+'_'+time.strftime("%Y-%m-%d %H-%M-%S",time.localtime())+'.jpg', 'wb') as fd:
                for chunk in message_content.iter_content():
                    fd.write(chunk)
            #圖片儲存流程

            with lite.connect('av_data.sqlite') as db:
                db.execute('DELETE FROM select_user_id WHERE user_id="'+by_user_id+'"')

            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text='已建立 我們將會審查您的圖片'))
        else:
            if isinstance(event.source, SourceGroup):
                with lite.connect('av_data.sqlite') as db:
                    read=pandas.read_sql_query('select * from KUSO_mode',con = db)
                    if sum(read['id']==by_group_id)==0:
                        image_search("line_bot_av_girl")
                    else:
                        image_search("line_bot_av_KUSO")
            elif isinstance(event.source, SourceUser):
                with lite.connect('av_data.sqlite') as db:
                    read=pandas.read_sql_query('select * from KUSO_mode',con = db)
                    if sum(read['id']==by_user_id)==0:
                        image_search("line_bot_av_girl")
                    else:
                        image_search("line_bot_av_KUSO")
                        
@app.route("/av_update_logo")
def av_update_logo():
    with lite.connect('av_data.sqlite') as db:
        read=pandas.read_sql_query('select * from face_search',con = db)
    with lite.connect('av_data.sqlite') as db:
        read=pandas.read_sql_query('select * from face_search',con = db) 
        av_name=list(set(read[read['logo']=='']['名子'].tolist()))  
    if av_name==[]:
        return 'logo都新增完惹~'
    else:
        return render_template('update_logo.html',av_allname=str(av_name),av_name=av_name[0],av_len=str(len(av_name)))

@app.route("/av_cut_logo", methods=['POST'])
def av_cut_logo():
    now_time=str(time.time())
    name=request.form['name']
    img =request.files['img_file']
    img.save('static/img/'+now_time+'.jpg')
    return render_template('cut_logo.html',img_name='img/'+now_time+'.jpg',name=name)

@app.route("/av_proces_logo", methods=['POST'])
def av_cut_proces():
    x1=int(request.form['x1'])
    y1=int(request.form['y1'])
    x2=int(request.form['x2'])
    y2=int(request.form['y2'])
    img_name=request.form['img_name']
    img=Image.open('static/'+img_name)
    print(img_name[4:len(img_name)-4])                 
    img = img.convert('RGB')
    img = img.crop((x1, y1, x2, y2))
    img.save("web-updata-logo-%s.jpg"%(img_name[4:len(img_name)-4]))
    ###將大小設定290###
    img=Image.open("web-updata-logo-%s.jpg"%(img_name[4:len(img_name)-4]))
    if img.size[0]>=300:
        img=img.resize( (290, 290), Image.BILINEAR )
    else:
        None#不對大小作處理
    img.save("web-updata-logo-%s.jpg"%(img_name[4:len(img_name)-4]))
    ###將大小設定290###
    ##################讀logo檔案##########################
    with lite.connect('av_data.sqlite') as db:
        read=pandas.read_sql_query('select * from face_search',con = db)
    with lite.connect('av_data.sqlite') as db:
        read=pandas.read_sql_query('select * from face_search',con = db) 
        av_name=list(set(read[read['logo']=='']['名子'].tolist()))  
    ##################讀logo檔案##########################   
    
    #####imgur上傳
    imgur_updata=client.upload_from_path("web-updata-logo-%s.jpg"%(img_name[4:len(img_name)-4]), config=None, anon=True)
    time.sleep(1)
    os.remove("web-updata-logo-%s.jpg"%(img_name[4:len(img_name)-4]))#上傳完刪除文件
    #####imgur上傳
    
    web=imgur_updata['link']
    item=request.form['name']
    with lite.connect('av_data.sqlite') as db:
        db.cursor().execute('UPDATE face_search set logo = "'+web+'" where 名子="'+item+'"')
    
    return '上傳成功\n'+imgur_updata['link']

@app.route("/av_update")
def av_update():
    return render_template('update.html')

@app.route("/av_cut", methods=['POST'])
def av_cut():
    now_time=str(time.time())
    name=request.form['name']
    img =request.files['img_file']
    img.save('static/img/'+now_time+'.jpg')
    
    return render_template('cut.html',img_name='img/'+now_time+'.jpg',name=name)

@app.route("/av_proces", methods=['POST'])
def av_proces():
    x1=int(request.form['x1'])
    y1=int(request.form['y1'])
    x2=int(request.form['x2'])
    y2=int(request.form['y2'])
    img_name=request.form['img_name']
    img=Image.open('static/'+img_name)
    print(img_name[4:len(img_name)-4])                 
    img = img.convert('RGB')
    img = img.crop((x1, y1, x2, y2))
    img.save("web-updata-%s.jpg"%(img_name[4:len(img_name)-4]))
    update_faceset_name='line_bot_av_girl'
############################開始上傳圖片##########################
    cli_name=request.form['name']
    cli_av_file_name="web-updata-%s"%(img_name[4:len(img_name)-4])
    
    ##初始化
    name=[cli_name]#人物名子
    ps=['']#人物附註
    av_file_name=cli_av_file_name+'.jpg'#人物檔名 一定要羅馬拼音
    ##初始化

    #######################將圖片上傳製作facetoken############################
    #在faceset裡面新增臉
    print('--facetoken製作')
    http_url = "https://api-cn.faceplusplus.com/facepp/v3/detect"

    decide=1#try跳開
    count=0#失敗計數數量
    while decide:
        time.sleep(1)
        try:
            data = {"api_key": key, "api_secret": secret}
            files = {"image_file": open(av_file_name, "rb")}
            response = requests.post(http_url, data=data, files=files)

            req_con = response.content.decode('utf-8')
            req_dict_facetoken = JSONDecoder().decode(req_con)

            face_token=[req_dict_facetoken['faces'][0]['face_token']]

            print('確認'+req_dict_facetoken['faces'][0]['face_token'])
            print('人臉數量'+str(len(req_dict_facetoken['faces'])))
            decide=0
            print('--成功')
        except KeyError as e3:
            count=count+1
            print('上傳失敗')
            if count==8:
                print('--上傳錯誤')
                decide=0
                while True:
                    None
    files['image_file'].close()
    ########################將圖片上傳製作facetoken############################       
    if len(req_dict_facetoken['faces'])==1:#判斷圖片是否只有一人
        #在faceset裡面新增臉
        print('--facetoken上傳')
        http_url = "https://api-cn.faceplusplus.com/facepp/v3/faceset/addface"

        decide=1#try跳開
        count=0#失敗計數數量
        while decide:
            time.sleep(1)
            try:
                data = {"api_key": key, "api_secret": secret, "outer_id": update_faceset_name,"face_tokens":face_token[0]}

                print('確認'+face_token[0])

                response = requests.post(http_url, data=data)

                req_con = response.content.decode('utf-8')
                req_dict = JSONDecoder().decode(req_con)

                web_face_count=str(eval(response.text)["face_count"])

                decide=0
                print('--成功')
            except KeyError as e3:
                count=count+1
                print('失敗上傳')
                if count==8:
                    print('--上傳錯誤')
                    decide=0
                    while True:
                        None

    #建立女優資料##################################
        #製作女優資料夾
        print('--女優資料製作')
        try:
            os.mkdir('av_girl_data/'+name[0])
        except FileExistsError as e:
            None
        #製作女優資料夾

        #製作女優圖片檔名排序
        dir_file=os.listdir('av_girl_data/'+name[0])
        file_name=[]
        for item in dir_file:
            file_name+=[int(item[item.find('_')+1:item.find('.jpg')])]
        if file_name==[]:
            file_name=[0]
        #製作女優圖片檔名排序

        #移動圖片
        file_end='av_girl_data/'+name[0]+'/'+av_file_name[0:av_file_name.find('.jpg')]+'_'+str(max(file_name)+1)+'.jpg'
        shutil.move(av_file_name,file_end)
        #移動圖片

        #紀錄資料庫程序
        pinyin=[av_file_name[0:av_file_name.find('.jpg')]]

        #logo檢查程序 如果有就增加 沒有就空白
        with lite.connect('av_data.sqlite') as db:
            read=pandas.read_sql_query('select * from face_search',con = db)
            if sum(read["名子"]==name[0])!=0:
                logo=read[read["名子"]==name[0]].iloc[0,6]
            else:
                logo=''
        #logo檢查程序 如果有就增加 沒有就空白

        av_data={'名子':name,'羅馬拼音':pinyin,'face_tokens':face_token,'附註':ps,'檔名':[av_file_name[0:av_file_name.find('.jpg')]+'_'+str(max(file_name)+1)+'.jpg'],'logo':[logo]}
        write=pandas.DataFrame(av_data)
        #紀錄資料庫程序

        #寫入資料程序(成功上傳再寫入)
        with lite.connect('av_data.sqlite') as db:
            write.to_sql('face_search',con=db,if_exists='append')

        with lite.connect('av_data.sqlite') as db:
            read=pandas.read_sql_query('select * from face_search',con = db)
            print('網路人臉數量:'+web_face_count)
            print('伺服器人臉數量:'+str(len(read['檔名'].tolist())))
        print('--成功'+file_end+'\n\n')
    #建立女優資料##################################
        return '上傳成功'
    else:
        #電腦告知錯誤人數
        print('圖片人數不是一人')
        os.remove(av_file_name)
        print('--已刪除\n')
        return '上傳失敗'
############################開始上傳圖片##########################
    
if __name__ == "__main__":
    '''
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)    
    context.load_verify_locations("ssl/ca_bundle.crt")
    context.load_cert_chain("ssl/certificate.crt", "ssl/private.key")

    app.run(host='0.0.0.0',port=443,ssl_context=context, threaded=True)
    '''
    app.run(host='0.0.0.0', port=5000, debug=True)

