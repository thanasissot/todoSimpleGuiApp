from pymongo import MongoClient, collection
import PySimpleGUI as sg
import sys

# connect to MongoD
client = MongoClient('mongodb://localhost:27017/')
# connect to specific database
db = client.todo
# user collection
userCollection = db.user
# todo collection
todoCollection = db.todo


def create_todo_layout(lst):
    res = [[sg.Image("rsz_close_img.png", k=("delete", x), enable_events=True, size=(14, 14)), sg.Text(x), sg.Text(y)]
           for x, y in enumerate(todos, start=1)]
    res.append([sg.Button("Add :"), sg.InputText(size=(25, 1))])
    res.append([sg.Button("Sign Out", size=(29, 1))])
    return res


def create_main_window_layout():
    return [[sg.Text("Main Menu", pad=(85, 0))],
            [sg.InputText("Username", size=(33, 1))],
            [sg.InputText("Password", size=(33, 1))],
            [sg.Button("Login", size=(29, 1))],
            [sg.Button("Sign Up", size=(29, 1))],
            [sg.Exit(size=(29, 1))]
            ]


def create_sign_window_layout():
    return [
        [sg.Text("Username:")], [sg.InputText(size=(33, 1), k="sign_username")],
        [sg.Text("Password:")], [sg.InputText(size=(33, 1), k="sign_password")],
        [sg.Button("OK", size=(29, 1))], [sg.Button("Cancel", size=(29, 1))]
    ]


window = sg.Window("TodoApp", create_main_window_layout())
logged_user = None

while True:
    event, values = window.read()

    if event == "Login":
        # if username not in database/memory
        logged_user = userCollection.find_one({'username': values[0]})
        if logged_user == None:
            sg.Popup("Username not found!")
        else:
            # if password is wrong
            if logged_user['password'] != values[1]:
                sg.Popup("Password is wrong. Try again!")
            else:
                # finds todos of user and adds them to new laytout creation
                todos = list(x["item"] for x in todoCollection.find({'username': logged_user["_id"]}))
                window.close()
                window = sg.Window("TodoApp", create_todo_layout(todos))

    elif event == "Sign Up":
        sign_window = sg.Window("SignUp", create_sign_window_layout())
        while True:
            event, values = sign_window.read()
            if event == "OK":
                # check if username already exists in database
                if userCollection.find_one({'username': values["sign_username"]}) is not None:
                    sg.Popup("Username already Exists!")
                else:
                    if len(values["sign_username"]) > 0 and len(values["sign_password"]) > 0:
                        # check if not null username and password, bad check, only temporary
                        # create user
                        userCollection.insert_one(
                            {'username': values["sign_username"], 'password': values["sign_password"]})
                        sign_window.close()
                    else:
                        sg.Popup("Username and password must not be empty!")
            # cancel signup, close sign up window
            if event == "Cancel":
                sign_window.close()
            # after successfully creating a user, you need this to stop the while loop continuously checking events
            # as to keep the app running smoothly
            if event == sg.WIN_CLOSED:
                break

    elif event == "Add :":
        # insert a todo in the db, associate it with current logged user
        todoCollection.insert_one({'username': logged_user["_id"], 'item': values[0]})
        todos = list(x["item"] for x in todoCollection.find({'username': logged_user["_id"]}))
        window.close()
        window = sg.Window("TodoApp", create_todo_layout(todos))

    elif event[0] == "delete":
        todos = list(todoCollection.find({"username" : logged_user["_id"]}))
        toDeleteId = todos[event[1] - 1]["_id"]
        todoCollection.delete_one({"_id" : toDeleteId})
        todos = list(x["item"] for x in todoCollection.find({'username': logged_user["_id"]}))
        window.close()
        window = sg.Window("TodoApp", create_todo_layout(todos))

    elif event == "Sign Out":
        logged_user = None
        window.close()
        window = sg.Window("TodoApp", create_main_window_layout())

    elif event in (sg.WIN_CLOSED, "Exit"):
        break

window.close()