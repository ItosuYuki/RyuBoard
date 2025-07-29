import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
#〜〜〜〜〜〜〜ここのやつらを追加（漢）〜〜〜〜〜〜〜
from flask import request, redirect, url_for
from datetime import datetime

#〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜

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
database = 'sqlite:///' + os.path.join(base_dir, 'data.sqlite')
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

    flag = db.Column(db.Boolean, nullable=False)


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
    return render_template('home.html', items=threads) #←ここcurrentThread.htmlからhome.htmlに変えた。threads=threadsからitems=threadsにしてitemsに値を渡すようにした（漢）

#〜〜〜〜〜ここから投稿したフォーム（1の本文とスレッド）をデータベースに送るルーティング（漢）〜〜〜〜〜〜〜

@app.route('/create_thread', methods=['POST'])
def create_thread():
    # フォームから送信されたデータを取得
    title = request.form['thread_title']
    content = request.form['content']
    ip_address = request.remote_addr  # ユーザーのIPアドレスを取得

    # 新しいスレッドをデータベースに追加
    new_thread = Thread(
        title=title,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        flag=True  # 初期状態ではスレッドは有効
    )
    db.session.add(new_thread)
    db.session.commit()

    # 新しい投稿をデータベースに追加
    new_post = Post(
        threads_id=new_thread.id,
        name="名無し",  # 投稿者名（仮）「名無し」に変更（漢）
        ip_address=ip_address,
        content=content,
        created_at=datetime.now(),
        parent_post_id=None  # 最初の投稿なので親IDはNone
    )
    db.session.add(new_post)
    db.session.commit()

    # スレッド一覧ページにリダイレクト
    return redirect(url_for('current_thread_list'))

#〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜


# 過去ログ一覧
@app.route('/PastLog/')
def past_log_list():
    # 作成日時が新しい順に取り出す
    logs = Log.query.order_by(Log.created_at.desc()).all()
    return render_template('pastLog.html', logs=logs)

# 現行スレッド表示
@app.route('/<int:id>')
def show_thread(id):
    # 対象データ取得
    thread = Thread.query.get(id)
    posts = Post.query.filter_by(threads_id=id).order_by(Post.created_at.asc()).all()#そのスレッドに対する投稿一覧を古い投稿から順に取り出す（漢）
    return render_template('currentThread.html', 
                           thread=thread, posts=posts, is_active=thread.flag) #htmlをcurrentThread.htmlに変えた.取り出す変数にposts（書き込まれている内容）、is_active(スレッドが過去ログか現行ログか判定する装置)を追加（漢）

#〜〜〜〜〜〜〜〜〜投稿したフォーム（レス）をデータベースに送るルーティング（漢）〜〜〜〜〜〜〜〜
@app.route('/thread/<int:thread_id>/add_post', methods=['POST'])
def add_post(thread_id):
    name = request.form.get('name', '名無し')  # 名前が未入力の場合は「名無し」
    content = request.form['content']
    ip_address = request.remote_addr  # ユーザーのIPアドレスを取得

    # 新しい投稿を作成
    new_post = Post(
        threads_id=thread_id,
        name=name,
        content=content,
        ip_address=ip_address,
        created_at=datetime.now()
    )

    # データベースに追加
    db.session.add(new_post)
    db.session.commit()

    # スレッド詳細ページにリダイレクト
    return redirect(url_for('show_thread', id=thread_id))
#〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜~

# 過去ログ表示
@app.route('/PastLog/<int:id>')
def show_thread1(id):
    # 対象データ取得
    log = Log.query.get(id)
    return render_template('.html', log=log)
# ==================================================
# 実行
# ==================================================
if __name__ == '__main__':
    app.run()