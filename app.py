from flask import Flask, render_template, request
import os
import zipfile
import shutil

app = Flask(__name__)


# Nhận diện framework
def check_framework(files):
    code = ""

    for file in files:
        if file.endswith(".py"):
            try:
                with open(file, "r", encoding="utf-8") as f:
                    code += f.read()
            except:
                pass

    code = code.lower()

    if "streamlit" in code:
        return "Streamlit"
    elif "flask" in code:
        return "Flask"
    elif "fastapi" in code:
        return "FastAPI"
    elif "gradio" in code:
        return "Gradio"
    else:
        return "Python thường"


# Kiểm tra requirements.txt
def check_requirements(files):
    for file in files:
        if os.path.basename(file) == "requirements.txt":
            return True

    return False


# Kiểm tra .env
def check_env(files):
    for file in files:
        if os.path.basename(file) == ".env":
            return True

    return False


# Kiểm tra API Key
def check_api_key(files):
    keywords = [
        "api_key=",
        "api_key =",
        "secret_key=",
        "secret_key =",
        "openai_api_key="
    ]

    for file in files:
        if file.endswith(".py"):
            try:
                with open(file, "r", encoding="utf-8") as f:
                    code = f.read().lower()

                for key in keywords:
                    if key in code:
                        return True

            except:
                pass

    return False


# Trang chủ
@app.route("/")
def home():
    return render_template("index.html")


# Upload project
@app.route("/upload", methods=["POST"])
def upload():

    files = request.files.getlist("project")

    folder = "uploads/project"

    # Xóa project cũ
    if os.path.exists(folder):
        shutil.rmtree(folder)

    os.makedirs(folder, exist_ok=True)


    # Lưu file
    for file in files:

        if file.filename == "":
            continue

        # Nếu là ZIP
        if file.filename.lower().endswith(".zip"):

            zip_path = os.path.join(
                "uploads",
                os.path.basename(file.filename)
            )

            file.save(zip_path)

            try:
                with zipfile.ZipFile(zip_path, "r") as zip_file:
                    zip_file.extractall(folder)

            except:
                return "File ZIP không hợp lệ"

        # Nếu là file bình thường
        else:

            file_path = os.path.join(
                folder,
                os.path.basename(file.filename)
            )

            file.save(file_path)


    # Lấy danh sách file trong project
    project_files = []

    for root, dirs, names in os.walk(folder):

        for name in names:

            project_files.append(
                os.path.join(root, name)
            )


    # Phân tích
    framework = check_framework(project_files)

    requirements = check_requirements(project_files)

    env = check_env(project_files)

    api_key = check_api_key(project_files)


    # Gửi kết quả sang result.html
    return render_template(
        "result.html",
        framework=framework,
        requirements=requirements,
        env=env,
        api_key=api_key
    )


# Chạy Flask
if __name__ == "__main__":
    app.run(debug=True)
    