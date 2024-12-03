This is MacOS setup

1. conda create --name web1 python=3.10
2. pip3 install -r requirements.txt
3. create .env file with openai api key
4. streamlit run nv_chat_app.py

Installed poetry & pyenv using 
$ pipz install poetry 
$ brew install pyenv 

Virtual env poetry + pyenv (for specific python env) follow the following command 
1. poetry new my-project
$  cd my-project
2. pyenv install 3.10
3. pyenv local 3.10
4. pyenv which python
5. poetry env use <prenv_which_python_PATH>
6. poetry shell
7. streamlit run nv_chat_app.py

  
