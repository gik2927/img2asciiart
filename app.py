import os
from flask import Flask, request, render_template, redirect, url_for
from werkzeug.utils import secure_filename
from ascii_magic import AsciiArt
from PIL import Image, ImageEnhance

# --- 설정 ---
UPLOAD_FOLDER = 'uploads'
STATIC_FOLDER = 'static'
ALLOWED_EXTENSIONS = {'png', 'jpg'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(STATIC_FOLDER, exist_ok=True)
# -------

#---확장자 검사---  
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
# ------

@app.route('/', methods=['GET', 'POST'])
def upload_and_convert():
    if request.method == 'POST':
        if 'image' not in request.files:
            return redirect(request.url)
        
        file = request.files['image']

        if file.filename == '':
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            try:
                # 이미지 밝기 조절
                img = Image.open(filepath)
                enhancer = ImageEnhance.Brightness(img)
                img_brightened = enhancer.enhance(1.05) 
                
                # 밝기 조절된 이미지를 임시로 저장
                temp_filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"bright_{filename}")
                img_brightened.save(temp_filepath)
                
                # ASCII 아트 생성
                my_art = AsciiArt.from_image(temp_filepath)
                
                # ASCII HTML 파일 생성
                ascii_filename = "ascii_art.html"
                ascii_path = os.path.join(STATIC_FOLDER, ascii_filename)
                
                my_art.to_html_file(
                    ascii_path, 
                    columns=180, 
                    width_ratio=2
                )
                
                os.remove(temp_filepath)
                
                # result.html에 iframe으로 삽입
                ascii_url = url_for('static', filename=ascii_filename)
                return render_template('result.html', ascii_url=ascii_url)

            except Exception as e:
                return f"<p>이미지 변환 중 오류 발생: {e}</p>"

    # GET 요청 시 업로드 페이지 표시
    return render_template('index.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000,debug=True)