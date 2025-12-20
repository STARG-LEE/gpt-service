# Hugging Face Spaces 배포용 메인 파일
# gradio_app.py를 import하여 사용

from gradio_app import demo

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, share=False)
