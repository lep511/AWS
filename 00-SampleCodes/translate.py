import argparse # argparse is a built in python package, we add it with an import statement
import boto3

# Define the parser variable to equal argparse.ArgumentParser()
parser = argparse.ArgumentParser(description="Provides translation between one source language and another of the same set of languages.")

# Add each of the arguments using the parser.add_argument() method
parser.add_argument(
    '--text',
    dest="Text",
    type=str,
    help="The text to translate. The text string can be a maximum of 5,000 bytes long. Depending on your character set, this may be fewer than 5,000 characters",
    required=True
    )

parser.add_argument(
    '--source-code', 
    dest="SourceLanguageCode", 
    type=str, 
    help="The language code for the language of the source text. The language must be a language supported by Amazon Translate.",
    required=True
    )

parser.add_argument(
    '--target-code',
    dest="TargetLanguageCode",
    type=str,
    help="The language code requested for the language of the target text. The language must be a language support by Amazon Translate.",
    required=True
    )

# Add our input validation as a function here.
def input_validation(item):
    languages = ["af","sq","am","ar","az","bn","bs","bg","zh","zh-TW","hr","cs","da","fa-AF",
                "nl","en","et","fi","fr","fr-CA","ka","de","el","ha","he","hi","hu","id","it",
                "ja","ko","lv","ms","no","fa","ps","pl","pt","ro","ru","sr","sk","sl","so","es",
                "sw","sv","tl","ta","th","tr","uk","ur","vi"
                ]
    json_input=item
    SourceLanguageCode = json_input['SourceLanguageCode']
    TargetLanguageCode = json_input['TargetLanguageCode']

    if SourceLanguageCode == TargetLanguageCode:
        print("The SourceLanguageCode is the same as the TargetLanguageCode - nothing to do")
        return False
    elif SourceLanguageCode not in languages and TargetLanguageCode not in languages:
        print("Neither the SourceLanguageCode and TargetLanguageCode are valid - stopping")
        return False
    elif SourceLanguageCode not in languages:
        print("The SourceLanguageCode is not valid - stopping")
        return False
    elif TargetLanguageCode not in languages:
        print("The TargetLanguageCode is not valid - stopping")
        return False
    else:
        return True

# This will inspect the command line, convert each argument to the appropriate type and then invoke the appropriate action.
args = parser.parse_args()

def translate_text(**kwargs): 
    
    _args = kwargs
    if input_validation(_args):
        client = boto3.client('translate')
        response = client.translate_text(**kwargs)
        print(response) 

def main():
    # vars() is an inbuilt function which returns a dictionary object
    translate_text(**vars(args))

if __name__=="__main__":
    main()
