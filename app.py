from flask import Flask, render_template, jsonify, request
app = Flask(__name__)

import requests
import jwt
import datetime
import bcrypt
from functools import wraps

from bs4 import BeautifulSoup
from bson.objectid import ObjectId
from pymongo import MongoClient

client = MongoClient('mongodb://test:test@localhost', 27017)
db = client.dbjungle

SECRET_KEY = 'YOUR_SECRET_KEY'

## HTML을 주는 부분
@app.route('/')
def home():
   return render_template('index.html')


## API 역할을 하는 부분
@app.route('/memo', methods=['GET'])
def listing():

   # DB에서 모든 데이터를 다 가져오기  (id 는 제외)
   # 1은 오름차순, -1은 내림차순
   memos = list(db.memos.find({}).sort('likes', -1))
   
   for memo in memos:
        memo['_id'] = str(memo['_id'])

   return jsonify({'result': 'success', 'memos': memos})



@app.route('/memo', methods=['POST'])
def saving():
   # 클라이언트로부터 데이터를 받기
   title = request.form.get('title')
   content = request.form.get('content')

   # 유효성 검사
   if not title or not content:
      return jsonify({'result': 'fail', 'msg': '제목과 내용을 모두 입력해주세요.'})

   # DB에 넣을 데이터 만들기
   data = {
      'title': title,
      'content': content,
      'likes': 0
   }

   # mongoDB에 데이터 넣기
   db.memos.insert_one(data)

   return jsonify({'result': 'success', 'msg':'포스팅 성공!'})



@app.route('/memo', methods=['PUT'])
def update_memo():
    id_receive = request.form.get('id')
    title_receive = request.form.get('title')
    content_receive = request.form.get('content')
    
    # 데이터베이스 업데이트 ($set 사용)
    db.memos.update_one(
        {'_id': ObjectId(id_receive)}, 
        {'$set': {'title': title_receive, 'content': content_receive}}
    )

    return jsonify({'result': 'success', 'msg': '수정완료!'})


@app.route('/memo', methods=['DELETE'])
def remove_memo():
    id_receive = request.form.get('id')

    # id 는 string 이므로 ObjectId로 형변환
    db.memos.delete_one({'_id': ObjectId(id_receive)})

    return jsonify({'result': 'success', 'msg': '삭제완료!'})


@app.route('/memo/like', methods=['PUT'])
def increment_like():
    id_receive = request.form.get('id')

    # 원자성 문제
    # $inc 연산자를 써서 값을 1 올리기
    db.memos.update_one(
        {'_id': ObjectId(id_receive)},
        {'$inc': {'likes': 1}}
    )

    return jsonify({'result': 'success', 'msg': '좋아요가 반영되었습니다'})



if __name__ == '__main__':
   app.run('0.0.0.0',port=5000,debug=True)