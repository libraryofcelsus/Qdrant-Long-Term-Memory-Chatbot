# Basic-Long-Term-Memory-Chatbot
Example code for a basic Long Term Memory Chatbot.  It uses a conversation history list and a vector database.

If you find this code useful, consider checking out my main Ai Assistant project: https://github.com/libraryofcelsus/Aetherius_AI_Assistant

If you want more code tutorials like this, follow me on github and youtube: https://www.youtube.com/@LibraryofCelsus

(Channel isn't launched yet, I have multiple scripts like this written, but am still working on a video production format. Subscribe for its Launch!)

In-Depth Code Tutorials in a documentation format available at: https://www.libraryofcelsus.com/research/public/code-tutorials/

## Window's Installation
1. If using Qdrant Cloud copy their Api key and Url to the corresponding .txt files.  
Qdrant Cloud Link: https://qdrant.to/cloud  
To use a local Qdrant server, first install Docker: https://www.docker.com/, then see: https://github.com/qdrant/qdrant/blob/master/QUICK_START.md  
Once the local Qdrant server is running, it should be auto detected by the script.
1. Install Git
2. Install Python 3.10.6, Make sure you add it to PATH
3. Open Git Bash Program
4. Run git clone: **git clone https://github.com/libraryofcelsus/Basic-Long-Term-Memory-Chatbot.git**
5. Open the Command Line as admin and navigate to the project install folder with **cd <PATH TO INSTALL>**
6. Create a virtual environment: python -m venv venv
7. Activate the virtual enviornment with: .\venv\Scripts\activate
8. Install the requirements with **pip install -r requirements.txt**
9. Edit and set your username and chatbot name in the .txt files
10. Edit and set your main prompt and greeting in the .txt files
11. **For Oobabooga:** Install the Oobabooga Web-Ui.  This can be done with a one-click installer found on their Github page: https://github.com/oobabooga/text-generation-webui.
Then launch the Web-Ui and navigate to the sessions tab, click both Api boxes and then click apply and restart.
Now navigate to the models tab and enter: "TheBloke/Llama-2-7b-Chat-GPTQ" or "TheBloke/Llama-2-13B-chat-GPTQ".  (If using cpu use the GMML Version)
Once the model is downloaded, change the Model loader to ExLlama and set the gpu-split parameter to .5gb under your GPU's limit.  Next set the max_seq_len to 4096.
13. **For OpenAI:** Add your OpenAi Api Key to **key_openai.txt**
15. Run the chatbot with **python Script_Name.py**
 
*Note, you will need to run .\venv\Scripts\activate every time you exit the command line to reactivate the virtual enviornment.

-----

My Ai research is self-funded, consider supporting me if you find it useful :)

<a href='https://ko-fi.com/libraryofcelsus' target='_blank'><img height='36' style='border:0px;height:36px;' src='https://storage.ko-fi.com/cdn/kofi3.png?v=3' border='0' alt='Buy Me a Coffee at ko-fi.com' /></a>

-----

# Contact
Discord: libraryofcelsus      -> Old Username Style: Celsus#0262

MEGA Chat: https://mega.nz/C!pmNmEIZQ

Email: libraryofcelsusofficial@gmail.com
