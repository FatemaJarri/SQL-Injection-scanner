import re
import requests
from bs4 import BeautifulSoup

# initialize an HTTP session & set the browser
s = requests.Session()
s.headers['User-Agent'] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)" \
                          " Chrome/103.0.0.0 Safari/537.36"

#A regular expression to constrain the path of the website provided.
regex = "^https?:\\/\\/(?:www\\.)?[-a-zA-Z0-9@:%._\\+~#=]{1,256}\\.[a-zA-Z0-9()]{1,6}" \
        "\\b(?:[-a-zA-Z0-9()@:%_\\+.~#?&\\/=]*)$"

#A function to ask if the user wants to do other scanning.
#If yes, it will take the user to the main menu. If no, exit the program.
def anotherScanning():
    try:
        # This flag is to help exit the while loop at the right time.
        flag = True
        while flag:
            choice = int(input("\nWould you like to do another scanning?\n1- Yes.\n2- No.\nYour choice: "))
            if choice == 1:
                menu()
            elif choice == 2:
                print("((( Thank you for using our system )))")
                flag = False
                exit(1)
            #If the user enters a value other than 1 or 2, ask the user to enter a valid value from the menu.
            else:
                print("~~~ Please enter a valid number from the menu ~~~")
                anotherScanning()
    #An exception to handle user inputs error.
    #It shows a customized error message that only integers are accepted. (User inputs Error handling).
    except ValueError:
        print("~~~ Only integers are accepted. Please enter a valid number from the menu ~~~")
        anotherScanning()
    #A general exception to handle other types of errors.
    except Exception as e:
        print("~~~ An error occurred ~~~ { " + str(e) + " }")

#A function for option 1 in the main menu. It provides a menu with popular websites to scan.
#It also allows the user to exit or go to the previous menu.
def option1():
    try:
        # This flag is to help exit the while loop at the right time.
        flag = True
        while flag:
            website = int(input("\nChoose one popular website of the following: \n1- https://yahoo.com\n"
                                "2- https://bing.com \n3- https://linkedin.com\n4- https://github.com\n"
                                "5- Go back to the previous menu.\n6- Exit.\nYour choice: ").strip())
            if website == 1:
                sql_injection_scan("https://yahoo.com")
            elif website == 2:
                sql_injection_scan("https://bing.com")
            elif website == 3:
                sql_injection_scan("https://www.linkedin.com")
            elif website == 4:
                sql_injection_scan("https://github.com")
            elif website == 5:
                menu()
            elif website == 6:
                print("((( Thank you for using our system )))")
                flag = False
                exit(1)
            #If the user enters a value other than the numbers in the menu,
            # ask the user to enter a valid value from the menu.
            else:
                print("~~~ Please enter a valid number from the menu ~~~")
                option1()
    #An exception to handle user inputs error.
    #It shows a customized error message that only integers are accepted. (User inputs Error handling).
    except ValueError:
        print("~~~ Only integers are accepted. Please enter a valid number from the menu ~~~")
        option1()
    #A general exception to handle other types of errors.
    except Exception as e:
        print("~~~ An error occurred ~~~ { " + str(e) + " }")

#The main menu function. It shows a menu to the user to choose between scanning a famous website,
# scanning a website of the user's choice,or exiting the program.
def menu():
    try:
        #This flag is to help exit the while loop at the right time.
        flag = True
        while flag:
            option = int(
                input("\nChoose one option of the following: \n1- Scan a URL for SQL Injection for a famous website."
                      "\n2- Scan a URL for SQL Injection for a website you provide. \n3- Exit.\nYour choice: ").strip())
            if option == 1:
                option1()
            elif option == 2:
                urlToBeChecked = input("Enter the URL you want to scan: ").strip()
                if re.search(regex, urlToBeChecked):
                    sql_injection_scan(urlToBeChecked)
                else:
                    print("~~~ Sorry, the URL you entered is invalid ~~~")
            elif option == 3:
                print(r'''                                                
                 ▀█▀ █░█ ▄▀█ █▄░█ █▄▀ █▄█ █▀█ █░█ ░ █▄▄ █▄█ █▀▀ ░
                 ░█░ █▀█ █▀█ █░▀█ █░█ ░█░ █▄█ █▄█ █ █▄█ ░█░ ██▄ ▄''')
                flag = False
                exit(1)
            # If the user enters a value other than the numbers in the menu,
            # ask the user to enter a valid value from the menu.
            else:
                print("~~~ Please enter a valid number from the menu ~~~")
                menu()
    # An exception to handle user inputs error.
    # It shows a customized error message that only integers are accepted. (User inputs Error handling).
    except ValueError:
        print("~~~ Only integers are accepted. Please enter a valid number from the menu ~~~")
        menu()
    # A general exception to handle other types of errors.
    except Exception as e:
        print("~~~ An error occurred ~~~ { " + str(e) + " }")


#A function to get all forms OR extract web forms
#We used BeautifulSoup library to extract all form tags
# out of HTML files and return them as a python list.
def get_forms(url):
    soup = BeautifulSoup(s.get(url).content, "html.parser")
    return soup.find_all("form")

#A function gets a single form tag object as an argument,
# then parses useful information about the form into a dictionary.
def form_details(form):
    detailsOfForm = {}

    #### get the form action (target url) ####
    #
    try:
        action = form.attrs.get("action")#.lower()
    except:
        action = None
    method = form.attrs.get("method", "get")#.lower()

    #Get all the input details such as type and name.
    inputs = []
    #### Iterate over inputs in a form. ####
    for input_tag in form.find_all("input"):
        #These are HTML tags.
        input_type = input_tag.attrs.get("type", "text")
        input_name = input_tag.attrs.get("name")
        #The value is empty at the beginning, so, we put empty quotations.
        input_value = input_tag.attrs.get("value", "")
        #Add all the details to the list we created earlier.
        inputs.append({
            "type": input_type,
            "name": input_name,
            "value": input_value,
        })

    #Add all information in the results dictionary created earlier.
    detailsOfForm['action'] = action
    detailsOfForm['method'] = method
    detailsOfForm['inputs'] = inputs
    return detailsOfForm

# Boolean function to determine whether a page is SQL Injection vulnerable to its `response
def vulnerable(response):
    #A set of errors
    errors = {"quoted string not properly terminated",
              "unclosed quotation mark after the character string",
              "you have an error in you SQL syntax"
              }

    for error in errors:
        # If you find one of these errors, return True
        if error in response.content.decode().lower():
            return True
    #No error?
    return False



#The main function that searches for all forms in the web page
# and tries to place quote and double quote characters in input fields:
def sql_injection_scan(url):

    ## test on HTML forms
    #Create forms from a url.
    forms = get_forms(url)
    print(f"[+] Detected {len(forms)} forms on {url}.")
    for form in forms:
            details = form_details(form)

            # Iterate over these characters ('") that may be maliciously entered as input.
            # If there is a response, it means there is a vulnerability.
            for i in "\"'":
                   # The data body we want to submit.
                    data = {}
                    for input_tag in details["inputs"]:
                        if input_tag["type"] == "hidden" or input_tag["value"]:
                            # any input form that is hidden or has some value,just use it in the form body.
                            try:
                                data[input_tag['name']] = input_tag["value"] + i
                            except Exception as e:
                                print(e)
                        elif input_tag["type"] != "submit":
                            data[input_tag['name']] = f"test{i}"
                    print(url)
                    form_details(form)
                    try:
                        global res
                        #Check, if the method is post, we will assign the url to the response.
                        if details["method"] == "post":
                            res = s.post(url, data=data)
                        #Else, we will get the url
                        elif details["method"] == "get":
                           res = s.get(url, params=data)
                        #Test whether the resulting page is vulnerable.
                        if vulnerable(res):
                            print("SQL injection attack vulnerability in link: ", url )
                        else:
                            print("No SQL injection attack vulnerability detected")
                    except Exception as e:
                        print("~~~ An error occurred ~~~ { " + str(e) + " }")
                    break

    #Calling the function to ask if the user wants to perform another scanning.
    # If yes, it will return to the main menu. If not, exit the program.
    anotherScanning()



if __name__ == "__main__":
    art3='''

                ▒█▀▀█ █▀▀█ █▀▀▄ █▀▀ ▒█░░▒█ █▀▀█ █▀▀█ █▀▀ 
                ▒█░░░ █░░█ █░░█ █▀▀ ▒█▒█▒█ █▄▄█ █▄▄▀ ▀▀█ 
                ▒█▄▄█ ▀▀▀▀ ▀▀▀░ ▀▀▀ ▒█▄▀▄█ ▀░░▀ ▀░▀▀ ▀▀▀
    '''
    print(art3)
    print("Done BY:\n[1]Sarah AL abbas\n[2]Fatema al jarri \n[3]Shouq al hammam\n[4]Layal Abualsaud \n[5]Bushra aleid \n\n")
    menu()