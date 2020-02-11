def name_splitter(fullname):
    names = fullname.split(" ")
    if len(names) > 1:
        fname = names[0]
        lname = names[1]
    else:
        fname = names[0]
        lname = ""
    return fname, lname


def name_from_email(email):
    mailname = email.split("@")[0]
    return name_splitter(mailname.replace(".", " "))
