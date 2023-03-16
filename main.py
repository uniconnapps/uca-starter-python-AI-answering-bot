# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
from uniconnapps import connector
import requests
from bs4 import BeautifulSoup
from transformers import pipeline

#START Sample Config - Replace with your own
raise Exception(
    """Could not find a valid config in your app. Please get it from https://platform.uniconnapps.com 
    Replace uca_client with your’s app config then remove the exception."""
    )
uca_client = connector.UcaClient(
  connector_endpoint="uca://xxxxxxx.xxx",
  app_id="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  client_id="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  client_secret="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
  )
#END Sample Config

question_answerer = pipeline("question-answering", model='distilbert-base-cased-distilled-squad')
CONTEXT = ""

@uca_client.action
def learn_from_urls(urls: str) -> dict[str, int]:
    global CONTEXT
    success_count = 0
    failure_count = 0
    for each_url in urls.split("\n"):
        each_url = each_url.strip()
        text = None
        try:
            html = requests.get(each_url, timeout=10).text
            text = BeautifulSoup(html).get_text()
        except Exception:
            pass

        if text:
            CONTEXT = "\n".join([CONTEXT, text])
            success_count += 1
        else:
            failure_count += 1
    return {"Learnned": success_count, "Errors": failure_count}

@uca_client.action
def teach(text: str) -> dict[str, str]:
    global CONTEXT
    text = text.strip()
    if not text:
        return {"Response": "What was that? could not hear anything"}
    if text not in CONTEXT:
        CONTEXT = "\n".join([CONTEXT, text])
        return {"Response": "Copied"}
    else:
        return {"Response": "I already Know it, Please tell me something else"}

@uca_client.action
def ask(question: str) -> dict[str, str]:
    global CONTEXT
    if not CONTEXT:
        return {"Response": "My mind is empty, Please teach me something first."}

    return {"Response": question_answerer(question=question, context=CONTEXT)['answer']}

@uca_client.action
def unlearn() -> dict[str, str]:
    global CONTEXT
    if not CONTEXT:
        return {"Response": "My mind is already empty."}
    CONTEXT = ""
    return {"Response": "Ok, I am forgoting everything."}

if __name__ == '__main__':
    uca_client.run_forever()
