import smtplib
import ssl


def sendMail(n, results):
    """ Send a mail containing the results to a mail address contained in "mailinfo:3", using gmail address
    "mailinfo:1" and password "mailinfo:2".

    :param n: Number of batches used in the run
    :type n: int
    :param results: Message to transfer
    :type results: str
    :rtype: None
    """
    server = None
    f = open("mailinfo", 'r')
    sender_email = f.readline()[:-1]
    password = f.readline()
    receiver_email = f.readline()
    smtp_server = "smtp.gmail.com"
    port = 587  #
    context = ssl.create_default_context()
    try:
        server = smtplib.SMTP(smtp_server, port)
        server.ehlo()
        server.starttls(context=context)
        server.ehlo()
        server.login(sender_email, password)
        message = """From: M2RECH_RAIMONDI <""" + sender_email + """>
To: ??? <""" + receiver_email + """>
Subject: Taxonomy of modules

Your run is terminated, please check the results below of your """ + str(n) + " batch" + 'es' * (n != '1') + ".\n"
        message = message + results
        server.sendmail(sender_email, receiver_email, message)
    except Exception as e:
        print(e)
    finally:
        if server:
            server.quit()
