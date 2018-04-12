from tesserocr import PyTessBaseAPI, RIL
from PIL import Image
import os
import cv2
from google import google
from googleapiclient.discovery import build
import pprint

service = build('customsearch', 'v1',
                developerKey='AIzaSyCk2qQxy6WjenVgOeBiS2M52uRXlWgETaE')

res = service.cse().list(
    q='lectures',
    cx='017576662512468239146:omuauf_lfve',
).execute()
pprint.pprint(res)


def search(query, num_page: 1):
    print("Sending request with query: \n{}".format(query))
    search_results = google.search(query, num_page)
    print("Found {} results".format(len(search_results)))
    return search_results


class Question:
    all = []

    def __init__(self, question="", alternatives=[]):
        self.q = question
        self.ans = alternatives
        Question.all.append(self)

    def predict(self, option=1):
        results = []
        if option == 1:
            for i in range(len(self.ans)):
                query = "{} {}".format(self.q, self.ans[i])
                response = search(query, 1)
                results.append([query, response])
        elif option == 2:
            print("implementation pending for option 2")
        elif option == 3:
            print("implementation pending for option 3")
        else:
            print("invalid option")
        return results


img_count = 1

images = ["sample{}.png".format(i + 1) for i in range(img_count)]

with PyTessBaseAPI() as api:
    for img in images:
        print("====== Reading Image '{}' ======\n".format(img))
        image = cv2.imread("samples/{}".format(img))
        cv2.imshow("img", image)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.threshold(
            gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        # gray = cv2.medianBlur(gray, 3)
        filename = "processed/{}".format(img)
        cv2.imwrite(filename, gray)
        image = Image.open(filename)
        api.SetImage(image)
        boxes = api.GetComponentImages(RIL.TEXTLINE, True)
        if len(boxes) < 4:
            print("Error processing the image")
            break
        else:
            lines = len(boxes)
            questionRange = [i for i in range(0, lines - 3)]
            alternativesRange = [i for i in range(lines - 3, lines)]
        question = Question()
        for i, (im, box, _, _) in enumerate(boxes):
            api.SetRectangle(box['x'], box['y'], box['w'], box['h'])
            ocrResult = api.GetUTF8Text()
            conf = api.MeanTextConf()
            if i in questionRange:
                parsedQuestion = ocrResult.replace(
                    "\n", " ").replace("\t", " ")
                # print("\t> Pregunta:")
                # print("\t {}".format(parsedQuestion))
                # print("\t  ---------------")
                question.q += parsedQuestion
            elif i in alternativesRange:
                parsedAlternative = ocrResult.replace("\n", " ").strip()
                # print("\t> Alternativa {}:".format(i))
                # print("\t  {}".format(parsedAlternative))
                question.ans.append(parsedAlternative)

question = Question.all[0]
print("QUESTION: {}".format(question.q))
print("ANSWERS: {}".format(question.ans))
googleResults = question.predict()
for result in googleResults:
    request = result[0]
    response = result[1][0]
    print("Result for '{}':\nNAME: {}\nDESCRIPTION: {}\n".format(
        request, response.name, response.description))
