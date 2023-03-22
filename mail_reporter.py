import os


def send_report(to, subject, body):
    command = "echo \"{body}\" | mail -s \"{subject}\" -aFrom:\<qa_auto_test@intermedia.net\> {to}".format(to=to, subject=subject, body=body)
    os.system(command)

if __name__ == "__main__":
    send_report(to="dgirdyuk@intermedia.net", subject="test", body="test")