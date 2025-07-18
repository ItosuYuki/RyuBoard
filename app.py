import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime

# ==================================================
# インスタンス生成
# ==================================================
app = Flask(__name__)

# ==================================================
# Flaskに対する設定
# ==================================================
# 乱数を設定
app.config['SECRET_KEY'] = os.urandom(24)
base_dir = os.path.dirname(__file__)
database = 'sqlite:///' + os.path.join(base_dir, 'CurrentThreads.sqlite')
app.config['SQLALCHEMY_DATABASE_URI'] = database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# ★db変数を使用してSQLAlchemyを操作できる
db = SQLAlchemy(app)
# ★「flask_migrate」を使用できる様にする
Migrate(app, db)

#==================================================
# モデル
#==================================================
# 現行スレッド
class Thread(db.Model):
    # テーブル名
    __tablename__ = 'current_threads'

    # 識別子
    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    # タイトル
    title = db.Column(db.String(200), nullable=False)
    # 作成日時
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    # 最終更新日時
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
#　過去ログ
class Log(db.Model):
    # テーブル名
    __tablename__ = 'past_logs'

    # 識別子
    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    # 現行スレッドのid
    threads_id = db.Column(db.Integer, db.ForeignKey('current_threads.id'), nullable=False)
    # タイトル
    title = db.Column(db.String(200), nullable=False)
    # 作成日時
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

class Post(db.Model):
    # テーブル名
    __tablename__ = 'posts'

    # 識別子
    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    # 現行スレッドのid
    threads_id = db.Column(db.Integer, db.ForeignKey('current_threads.id'), nullable=False)
    # 名前
    name = db.Column(db.String(200))
    # ipアドレス
    ip_address = db.Column(db.String(200), nullable=False)
    # 投稿内容
    content = db.Column(db.String(200), nullable=False)
    # 作成日時
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    # 返信先のid
    parent_post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))

# ==================================================
# ルーティング
# ==================================================
# 現行スレッド一覧
@app.route('/')
def current_thread_list():
    # 最終更新日時が新しい順に取り出す
    threads = Thread.query.order_by(Thread.updated_at.desc()).all()
    return render_template('currentThread.html', threads=threads)

# 過去ログ一覧
@app.route('/PastLog/')
def past_log_list():
    # 作成日時が新しい順に取り出す
    logs = Log.query.order_by(Log.created_at.desc()).all()
    return render_template('pastLog.html', logs=logs)
# ==================================================
# 実行
# ==================================================
if __name__ == '__main__':
    app.run()