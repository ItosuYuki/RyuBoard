import os
from flask import Flask, render_template, request, redirect, url_for
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
    __tablename__ = 'threads'

    # 識別子
    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    # タイトル
    title = db.Column(db.String(200), nullable=False)
    # 作成日時
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    # 最終更新日時
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
    # 現行かログか
    is_active = db.Column(db.Boolean, nullable=False, default=False)


class Post(db.Model):
    # テーブル名
    __tablename__ = 'posts'

    # 識別子
    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    # 現行スレッドのid
    threads_id = db.Column(db.Integer, db.ForeignKey('threads.id'), nullable=False)
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
    logs = Thread.query.filter_by(flag=False).order_by(Thread.created_at.desc()).all()
    return render_template('pastLog.html', logs=logs)

# 現行スレッド表示
@app.route('/<int:id>')
def show_thread(id):
    # 対象データ取得
    thread = Thread.query.get(id)
    return render_template('.html', thread=thread)

# 過去ログ表示
@app.route('/PastLog/<int:id>')
def show_thread1(id): # 名前+1
    # 対象データ取得
    log = Thread.query.filter_by(id=id, flag=False).first()
    return render_template('.html', log=log)
#〜〜〜〜〜ここから投稿したフォームをデータベースに送るルーティング（漢）〜〜〜〜〜〜〜

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
        name="名無しさん",  # 投稿者名（仮）
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


@app.route('/search')
def search_threads():
    keyword = request.args.get('search', '')
    if keyword:
        threads = Thread.query.filter(Thread.title.ilike(f"%{keyword}%"),Thread.flag == False).all()
    else:
        threads = []

    return render_template('searchPastLog.html', threads=threads, keyword=keyword)
# ==================================================
# 実行
# ==================================================
if __name__ == '__main__':
    app.run()