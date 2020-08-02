import boto3


def aadhar():
    # Document
    documentName = r'./aadhar/1.jpg'

    # Read document content
    with open(documentName, 'rb') as document:
        imageBytes = bytearray(document.read())

    #boto3.session.Session(aws_access_key_id='', aws_secret_access_key= '',region_name='')

    # Amazon Textract client
    textract = boto3.client('textract')

    # Call Amazon Textract
    response = textract.detect_document_text(Document={'Bytes': imageBytes})

    #print(response)

    def verify_aadhar(string):
        for index in range(len(string)):
            if index==4 or index==9:
                continue
            if not string[index].isnumeric():
                return False
        return True
    # Print detected text
    for item in response["Blocks"]:
        if item["BlockType"] == "LINE":
            if len(item["Text"])==14 and verify_aadhar(item["Text"]):
                aadhar_number = item["Text"][:4] + item["Text"][5:9] + item["Text"][10:]
    #           print ('\033[94m' , int(aadhar_number) , '\033[0m')
                aadhar = int(aadhar_number)
                return aadhar


if __name__ == '__main__':
    aadhar()